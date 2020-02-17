# -*- coding: utf-8 -*-
"""
Public section, including homepage and signup.
"""
import json
from functools import wraps

from flask import Blueprint, abort, jsonify, request
from megaqc.api.utils import (
    aggregate_new_parameters,
    delete_report_data,
    generate_comparison_plot,
    generate_distribution_plot,
    generate_report_plot,
    generate_trend_plot,
    get_dashboard_data,
    get_favourite_plot_data,
    get_filter_from_data,
    get_queued_uploads,
    get_report_metadata_fields,
    get_reports_data,
    get_sample_fields_values,
    get_sample_metadata_fields,
    get_samples,
    get_timeline_sample_data,
    get_user_filters,
    handle_report_data,
    save_dashboard_data,
    save_plot_favourite_data,
    store_report_data,
    update_fav_report_plot_type,
    update_user_filter,
)
from megaqc.extensions import db
from megaqc.model.models import Dashboard, PlotData, PlotFavourite, Report, SampleFilter
from megaqc.user.forms import AdminForm
from megaqc.user.models import User
from sqlalchemy.sql import distinct, func

api_blueprint = Blueprint("api", __name__, static_folder="../static")


# decorator to handle api authentication
def check_user(function):
    @wraps(function)
    def user_wrap_function(*args, **kwargs):
        user = User.query.filter_by(
            api_token=request.headers.get("access_token")
        ).first()
        if not user:
            abort(403)  # if no user, abort the request with 403
        kwargs["user"] = user
        return function(
            *args, **kwargs
        )  # else add "user" to kwargs so it can be used in the request handling

    return user_wrap_function


def check_admin(function):
    @wraps(function)
    def user_wrap_function(*args, **kwargs):
        user = User.query.filter_by(
            api_token=request.headers.get("access_token")
        ).first()
        if not user or not user.is_admin:
            abort(403)  # if no user, abort the request with 403
        kwargs["user"] = user
        return function(
            *args, **kwargs
        )  # else add "user" to kwargs so it can be used in the request handling

    return user_wrap_function


@api_blueprint.route("/api/test", methods=["GET"])
@check_user
def test(user, *args, **kwargs):
    return jsonify(
        {"success": True, "name": user.username, "message": "Test API call successful"}
    )


@api_blueprint.route("/api/test_post", methods=["POST"])
@check_user
def test_post(user, *args, **kwargs):
    data = request.get_json()
    data["name"] = user.username


@api_blueprint.route("/api/upload_data", methods=["POST"])
@check_user
def queue_multiqc_data(user, *args, **kwargs):
    data = request.data
    try:
        uploaded_file = request.files["file"]
    except:
        uploaded_file = None
    success, msg = store_report_data(user, data, uploaded_file)
    response = jsonify({"success": success, "message": msg})
    if not success:
        response.status_code = 400
    return response


@api_blueprint.route("/api/upload_parse", methods=["POST"])
@check_user
def handle_multiqc_data(user, *args, **kwargs):
    data = request.get_json().get("data")
    success, msg = handle_report_data(user, data)
    response = jsonify({"success": success, "message": msg})
    if not success:
        response.status_code = 400
    return response


@api_blueprint.route("/api/update_users", methods=["POST"])
@check_admin
def admin_update_users(user, *args, **kwargs):
    data = request.get_json()
    try:
        user_id = int(data["user_id"])
        data["user_id"] = user_id
    except:
        abort(400)
    cured_data = {key: (data[key] if data[key] != "None" else None) for key in data}
    form = AdminForm(**cured_data)
    if not form.validate():
        response = jsonify(
            {
                "success": False,
                "message": " ".join(
                    " ".join(errs) for errs in list(form.errors.values())
                ),
            }
        )
        response.status_code = 400
        return response
    else:
        db.session.query(User).filter(User.user_id == user_id).first().update(
            **cured_data
        )
        return jsonify({"success": True})


@api_blueprint.route("/api/delete_users", methods=["POST"])
@check_admin
def admin_delete_users(user, *args, **kwargs):
    data = request.get_json()
    try:
        user_id = int(data["user_id"])
    except:
        abort(400)
    db.session.query(User).filter(User.user_id == user_id).first().delete()
    return jsonify({"success": True})


@api_blueprint.route("/api/reset_password", methods=["POST"])
@check_user
def reset_password(user, *args, **kwargs):
    data = request.get_json()
    if user.is_admin or data["user_id"] == user.user_id:
        new_password = user.reset_password()
        user.save()
    else:
        abort(403)
    return jsonify({"success": True, "password": new_password})


@api_blueprint.route("/api/set_password", methods=["POST"])
@check_user
def set_password(user, *args, **kwargs):
    data = request.get_json()
    user.set_password(data["password"])
    user.save()
    return jsonify({"success": True})


