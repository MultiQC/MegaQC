# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, request, jsonify, abort

from megaqc.extensions import db
from megaqc.user.models import User
from megaqc.model.models import PlotData, Report, SampleFilter
from megaqc.api.utils import handle_report_data, generate_plot, get_samples, get_report_metadata_fields, \
                            get_sample_metadata_fields, aggregate_new_parameters, get_user_filters, update_fav_plot, \
                            get_sample_fields_values, update_user_filter
from megaqc.user.forms import AdminForm

from sqlalchemy.sql import func, distinct

from functools import  wraps

import json

api_blueprint = Blueprint('api', __name__, static_folder='../static')


# decorator to handle api authentication
def check_user(function):
    @wraps(function)
    def user_wrap_function(*args, **kwargs):
        user = User.query.filter_by(api_token=request.headers.get("access_token")).first()
        if not user:
            abort(403) # if no user, abort the request with 403
        kwargs['user'] = user
        return function(*args, **kwargs) # else add "user" to kwargs so it can be used in the request handling
    return user_wrap_function

def check_admin(function):
    @wraps(function)
    def user_wrap_function(*args, **kwargs):
        user = User.query.filter_by(api_token=request.headers.get("access_token")).first()
        if not user or not user.is_admin:
            abort(403) # if no user, abort the request with 403
        kwargs['user'] = user
        return function(*args, **kwargs) #else add "user" to kwargs so it can be used in the request handling
    return user_wrap_function


@api_blueprint.route('/api/test', methods=['GET'])
@check_user
def test(user, *args, **kwargs):
    return jsonify({
        'success': True,
        'name': user.username,
        'message': 'Test API call successful'
    })

@api_blueprint.route('/api/test_post', methods=['POST'])
@check_user
def test_post(user, *args, **kwargs):
    data = request.get_json()
    data['name'] = user.username


@api_blueprint.route('/api/upload_data', methods=['POST'])
@check_user
def handle_multiqc_data(user, *args, **kwargs):
    data = request.get_json().get('data')
    success, msg = handle_report_data(user, data)
    response = jsonify({
        'success': success,
        'message': msg
    })
    if not success:
        response.status_code = 400
    return response


@api_blueprint.route('/api/update_users', methods=['POST'])
@check_admin
def admin_update_users(user, *args, **kwargs):
    data = request.get_json()
    try:
        user_id = int(data['user_id'])
        data['user_id'] = user_id
    except:
        abort(400)
    cured_data = {key:(data[key] if data[key] != "None" else None) for key in data}
    form = AdminForm(**cured_data)
    if not form.validate():
        response = jsonify({
            'success': False,
            'message': ' '.join(' '.join(errs) for errs in form.errors.values())
        })
        response.status_code = 400
        return response
    else:
        db.session.query(User).filter(User.user_id==user_id).first().update(**cured_data)
        return jsonify({'success': True})

@api_blueprint.route('/api/delete_users', methods=['POST'])
@check_admin
def admin_delete_users(user, *args, **kwargs):
    data = request.get_json()
    try:
        user_id = int(data['user_id'])
    except:
        abort(400)
    db.session.query(User).filter(User.user_id==user_id).first().delete()
    return jsonify({'success': True})

@api_blueprint.route('/api/reset_password', methods=['POST'])
@check_user
def reset_password(user, *args, **kwargs):
    data = request.get_json()
    if user.is_admin or data['user_id'] == user.user_id:
        new_password= user.reset_password()
        user.save()
    else:
        abort(403)
    return jsonify({'success': True, 'password': new_password})

@api_blueprint.route('/api/set_password', methods=['POST'])
@check_user
def set_password(user, *args, **kwargs):
    data = request.get_json()
    user.set_password(data['password'])
    user.save()
    return jsonify({'success': True})

@api_blueprint.route('/api/add_user', methods=['POST'])
@check_admin
def admin_add_users(user, *args, **kwargs):
    data = request.get_json()
    try:
        data['user_id'] = int(data['user_id'])
    except:
        abort(400)
    new_user= User(**data)
    password = new_user.reset_password()
    new_user.active= True
    new_user.save()
    return jsonify({
        'success': True,
        'password': password,
        'api_token': user.api_token
    })

