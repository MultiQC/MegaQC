"""
Location of a rewritten API in a RESTful style, with appropriate resources
Following the JSON API standard where relevant: https://jsonapi.org/format/
"""
from http import HTTPStatus
from hashlib import sha1

from flask import request, Blueprint, jsonify, make_response
from flask_login import login_required, current_user
from flask_restful import Resource
from marshmallow.utils import INCLUDE
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from sqlalchemy.orm import joinedload, contains_eager

import megaqc.user.models as user_models
from megaqc import model
from megaqc.api.views import check_user, check_admin
from megaqc.extensions import db, restful
from megaqc.model import models
from megaqc.rest_api import schemas, filters, utils, plot
from megaqc.rest_api.webarg_parser import use_args, use_kwargs, error_handler
from megaqc.rest_api.content import json_to_csv

api_bp = Blueprint('rest_api', __name__, url_prefix='/rest_api/v1')


@api_bp.errorhandler(IncorrectTypeError)
def handle_jsonapi_error(e):
    """
    Handles a marshmallow validation error, and returns a structured JSON response
    """
    return make_response(jsonify(e.messages), HTTPStatus.BAD_REQUEST)


class UploadList(Resource):
    @check_user
    def get(self, user, user_id=None):
        """
        Get a list of pending uploads
        """
        query = db.session.query(
            models.Upload,
        )
        if user_id is not None:
            query = query.filter(models.Upload.user_id == user_id)

        # Only show the filepath if they're an admin
        exclude = [] if user.is_admin else ['path']

        return schemas.UploadSchema(many=True, exclude=exclude).dump(query.all())

    @check_user
    def post(self, user):
        """
        Upload a new report
        """
        # This doesn't exactly follow the JSON API spec, since it doesn't exactly support file uploads:
        # https://github.com/json-api/json-api/issues/246
        file_name = utils.get_unique_filename()
        request.files['report'].save(file_name)
        upload_row = models.Upload.create(
            status="NOT TREATED",
            path=file_name,
            message="File has been created, loading in MegaQC is queued.",
            user_id=user.user_id
        )

        # Only show the filepath if they're an admin
        exclude = [] if user.is_admin else ['path']

        return schemas.UploadSchema(exclude=exclude).dump(upload_row), HTTPStatus.CREATED


class Upload(Resource):
    @check_user
    def get(self, upload_id, user, user_id=None):
        """
        Get data about a single upload
        """
        upload = db.session.query(
            models.Upload,
        ).filter(
            models.Upload.upload_id == upload_id
        ).first_or_404()

        # Only show the filepath if they're an admin
        exclude = [] if user.is_admin else ['path']

        return schemas.UploadSchema(many=False, exclude=exclude).dump(upload)

    @check_admin
    def delete(self, upload_id, user, user_id=None):
        """
        Get data about a single upload
        """
        upload = db.session.query(
            models.Upload,
        ).filter(
            models.Upload.upload_id == upload_id
        ).first_or_404()

        db.session.delete(upload)
        db.session.commit()

        return {}


class ReportList(Resource):
    def get(self, user_id=None):
        """
        Get a list of reports
        """
        query = db.session.query(
            models.Report,
        )
        if user_id is not None:
            query = query.filter(models.Report.user_id == user_id)

        return schemas.ReportSchema(many=True).dump(query.all())

    @check_user
    def post(self, user):
        """
        Upload a new report
        """
        return '', HTTPStatus.METHOD_NOT_ALLOWED


class Report(Resource):
    def get(self, report_id):
        """
        Get data about this report
        """
        report_meta = db.session.query(
            models.Report,
        ).options(
            joinedload(models.Report.meta)
        ).filter(
            models.Report.report_id == report_id
        ).first()

        return schemas.ReportSchema(many=False).dump(report_meta)

    def put(self, report_id):
        """
        Update this report
        """
        return '', HTTPStatus.METHOD_NOT_ALLOWED

    @check_admin
    def delete(self, report_id, user):
        """
        Delete this report
        """
        db.session.query(models.Report).filter(models.Report.report_id == report_id).delete()
        db.session.commit()
        return {}