@api_blueprint.route("/api/add_user", methods=["POST"])
@check_admin
def admin_add_users(user, *args, **kwargs):
    data = request.get_json()
    try:
        data["user_id"] = int(data["user_id"])
    except:
        abort(400)
    new_user = User(**data)
    password = new_user.reset_password()
    new_user.active = True
    new_user.save()
    return jsonify({"success": True, "password": password, "api_token": user.api_token})


@api_blueprint.route("/api/get_samples_per_report", methods=["POST"])
@check_user
def get_samples_per_report(user, *args, **kwargs):
    data = request.get_json()
    report_id = data.get("report_id")
    sample_names = {
        x[0]: x[1]
        for x in db.session.query(distinct(PlotData.sample_name), Report.title)
        .join(Report)
        .filter(PlotData.report_id == report_id)
        .all()
    }
    return jsonify(sample_names)


@api_blueprint.route("/api/get_report_plot", methods=["POST"])
@check_user
def get_report_plot(user, *args, **kwargs):
    data = request.get_json()
    plot_type = data.get("plot_type")
    filters = data.get("filters", [])
    sample_names = get_samples(filters)
    html = generate_report_plot(plot_type, sample_names)
    return jsonify({"success": True, "plot": html})


@api_blueprint.route("/api/count_samples", methods=["POST"])
@check_user
def count_samples(user, *args, **kwargs):
    data = request.get_json()
    filters = data.get("filters", [])
    count = get_samples(filters, count=True)
    return jsonify({"success": True, "count": count})


@api_blueprint.route("/api/report_filter_fields", methods=["GET", "POST"])
@check_user
def report_filter_fields(user, *args, **kwargs):
    data = request.get_json()
    filters = get_filter_from_data(data)
    return_data = aggregate_new_parameters(user, filters, True)
    return jsonify(
        {
            "success": True,
            "num_samples": return_data[0],
            "report_plot_types": return_data[1],
        }
    )


@api_blueprint.route("/api/get_sample_meta_fields", methods=["GET", "POST"])
@check_user
def get_sample_meta_fields(user, *args, **kwargs):
    data = request.get_json()
    filters = get_filter_from_data(data)
    return_data = aggregate_new_parameters(user, filters, False)
    return jsonify(
        {
            "success": True,
            "num_samples": return_data[0],
            "sample_meta_fields": return_data[2],
        }
    )


@api_blueprint.route("/api/save_filters", methods=["POST"])
@check_user
def save_filters(user, *args, **kwargs):
    data = request.get_json()
    one_filter = data.get("filters", [])
    meta = data.get("meta", {})
    data = json.dumps(one_filter)
    if one_filter and meta:
        new_sf = SampleFilter(
            sample_filter_name=meta.get("name"),
            sample_filter_tag=meta.get("set"),
            is_public=meta.get("is_public", False),
            sample_filter_data=data,
            user_id=user.user_id,
        )
        new_sf.save()
        return jsonify(
            {
                "success": True,
                "message": "Filters created successfully",
                "filter_id": new_sf.sample_filter_id,
            }
        )
    else:
        return jsonify({"success": False, "message": "Filters or metadata were empty"})


@api_blueprint.route("/api/get_filters", methods=["GET", "POST"])
@check_user
def get_filters(user, *args, **kwargs):
    data = get_user_filters(user)
    return jsonify({"success": True, "data": data})


@api_blueprint.route("/api/update_favourite_plot", methods=["GET", "POST"])
@check_user
def update_favourite_plot(user, *args, **kwargs):
    data = request.get_json()
    plot_info = data.get("plot_id", "").split(" -- ")
    method = data.get("method", None)
    if plot_info and method:
        try:
            update_fav_report_plot_type(method, user, plot_info)
        except Exception as e:
            return jsonify({"success": False, "message": e.message})
    return jsonify({"success": True})


@api_blueprint.route("/api/get_sample_data", methods=["POST"])
@check_user
def get_sample_data(user, *args, **kwargs):
    data = request.get_json()
    my_filters = get_filter_from_data(data)
    data_keys = data.get("fields", {})
    ret_data = get_sample_fields_values(data_keys, my_filters)
    return jsonify(ret_data)


@api_blueprint.route("/api/get_distribution_plot", methods=["POST"])
@check_user
def get_distribution_plot(user, *args, **kwargs):
    data = request.get_json()
    my_filters = get_filter_from_data(data)
    data_keys = data.get("fields", {})
    nbins = data.get("nbins", 20)
    ptype = data.get("ptype", 20)
    plot_data = get_sample_fields_values(data_keys, my_filters)
    html = generate_distribution_plot(plot_data, nbins, ptype)
    return jsonify({"success": True, "plot": html})


