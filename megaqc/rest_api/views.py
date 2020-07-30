"""
Location of a rewritten API in a RESTful style, with appropriate resources
Following the JSON API standard where relevant: https://jsonapi.org/format/
"""

from hashlib import sha1
from http import HTTPStatus

import megaqc.user.models as user_models
from flapison import ResourceDetail, ResourceList, ResourceRelationship
from flask import Blueprint, jsonify, make_response, request
from flask_login import current_user
from marshmallow.utils import EXCLUDE, INCLUDE
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from megaqc.api.views import check_user
from megaqc.extensions import db, json_api, restful
from megaqc.model import models
from megaqc.rest_api import plot, schemas, utils
from megaqc.rest_api.content import json_to_csv
from megaqc.rest_api.webarg_parser import use_args, use_kwargs

api_bp = Blueprint("rest_api", __name__, url_prefix="/rest_api/v1")
json_api.blueprint = api_bp


class Upload(ResourceDetail):
    schema = schemas.UploadSchema
    data_layer = dict(session=db.session, model=models.Upload)


class UploadList(ResourceList):
    view_kwargs = True
    schema = schemas.UploadSchema
    data_layer = dict(session=db.session, model=models.Upload)
    request_parsers = {"multipart/form-data": lambda x: x}

    def get_schema_kwargs(self, args, kwargs):
        # Only show the filepath if they're an admin
        if "user" in kwargs and kwargs["permission"] <= utils.Permission.ADMIN:
            return {"exclude": ["path"]}

        return {}

    @check_user
    def post(self, **kwargs):
        """
        Upload a new report.
        """
        # This doesn't exactly follow the JSON API spec, since it doesn't exactly support file uploads:
        # https://github.com/json-api/json-api/issues/246
        file_name = utils.get_unique_filename()
        request.files["report"].save(file_name)
        upload_row = models.Upload.create(
            status="NOT TREATED",
            path=file_name,
            message="File has been created, loading in MegaQC is queued.",
            user_id=kwargs["user"].user_id,
        )

        return schemas.UploadSchema(many=False).dump(upload_row), HTTPStatus.CREATED


class UploadRelationship(ResourceRelationship):
    schema = schemas.UploadSchema
    data_layer = dict(session=db.session, model=models.Upload)


class ReportList(ResourceList):
    view_kwargs = True
    schema = schemas.ReportSchema
    data_layer = dict(session=db.session, model=models.Report)


class Report(ResourceDetail):
    schema = schemas.ReportSchema
    data_layer = dict(session=db.session, model=models.Report)


class ReportRelationship(ResourceRelationship):
    schema = schemas.ReportSchema
    data_layer = dict(session=db.session, model=models.Report)


class ReportMeta(ResourceDetail):
    view_kwargs = True
    schema = schemas.ReportMetaSchema
    data_layer = dict(session=db.session, model=models.ReportMeta)


class ReportMetaList(ResourceList):
    view_kwargs = True
    schema = schemas.ReportMetaSchema
    data_layer = dict(session=db.session, model=models.ReportMeta)


class ReportMetaRelationship(ResourceRelationship):
    schema = schemas.ReportMetaSchema
    data_layer = dict(session=db.session, model=models.ReportMeta)


class Sample(ResourceDetail):
    schema = schemas.SampleSchema
    data_layer = dict(session=db.session, model=models.Sample)


class SampleList(ResourceList):
    view_kwargs = True
    schema = schemas.SampleSchema
    data_layer = dict(session=db.session, model=models.Sample)


class SampleRelationship(ResourceRelationship):
    schema = schemas.SampleSchema
    data_layer = dict(session=db.session, model=models.Sample)


class ReportMetaTypeList(ResourceList):
    view_kwargs = True
    schema = schemas.ReportMetaTypeSchema
    data_layer = dict(session=db.session, model=models.ReportMeta)

    # def _list_query(self, **kwargs):
    def get_collection(self, qs, kwargs, filters=None):
        # We override the query because this resource is basically simulated, and doesn't correspond to an underlying
        # model
        query = (
            db.session.query(models.ReportMeta)
            .with_entities(models.ReportMeta.report_meta_key)
            .distinct()
        )

        return query.count(), query.all()