class ReportMeta(Resource):
    def get(self, report_id):
        """
        Get all data for a sample
        """
        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        meta = db.session.query(
            models.ReportMeta
        ).filter(
            models.ReportMeta.report_id == report_id
        ).all()

        return schemas.ReportMetaSchema(many=True).dump(meta)

    def post(self, report_id):
        data = schemas.ReportMetaSchema(many=False).load(request.json)
        instance = models.ReportMeta.create(**data, report_id=report_id)
        return schemas.ReportMetaSchema(many=False).dump(instance), HTTPStatus.CREATED


class ReportMetaTypeList(Resource):
    def get(self):
        """
        Get all possible report data types
        """
        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        type = db.session.query(
            models.ReportMeta
        ).with_entities(models.ReportMeta.report_meta_key).distinct().all()

        return schemas.ReportMetaTypeSchema(many=True).dump(type)


class SamplesList(Resource):
    def get(self, report_id=None):
        """
        Get all samples for this report
        """

        # Only apply the report filter if we had a report ID
        filters = []
        if report_id is not None:
            filters.append(models.Sample.report_id == report_id)

        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        samples = db.session.query(
            models.Sample
        ).options(
            joinedload(models.Sample.data).joinedload(models.SampleData.data_type)
        ).filter(
            *filters
        ).all()

        return schemas.SampleSchema(many=True).dump(samples)

    def post(self, report_id):
        # Currently we only support uploading samples via a report
        return {}, HTTPStatus.METHOD_NOT_ALLOWED


class Sample(Resource):
    def get(self, sample_id, report_id=None):
        """
        Get a single sample within a report
        """
        samples = db.session.query(
            models.Sample
        ).options(
            joinedload(models.Sample.data).joinedload(models.SampleData.data_type)
        ).filter(
            models.Sample.sample_id == sample_id
        ).first()

        return schemas.SampleSchema(many=False).dump(samples)

    def put(self, report_id, sample_id):
        """
        Update an existing sample
        """
        raise NotImplementedError()

    @check_admin
    def delete(self, sample_id, user, report_id=None):
        """
        Delete a single sample
        """
        db.session.query(
            models.Sample
        ).options(
            joinedload(models.Sample.data).joinedload(models.SampleData.data_type)
        ).filter(
            models.Sample.sample_id == sample_id
        ).delete()

        db.session.commit()

        return {}


class SampleData(Resource):
    def get(self, sample_id):
        """
        Get all data for a sample
        """
        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        samples = db.session.query(
            models.SampleData
        ).options(
            joinedload(models.SampleData.data_type)
        ).filter(
            models.SampleData.sample_id == sample_id
        ).all()

        return schemas.SampleDataSchema(many=True, include_data=['data_type']).dump(samples)

    def post(self, sample_id):
        loaded = schemas.SampleDataSchema(many=False, include_data=['data_type']).load(request.json)
        data_type = models.SampleDataType.get_or_create(loaded.pop('data_type'))
        instance = models.SampleData.create(**loaded, data_type=data_type, sample_id=sample_id)
        return schemas.SampleDataSchema(many=False).dump(instance), HTTPStatus.CREATED


class SampleDataType(Resource):
    def get(self, type_id):
        """
        Get all possible data types
        """
        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        type = db.session.query(
            models.SampleDataType
        ).filter(
            models.SampleDataType.sample_data_type_id == type_id
        ).first_or_404()

        return schemas.SampleDataTypeSchema(many=False).dump(type)


class SampleDataTypeList(Resource):
    def get(self):
        """
        Get all possible data types
        """
        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        types = db.session.query(
            models.SampleDataType
        ).all()

        return schemas.SampleDataTypeSchema(many=True).dump(types)


class UserList(Resource):
    @check_admin
    def get(self, user):
        """
        Get a list of users
        """
        users = db.session.query(
            user_models.User
        ).options(
            joinedload(user_models.User.roles)
        ).all()

        # Only admins can do this, so it doesn't matter if we return their password/key
        return schemas.UserSchema(many=True).dump(users)

    def post(self):
        """
        Create a new user
        """
        data = schemas.UserSchema(exclude=['reports', 'salt', 'api_token']).load(request.json)
        new_user = user_models.User(**data)
        new_user.set_password(data['password'])
        new_user.active = True
        new_user.save()

        return schemas.UserSchema().dump(new_user), HTTPStatus.CREATED