@api_blueprint.route('/api/get_samples_per_report', methods=['POST'])
@check_user
def get_samples_per_report(user, *args, **kwargs):
    data = request.get_json()
    report_id = data.get("report_id")
    sample_names = {x[0]:x[1] for x in db.session.query(distinct(PlotData.sample_name), Report.title).join(Report).filter(PlotData.report_id ==  report_id).all()}
    return jsonify(sample_names)

@api_blueprint.route('/api/get_plot', methods=['POST'])
@check_user
def get_plot(user, *args, **kwargs):
    data = request.get_json()
    plot_type = data.get("plot_type")
    filters = data.get("filters", [])
    sample_names = get_samples(filters)
    html = generate_plot(plot_type, sample_names)
    return jsonify({
        'success': True,
        'plot': html
    })

@api_blueprint.route('/api/count_samples', methods=['POST'])
@check_user
def count_samples(user, *args, **kwargs):
    data = request.get_json()
    filters = data.get("filters", [])
    count = get_samples(filters, count=True)
    return jsonify({
        'success': True,
        'count': count
    })

@api_blueprint.route('/api/report_filter_fields', methods=['GET', 'POST'])
@check_user
def report_filter_fields(user, *args, **kwargs):
    data = request.get_json()
    filter_id = int(data.get("filters_id", 0))
    if filter_id:
        # Hardcoded "All Samples" filter set
        if filter_id == -1:
            filters = []
        else:
            my_filter = db.session.query(SampleFilter).filter(SampleFilter.sample_filter_id == filter_id).first()
            filters = json.loads(my_filter.sample_filter_data)
    else:
        filters = data.get("filters", [])
    return_data = aggregate_new_parameters(user, filters, True)
    return jsonify({
        'success': True,
        'num_samples': return_data[0],
        'report_plot_types': return_data[1]
    })

@api_blueprint.route('/api/save_filters', methods=['POST'])
@check_user
def save_filters(user, *args, **kwargs):
    data = request.get_json()
    one_filter = data.get("filters", [])
    meta = data.get("meta", {})
    data = json.dumps(one_filter)
    if one_filter and meta:
        new_sf_id = SampleFilter.get_next_id()
        new_sf = SampleFilter(
                sample_filter_id = new_sf_id,
                sample_filter_name = meta.get('name'),
                sample_filter_tag = meta.get('set'),
                is_public = meta.get('is_public', False),
                sample_filter_data = data,
                user_id = user.user_id
            )
        new_sf.save()
        return jsonify({
                'success': True,
                'message': "Filters created successfully",
                'filter_id': new_sf_id
            })
    else:
        return jsonify({
                'success': False,
                'message': "Filters or metadata were empty"
            })



@api_blueprint.route('/api/get_filters', methods=['GET', 'POST'])
@check_user
def get_filters(user, *args, **kwargs):
    data = get_user_filters(user)
    return jsonify({
            'success': True,
            'data': data
            })


@api_blueprint.route('/api/update_favourite_plot', methods=['GET', 'POST'])
@check_user
def update_favourite_plot(user, *args, **kwargs):
    data = request.get_json()
    plot_info = data.get("plot_id","").split(" -- ")
    method = data.get('method', None)
    if plot_info and method:
        try:
            update_fav_plot(method, user, plot_info)
        except Exception as e:
            return jsonify({
                'success':False,
                'message':e.message
            })
    return jsonify({
        'success': True
    })
@api_blueprint.route('/api/get_sample_data', methods=['POST'])
@check_user
def get_sample_data(user, *args, **kwargs):
    data = request.get_json()
    my_filters = data.get("filters", [])
    data_keys = data.get("fields", {})
    ret_data = get_sample_fields_values(data_keys, my_filters)
    return jsonify(ret_data)

@api_blueprint.route('/api/update_filters', methods=['POST'])
@check_user
def update_filters(user, *args, **kwargs):
    data = request.get_json()
    method = data.get("method")
    filter_id = float(data.get("filter_id"))
    filter_object = data.get("filters", {})
    update_user_filter(user, method, filter_id, filter_object)
    return jsonify({
            'success': True
            })