class SampleData(ResourceDetail):
    view_kwargs = True
    schema = schemas.SampleDataSchema
    data_layer = dict(session=db.session, model=models.SampleData)


class SampleDataList(ResourceList):
    view_kwargs = True
    schema = schemas.SampleDataSchema
    data_layer = dict(session=db.session, model=models.SampleData)


class SampleDataRelationship(ResourceRelationship):
    schema = schemas.SampleDataSchema
    data_layer = dict(session=db.session, model=models.SampleData)


class DataType(ResourceDetail):
    schema = schemas.SampleDataTypeSchema
    data_layer = dict(session=db.session, model=models.SampleDataType)


class DataTypeList(ResourceList):
    view_kwargs = True
    schema = schemas.SampleDataTypeSchema
    data_layer = dict(session=db.session, model=models.SampleDataType)


class User(ResourceDetail):
    schema = schemas.UserSchema
    data_layer = dict(session=db.session, model=user_models.User)


class UserRelationship(ResourceRelationship):
    schema = schemas.UserSchema
    data_layer = dict(session=db.session, model=user_models.User)


class UserList(ResourceList):
    view_kwargs = True
    schema = schemas.UserSchema
    data_layer = dict(session=db.session, model=user_models.User)

    def get_schema_kwargs(self, args, kwargs):
        # Only show the filepath if they're an admin
        if "user" in kwargs and kwargs["permission"] <= utils.Permission.ADMIN:
            return {"exclude": ["reports", "salt", "api_token"]}

        return {}

    def create_object(self, data, kwargs):
        # Creating a user requires generating a password
        new_user = super().create_object(data, kwargs)
        new_user.set_password(data["password"])
        new_user.active = True
        new_user.save()
        return new_user


class CurrentUser(ResourceDetail):
    schema = schemas.UserSchema
    data_layer = dict(session=db.session, model=user_models.User)

    @utils.check_perms
    def get(self, **kwargs):
        """
        Get details about the current user.

        This is also how the frontend can get an access token. For that
        reason, this endpoint is authenticated using the session, NOT
        the access token
        """

        # Fail if we aren't logged in
        if current_user.is_anonymous:
            return "", HTTPStatus.UNAUTHORIZED

        user = (
            db.session.query(user_models.User)
            .filter(user_models.User.user_id == current_user.user_id)
            .first_or_404()
        )

        if kwargs["permission"] >= utils.Permission.ADMIN:
            # If an admin is making this request, give them everything
            schema_kwargs = {}
        else:
            # If it's a user requesting their own data, exclude password info
            schema_kwargs = {"exclude": ["salt", "password"]}

        return schemas.UserSchema(many=False, **schema_kwargs).dump(user)


class FilterList(ResourceList):
    view_kwargs = True
    schema = schemas.SampleFilterSchema
    data_layer = dict(session=db.session, model=models.SampleFilter)


class Filter(ResourceDetail):
    schema = schemas.SampleFilterSchema
    data_layer = dict(session=db.session, model=models.SampleFilter)


class FilterRelationship(ResourceRelationship):
    schema = schemas.SampleFilterSchema
    data_layer = dict(session=db.session, model=models.SampleFilter)


class FilterGroupList(ResourceList):
    view_kwargs = True
    schema = schemas.FilterGroupSchema
    data_layer = dict(session=db.session, model=models.SampleFilter)

    def get_collection(self, qs, kwargs, filters=None):
        query = (
            self._data_layer.query(kwargs)
            .with_entities(models.SampleFilter.sample_filter_tag)
            .distinct()
        )

        return query.count(), query.all()


class FavouritePlotList(ResourceList):
    view_kwargs = True
    schema = schemas.FavouritePlotSchema
    data_layer = dict(session=db.session, model=models.PlotFavourite)


class FavouritePlot(ResourceDetail):
    schema = schemas.FavouritePlotSchema
    data_layer = dict(session=db.session, model=models.PlotFavourite)


class FavouritePlotRelationship(ResourceRelationship):
    schema = schemas.FavouritePlotSchema
    data_layer = dict(session=db.session, model=models.PlotFavourite)


class DashboardList(ResourceList):
    view_kwargs = True
    schema = schemas.DashboardSchema
    data_layer = dict(session=db.session, model=models.Dashboard)