class User(Resource):
    @check_admin
    def get(self, user_id, user):
        """
        Get a specific user
        """
        users = db.session.query(
            user_models.User
        ).options(
            joinedload(user_models.User.roles)
        ).filter(
            user_models.User.user_id == user_id
        ).first()

        return schemas.UserSchema(many=False).dump(users)

    def put(self, user_id):
        """
        Update a user
        """
        raise NotImplementedError()

    @check_admin
    def delete(self, user_id, user):
        """
        Delete a user
        """
        db.session.query(
            user_models.User
        ).filter(
            user_models.User.user_id == user_id
        ).delete()
        db.session.commit()

        return {}


class CurrentUser(Resource):
    @login_required
    def get(self):
        """
        Get details about the current user. This is also how the frontend can get an access token. For that reason,
        this endpoint is authenticated using the session, NOT the access token
        """

        # Fail if we aren't logged in
        if current_user.is_anonymous:
            return '', HTTPStatus.UNAUTHORIZED

        user = db.session.query(
            user_models.User
        ).filter(
            user_models.User.user_id == current_user.user_id
        ).first_or_404()

        return schemas.UserSchema(many=False, exclude=('salt', 'password')).dump(user)


class FilterGroupList(Resource):
    def get(self):
        """
        Get a list of filter groups
        """
        results = db.session.query(
            models.SampleFilter
        ).with_entities(
            models.SampleFilter.sample_filter_tag
        ).distinct().all()
        return schemas.FilterGroupSchema(many=True).dump(results)


class FilterList(Resource):
    def get(self, user_id=None):
        query = db.session.query(
            models.SampleFilter
        ).join(
            user_models.User, user_models.User.user_id == models.SampleFilter.user_id
        ).options(
            # We're already joining to the users table in order to filter, so use this to load the relationship
            contains_eager(models.SampleFilter.user)
        )

        # If this is the filter list for a single user, filter it down to that
        if user_id is not None:
            query = query.filter(user_models.User.user_id == user_id)

        results = query.all()
        return schemas.SampleFilterSchema(many=True).dump(results)

    @check_user
    def post(self, user, user_id=None):
        load_schema = schemas.SampleFilterSchema(many=False, exclude=['user'])
        dump_schema = schemas.SampleFilterSchema(many=False)

        model = load_schema.load(request.json)
        model['user_id'] = user.user_id
        instance = models.SampleFilter(**model)
        db.session.add(instance)
        db.session.commit()

        return dump_schema.dump(instance), HTTPStatus.CREATED


class Filter(Resource):
    def get(self, filter_id, user_id=None):
        query = db.session.query(
            models.SampleFilter
        ).join(
            user_models.User, user_models.User.user_id == models.SampleFilter.user_id
        ).options(
            contains_eager(models.SampleFilter.user)
        ).filter(
            models.SampleFilter.sample_filter_id == filter_id
        )

        # If this is the filter list for a single user, filter it down to that
        if user_id is not None:
            query = query.filter(user_models.User.user_id == user_id)

        results = query.first_or_404()

        return schemas.SampleFilterSchema(many=False).dump(results)

    @check_user
    def put(self, filter_id, user, user_id=None):
        load_schema = schemas.SampleFilterSchema(many=False, exclude=('user', 'id'))

        # Find an instance that meets the user_id and filter_id constraints
        query = db.session.query(
            models.SampleFilter
        ).join(
            user_models.User, user_models.User.user_id == models.SampleFilter.user_id
        ).options(
            contains_eager(models.SampleFilter.user)
        ).filter(
            models.SampleFilter.sample_filter_id == filter_id
        )
        if user_id is not None:
            query = query.filter(user_models.User.user_id == user_id)
        curr_instance = query.first_or_404()

        # Check permissions
        if not (user.is_admin or curr_instance.user_id == user.user_id):
            return '', HTTPStatus.UNAUTHORIZED

        # Update the instance
        new_instance = load_schema.load(request.json, session=db.session, instance=curr_instance).data
        db.session.add(model)
        db.session.commit()

        # Dump the new instance as the response
        dump_schema = schemas.SampleFilterSchema(many=False)
        return dump_schema.dump(new_instance)

    def delete(self, filter_id):
        instance = db.session.query(
            models.SampleFilter
        ).get_or_404(filter_id)

        db.session.delete(instance)
        db.session.commit()

        return {}


