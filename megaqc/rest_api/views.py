"""
Location of a rewritten API in a RESTful style, with appropriate resources
Following the JSON API standard where relevant: https://jsonapi.org/format/
"""

from hashlib import sha1
from http import HTTPStatus

from flask import Blueprint
from flask import request, jsonify, make_response
from flask_login import current_user
from marshmallow.utils import INCLUDE
from marshmallow_jsonapi.exceptions import IncorrectTypeError

import megaqc.user.models as user_models
from megaqc.api.views import check_user
from megaqc.extensions import db
from megaqc.extensions import restful
from megaqc.model import models
from megaqc.rest_api import schemas, utils, plot
from megaqc.rest_api.content import json_to_csv
from megaqc.rest_api.resources import ResourceDetail, ResourceList
from megaqc.rest_api.webarg_parser import use_kwargs

api_bp = Blueprint("rest_api", __name__, url_prefix="/rest_api/v1")


@restful.representation("text/csv")
def output_csv(resp, code, headers=None):
    csv = json_to_csv(resp["data"], delimiter="\t")
    resp = make_response(csv, code)
    resp.headers.extend(headers or {})
    return resp


@api_bp.errorhandler(IncorrectTypeError)
def handle_jsonapi_error(e):
    """
    Handles a marshmallow validation error, and returns a structured JSON response
    """
    return make_response(jsonify(e.messages), HTTPStatus.BAD_REQUEST)


@restful.resource("/uploads/<int:upload_id>")
class Upload(ResourceDetail):
    schema = schemas.UploadSchema
    model = models.Upload


@restful.resource("/uploads", "/users/<int:user_id>/uploads")
class UploadList(ResourceList):
    schema = schemas.UserSchema
    model = user_models.User

    @classmethod
    def _get_exclude(cls, **kwargs):
        # Only show the filepath if they're an admin
        if 'user' in kwargs:
            return [] if kwargs['permission'] >= utils.Permission.ADMIN else ["path"]
        else:
            return []

    @check_user
    def post(self, **kwargs):
        """
        Upload a new report
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

        return self._dump(upload_row), HTTPStatus.CREATED


@restful.resource("/reports", "/users/<int:user_id>/reports")
class ReportList(ResourceList):
    schema = schemas.ReportSchema
    model = models.Report


@restful.resource("/reports/<int:report_id>")
class Report(ResourceDetail):
    schema = schemas.ReportSchema
    model = models.Report


@restful.resource("/reports/<int:report_id>/report_meta", "/report_meta")
class ReportMetaList(ResourceList):
    schema = schemas.ReportMetaSchema
    model = models.ReportMeta


@restful.resource("/reports/<int:report_id>/samples", "/samples")
class SampleList(ResourceList):
    schema = schemas.SampleSchema
    model = models.Sample


@restful.resource("/meta_type")
class ReportMetaTypeList(ResourceList):
    schema = schemas.ReportMetaSchema
    model = models.ReportMeta

    def _list_query(self, **kwargs):
        # We override the query because this resource is basically simulated, and doesn't correspond to an underlying
        # model
        return (
            db.session.query(self.model)
                .with_entities(models.ReportMeta.report_meta_key)
                .distinct()
        )


@restful.resource("/samples/<int:sample_id>")
class Sample(ResourceDetail):
    schema = schemas.SampleSchema
    model = models.Sample


@restful.resource("/samples/<int:sample_id>/sample_data")
class SampleDataList(ResourceList):
    schema = schemas.SampleDataSchema
    model = models.SampleData


@restful.resource("/data_types/<int:type_id>")
class DataType(ResourceDetail):
    schema = schemas.SampleDataTypeSchema
    model = models.SampleDataType


@restful.resource("/data_types")
class DataTypeList(ResourceList):
    schema = schemas.SampleDataTypeSchema
    model = models.SampleDataType


@restful.resource("/users/<int:user_id>")
class User(ResourceDetail):
    schema = schemas.UserSchema
    model = user_models.User


@restful.resource("/users")
class UserList(ResourceList):
    schema = schemas.UserSchema
    model = user_models.User

    @classmethod
    def _get_exclude(cls, user, permission, **kwargs):
        # Only show the filepath if they're an admin
        return (
            []
            if permission >= utils.Permission.ADMIN
            else ["reports", "salt", "api_token"]
        )

    def _create_model(self, data, **kwargs):
        # Creating a user requires generating a password
        new_user = super()._create_model(data, **kwargs)
        new_user.set_password(data["password"])
        new_user.active = True
        new_user.save()


@restful.resource("/users/current")
class CurrentUser(ResourceDetail):
    schema = schemas.UserSchema
    model = user_models.User

    def _get_exclude(self, user, permissions, **kwargs):
        # Only show the filepath if they're an admin
        return [] if permissions >= utils.Permission.ADMIN else ["salt", "api_token"]

    def get(self, **kwargs):
        """
        Get details about the current user. This is also how the frontend can get an access token. For that reason,
        this endpoint is authenticated using the session, NOT the access token
        """

        # Fail if we aren't logged in
        if current_user.is_anonymous:
            return "", HTTPStatus.UNAUTHORIZED

        user = (
            db.session.query(user_models.User)
                .filter(user_models.User.user_id == current_user.user_id)
                .first_or_404()
        )

        return schemas.UserSchema(many=False, exclude=self._get_exclude(**kwargs)).dump(
            user
        )


@restful.resource("/filters", "/users/<int:user_id>/filters")
class FilterList(ResourceList):
    schema = schemas.SampleFilterSchema
    model = models.SampleFilter


@restful.resource("/filters/<int:filter_id>")
class Filter(ResourceDetail):
    schema = schemas.SampleFilterSchema
    model = models.SampleFilter


@restful.resource("/filter_groups")
class FilterGroupList(ResourceList):
    model = models.SampleFilter
    schema = schemas.FilterGroupSchema

    def _list_query(self, **kwargs):
        return (
            super()
                ._list_query(**kwargs)
                .with_entities(models.SampleFilter.sample_filter_tag)
                .distinct()
        )


@restful.resource("/favourites", "/users/<int:user_id>/favourites")
class FavouritePlotList(ResourceList):
    schema = schemas.FavouritePlotSchema
    model = models.PlotFavourite


@restful.resource("/favourites/<int:favourite_id>")
class FavouritePlot(ResourceDetail):
    schema = schemas.FavouritePlotSchema
    model = models.PlotFavourite


@restful.resource("/dashboards", "/users/<int:user_id>/dashboards")
class DashboardList(ResourceList):
    schema = schemas.DashboardSchema
    model = models.Dashboard


@restful.resource("/dashboards/<int:dashboard_id>")
class Dashboard(ResourceDetail):
    schema = schemas.DashboardSchema
    model = models.Dashboard


@restful.resource("/plots/trends/series")
class TrendSeries(ResourceDetail):
    @use_kwargs(schemas.TrendInputSchema(), locations=("querystring",))
    def get(self, fields, filter):
        # We need to give each resource a unique ID so the client doesn't try to cache or reconcile different plots
        request_hash = sha1(request.query_string).hexdigest()

        plots = plot.trend_data(fields=fields, filters=filter, plot_prefix=request_hash)

        return schemas.TrendSchema(many=True, unknown=INCLUDE).dump(plots)


restful.init_app(api_bp)