class DashboardRelationship(ResourceList):
    view_kwargs = True
    schema = schemas.DashboardSchema
    data_layer = dict(session=db.session, model=models.Dashboard)


class Dashboard(ResourceDetail):
    schema = schemas.DashboardSchema
    data_layer = dict(session=db.session, model=models.Dashboard)


class TrendSeries(ResourceList):
    @use_args(schemas.TrendInputSchema(), locations=("querystring",))
    def get(self, args):
        # We need to give each resource a unique ID so the client doesn't try to cache
        # or reconcile different plots
        request_hash = sha1(request.query_string).hexdigest()

        plots = plot.trend_data(plot_prefix=request_hash, **args)

        return schemas.TrendSchema(many=True, unknown=INCLUDE).dump(plots)


json_api.route(Upload, "upload", "/uploads/<int:id>")
json_api.route(UploadList, "uploadlist", "/uploads")
json_api.route(UploadList, "user_uploadlist", "/users/<int:id>/uploads")
json_api.route(
    UploadRelationship, "userupload", "/users/<int:id>/relationships/uploads"
)

json_api.route(Report, "report", "/reports/<int:id>")
json_api.route(ReportList, "reportlist", "/reports")
json_api.route(ReportList, "user_reportlist", "/users/<int:id>/reports")
json_api.route(
    ReportRelationship, "report_samples_rel", "/reports/<int:id>/relationships/samples"
)

json_api.route(User, "user", "/users/<int:id>")
json_api.route(UserList, "userlist", "/users")
json_api.route(CurrentUser, "currentuser", "/users/current")
json_api.route(
    UserRelationship, "user_reports_rel", "/users/<int:id>/relationships/reports"
)
json_api.route(
    UserRelationship, "user_filters_rel", "/users/<int:id>/relationships/filters"
)

json_api.route(ReportMeta, "reportmeta", "/report_meta/<int:id>")
json_api.route(ReportMetaList, "reportmetalist", "/report_meta")
json_api.route(ReportMetaList, "report_reportmetalist", "/reports/<int:id>/report_meta")
json_api.route(
    ReportMetaRelationship,
    "report_reportmeta_rel",
    "/reports/<int:id>/relationships/report_meta",
)

json_api.route(Sample, "sample", "/samples/<int:id>")
json_api.route(SampleList, "samplelist", "/samples")
json_api.route(SampleList, "report_samplelist", "/reports/<int:id>/samples")

json_api.route(ReportMetaTypeList, "metatypelist", "/meta_types")

json_api.route(SampleData, "sampledata", "/sample_data/<int:id>")
json_api.route(SampleDataList, "sampledatalist", "/sample_data")
json_api.route(SampleDataList, "sample_sampledatalist", "/samples/<int:id>/sample_data")
json_api.route(
    SampleDataRelationship,
    "sample_sampledata",
    "/samples/<int:id>/relationships/sample_data",
)

json_api.route(DataType, "datatype", "/data_types/<int:id>")
json_api.route(DataTypeList, "datatypelist", "/data_types")

json_api.route(
    Filter, "filter", "/filters/<int:id>",
)
json_api.route(FilterList, "filterlist", "/filters")
json_api.route(FilterList, "user_filterlist", "/users/<int:id>/filters")

json_api.route(FilterGroupList, "filtergrouplist", "/filter_groups")

json_api.route(FavouritePlot, "favouriteplot", "/favourites/<int:id>")
json_api.route(FavouritePlotList, "favouriteplotlist", "/favourites")
json_api.route(
    FavouritePlotList, "user_favouriteplotlist", "/users/<int:id>/favourites"
)
json_api.route(
    FavouritePlotRelationship,
    "user_favourites_rel",
    "/users/<int:id>/relationships/favourites",
)

json_api.route(Dashboard, "dashboard", "/dashboards/<int:id>")
json_api.route(DashboardList, "dashboardlist", "/dashboards")
json_api.route(DashboardList, "user_dashboardlist", "/users/<int:id>/dashboards")
json_api.route(
    DashboardRelationship,
    "user_dashboards_rel",
    "/users/<int:id>/relationships/dashboards",
)

json_api.route(TrendSeries, "trend_data", "/plots/trends/series")