class TrendSeries(Resource):
    @use_kwargs(schemas.TrendInputSchema(), locations=('querystring',))
    def get(self, fields, filter, outliers):
        # We need to give each resource a unique ID so the client doesn't try to cache or reconcile different plots
        request_hash = sha1(request.query_string).hexdigest()

        plots = plot.trend_data(
            fields=fields,
            filters=filter,
            outlier_det=outliers,
            plot_prefix=request_hash
        )

        return schemas.TrendSchema(many=True, unknown=INCLUDE).dump(plots)


class FavouritePlotList(Resource):
    def get(self):
        """
        Get a list of favourite plots
        """
        plots = db.session.query(
            models.PlotFavourite
        ).all()

        return schemas.FavouritePlotSchema(many=True, unknown=INCLUDE).dump(plots)

    @use_args(schemas.FavouritePlotSchema(), locations=('json',))
    @check_user
    def post(self, args, user):
        """
        Save a new favourite
        """
        favourite = models.PlotFavourite.create(**args, user=user)
        return schemas.FavouritePlotSchema(many=False).dump(favourite), HTTPStatus.CREATED


class FavouritePlot(Resource):
    def get(self, favourite_id):
        """
        Get a certain plot
        """
        plot = db.session.query(
            models.PlotFavourite
        ).get_or_404(favourite_id)

        return schemas.FavouritePlotSchema(many=False).dump(plot)

    def delete(self, favourite_id):
        """
        Get a certain plot
        """
        plot = db.session.query(
            models.PlotFavourite
        ).get_or_404(favourite_id)

        db.session.delete(plot)
        db.session.commit()

        return {}


class DashboardList(Resource):
    def get(self):
        """
        Get a list of dashboards
        """
        dash = db.session.query(
            models.Dashboard
        ).all()

        return schemas.DashboardSchema(many=True, unknown=INCLUDE).dump(dash)

    @use_args(schemas.FavouritePlotSchema(), locations=('json',))
    @check_user
    def post(self, args, user):
        """
        Save a new favourite
        """
        dash = models.Dashboard.create(**args, user=user)
        return schemas.DashboardSchema(many=False).dump(dash), HTTPStatus.CREATED


class Dashboard(Resource):
    def get(self, dashboard_id):
        """
        Get a certain plot
        """
        dashboard = db.session.query(
            models.Dashboard
        ).get_or_404(dashboard_id)

        return schemas.DashboardSchema(many=False).dump(dashboard)

    def delete(self, dashboard_id):
        """
        Get a certain plot
        """
        plot = db.session.query(
            models.Dashboard
        ).get_or_404(dashboard_id)

        db.session.delete(plot)
        db.session.commit()

        return {}


@restful.representation('text/csv')
def output_csv(resp, code, headers=None):
    csv = json_to_csv(resp['data'], delimiter='\t')
    resp = make_response(csv, code)
    resp.headers.extend(headers or {})
    return resp


restful.add_resource(UploadList, '/uploads', '/users/<int:user_id>/uploads')
restful.add_resource(Upload, '/uploads/<int:upload_id>')

restful.add_resource(ReportList, '/reports', '/users/<int:user_id>/reports')
restful.add_resource(Report, '/reports/<int:report_id>')

restful.add_resource(ReportMeta, '/reports/<int:report_id>/report_meta')
restful.add_resource(ReportMetaTypeList, '/report_meta')

restful.add_resource(SamplesList, '/reports/<int:report_id>/samples', '/samples')
restful.add_resource(Sample, '/samples/<int:sample_id>')
restful.add_resource(SampleData, '/samples/<int:sample_id>/sample_data')

restful.add_resource(SampleDataType, '/data_types/<int:type_id>')
restful.add_resource(SampleDataTypeList, '/data_types')

restful.add_resource(UserList, '/users')
restful.add_resource(CurrentUser, '/users/current')
restful.add_resource(User, '/users/<int:user_id>')

restful.add_resource(TrendSeries, '/plots/trends/series', endpoint='trend_data')

restful.add_resource(FilterList, '/filters', '/users/<int:user_id>/filters')
restful.add_resource(Filter, '/filters/<int:filter_id>')

restful.add_resource(FavouritePlotList, '/favourites', '/users/<int:user_id>/favourites')
restful.add_resource(FavouritePlot, '/favourites/<int:favourite_id>')

restful.add_resource(DashboardList, '/dashboards', '/users/<int:user_id>/dashboards')
restful.add_resource(Dashboard, '/dashboards/<int:dashboard_id>')

restful.add_resource(FilterGroupList, '/filter_groups')

restful.init_app(api_bp)