@api_blueprint.route("/api/get_trend_plot", methods=["POST"])
@check_user
def get_trend_plot(user, *args, **kwargs):
    data = request.get_json()
    my_filters = get_filter_from_data(data)
    data_keys = data.get("fields", {})
    plot_data = get_timeline_sample_data(my_filters, data_keys)
    html = generate_trend_plot(plot_data)
    return jsonify({"success": True, "plot": html})


@api_blueprint.route("/api/get_comparison_plot", methods=["POST"])
@check_user
def get_comparison_plot(user, *args, **kwargs):
    data = request.get_json()
    my_filters = get_filter_from_data(data)
    data_keys = data.get("fields", {})
    field_names = data.get("field_names", {})
    pointsize = data.get("pointsize", 10)
    joinmarkers = data.get("joinmarkers", False)
    plot_data = get_sample_fields_values(
        data_keys.values(), my_filters, num_fieldids=True
    )
    html = generate_comparison_plot(
        plot_data, data_keys, field_names, pointsize, joinmarkers
    )
    return jsonify({"success": True, "plot": html})


@api_blueprint.route("/api/update_filters", methods=["POST"])
@check_user
def update_filters(user, *args, **kwargs):
    data = request.get_json()
    method = data.get("method")
    filter_id = float(data.get("filter_id"))
    filter_object = data.get("filters", {})
    update_user_filter(user, method, filter_id, filter_object)
    return jsonify({"success": True})


@api_blueprint.route("/api/get_timeline_sample_data", methods=["POST"])
@check_user
def timeline_sample_data(user, *args, **kwargs):
    data = request.get_json()
    my_filters = get_filter_from_data(data)
    data_keys = data.get("fields", {})
    ret_data = get_timeline_sample_data(my_filters, data_keys)
    return jsonify(ret_data)


@api_blueprint.route("/api/get_reports", methods=["GET", "POST"])
@check_user
def get_reports(user, *args, **kwargs):
    count = False
    filtering = None
    if request.method == "POST":
        data = request.get_json()
        filtering = (data.get("key"), data.get("value"))
        if filtering[1] == "":
            filtering = None
    else:
        filtering = None
    if not user.is_admin:
        user_id = user.user_id
    else:
        user_id = None
    ret_data = get_reports_data(count=count, user_id=user_id, filters=filtering)
    return jsonify(ret_data)


@api_blueprint.route("/api/delete_report", methods=["POST"])
@check_user
def delete_report(user, *args, **kwargs):
    data = request.get_json()
    delete_report_data(data.get("report_id", -1))
    return jsonify({"success": True})


@api_blueprint.route("/api/get_favourite_plot", methods=["POST"])
@check_user
def get_favourite_plot(user, *args, **kwargs):
    data = request.get_json()
    favourite_id = data.get("favourite_id")
    plot_results = get_favourite_plot_data(user, favourite_id)
    plot_results["success"] = True
    return jsonify(plot_results)


@api_blueprint.route("/api/save_plot_favourite", methods=["POST"])
@check_user
def save_plot_favourite(user, *args, **kwargs):
    data = request.get_json()
    type = data.get("type")
    request_data = data.get("request_data")
    title = data.get("title")
    description = data.get("description")
    pf_id = save_plot_favourite_data(user, type, request_data, title, description)
    return jsonify({"favourite_id": pf_id, "success": True})


@api_blueprint.route("/api/delete_plot_favourite", methods=["POST"])
@check_user
def delete_plot_favourite(user, *args, **kwargs):
    data = request.get_json()
    favourite_id = data.get("favourite_id")
    PlotFavourite.query.filter_by(
        user_id=user.user_id, plot_favourite_id=favourite_id
    ).delete()
    db.session.commit()
    return jsonify({"success": True})


@api_blueprint.route("/api/get_dashboard", methods=["POST"])
@check_user
def get_dashboard(user, *args, **kwargs):
    data = request.get_json()
    dashboard_id = data.get("dashboard_id")
    results = get_dashboard_data(user, dashboard_id)
    results["success"] = True
    return jsonify(results)


@api_blueprint.route("/api/save_dashboard", methods=["POST"])
@check_user
def save_dashboard(user, *args, **kwargs):
    data = request.get_json()
    title = data.get("title")
    request_data = data.get("data")
    is_public = data.get("is_public", False)
    dash_id = save_dashboard_data(user, title, request_data, is_public)
    return jsonify({"dashboard_id": dash_id, "success": True})


@api_blueprint.route("/api/delete_dashboard", methods=["POST"])
@check_user
def delete_dashboard(user, *args, **kwargs):
    data = request.get_json()
    dashboard_id = data.get("dashboard_id")
    Dashboard.query.filter_by(user_id=user.user_id, dashboard_id=dashboard_id).delete()
    db.session.commit()
    return jsonify({"success": True})


@api_blueprint.route("/api/count_queued_uploads", methods=["POST"])
def count_queued_uploads():
    count = get_queued_uploads(count=True)
    return jsonify({"success": True, "count": count})
