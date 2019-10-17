"""fi
These schemas describe the format of the web requests to and from the API. They incidentally share most fields with the
database models, but they can be opinionated about REST-specific fields
"""
from marshmallow import post_load, validate, Schema as BaseSchema, INCLUDE
from marshmallow_jsonapi import fields as f
from marshmallow_jsonapi.flask import Relationship, Schema as JsonApiSchema

from megaqc.rest_api.fields import JsonString, FilterReference


class OptionalLinkSchema(JsonApiSchema):
    def __init__(self, use_links=True, *args, **kwargs):
        self.use_links = use_links
        super().__init__(*args, **kwargs)

    def get_resource_links(self, item):
        if not self.use_links:
            return None
        return super().get_resource_links(item)

    @post_load()
    def remove_empty_id(self, item, **kwargs):
        """
        Hack to deal with empty ID field that has to be sent
        """
        id_field = self.fields['id'].attribute
        if id_field in item and item[id_field] is None:
            del item[id_field]

        return item


# Make every JSON API schema use this
Schema = OptionalLinkSchema


class SampleDataTypeSchema(Schema):
    class Meta:
        type_ = 'data_types'

    id = f.Integer(attribute='sample_data_type_id', as_string=True)
    section = f.String(attribute='data_section')
    key = f.String(attribute='data_key')


class SampleDataSchema(Schema):
    class Meta:
        type_ = 'sample_data'
        # self_view = 'rest_api.sampledata'
        # self_view_many = 'rest_api.sampledata'
        # self_view_kwargs = {
        #     'sample_id': '<sample_id>'
        # }

    id = f.String(attribute='sample_data_id', allow_none=True)
    value = f.String()

    # We can't link to the parent sample because of
    # https://github.com/marshmallow-code/marshmallow-jsonapi/issues/247

    data_type = Relationship(
        related_view='rest_api.sampledatatype',
        related_view_kwargs={
            'type_id': '<sample_data_type_id>'
        },
        many=False,
        type_='data_types',
        include_resource_linkage=True,
        id_field='sample_data_type_id',
        schema='SampleDataTypeSchema',
    )


class SampleSchema(Schema):
    class Meta:
        type_ = 'samples'
        self_view = 'rest_api.sample'
        self_view_many = 'rest_api.samplelist'
        self_view_kwargs = {
            'sample_id': '<id>'
        }

    id = f.Integer(attribute='sample_id', allow_none=True, as_string=True)
    name = f.String(attribute='sample_name')
    data = Relationship(
        related_view='rest_api.sampledatalist',
        related_view_kwargs={
            'sample_id': '<sample_id>'
        },
        many=True,
        type_='sample_data',
        schema="SampleDataSchema"
    )


# By using this metaclass, we stop all the default fields being copied into the schema, allowing us to rename them
class SampleFilterSchema(OptionalLinkSchema):
    class Meta:
        type_ = "filters"
        self_view = 'rest_api.filter'
        self_view_many = 'rest_api.filterlist'
        self_view_kwargs = {
            'filter_id': '<id>'
        }

    id = f.Integer(attribute='sample_filter_id', allow_none=True, as_string=True)
    tag = f.String(attribute='sample_filter_tag')
    name = f.String(attribute='sample_filter_name')
    public = f.Boolean(attribute='is_public')
    data = JsonString(attribute='sample_filter_data')

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'user_id': '<user_id>'
        },
        type_='users',
        include_resource_linkage=True,
        id_field='user_id',
        schema='UserSchema'
    )


class FilterGroupSchema(OptionalLinkSchema):
    """
    Fake schema (no underlying model) for filter groups, which dump from a filter object
    """

    class Meta:
        type_ = "filter_groups"

    id = f.String(attribute='sample_filter_tag', allow_none=True)


class ReportSchema(Schema):
    """
    This is an abstraction of Report + ReportMeta
    """

    class Meta:
        type_ = 'reports'
        self_view = 'rest_api.report'
        self_view_many = 'rest_api.reportlist'
        self_view_kwargs = {
            'report_id': '<id>'
        }
        strict = True

    id = f.Integer(attribute='report_id', allow_none=True, as_string=True)
    hash = f.String(attribute='report_hash')
    created_at = f.DateTime()
    uploaded_at = f.DateTime()

    meta = Relationship(
        related_view='rest_api.reportmetalist',
        related_view_kwargs={
            'report_id': '<report_id>'
        },
        many=True,
        type_='report_meta',
        schema='ReportMetaSchema'
    )

    samples = Relationship(
        related_view='rest_api.samplelist',
        related_view_kwargs={
            'report_id': '<report_id>'
        },
        many=True,
        type_='sample',
        schema='SampleSchema'
    )

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'user_id': '<user_id>'
        },
        many=False,
        type_='users',
        id_field='user_id',
        include_resource_linkage=True,
        schema='UserSchema'
    )


class UploadSchema(Schema):
    class Meta:
        type_ = 'uploads'
        self_view = 'rest_api.upload'
        self_view_many = 'rest_api.uploadlist'
        self_view_kwargs = {
            'upload_id': '<id>'
        }
        strict = True

    id = f.Integer(attribute='upload_id', allow_none=True, as_string=True)
    status = f.String()
    path = f.String()
    message = f.String()
    created_at = f.DateTime()
    modified_at = f.DateTime()

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'user_id': '<user_id>'
        },
        many=False,
        type_='users',
        id_field='user_id',
        include_resource_linkage=True,
        schema='UserSchema'
    )


class ReportMetaSchema(Schema):
    class Meta:
        type_ = 'report_meta'
        # self_view = 'rest_api.reportmeta'
        # self_view_kwargs = {
        #     'report_id': '<id>'
        # }

    id = f.Integer(attribute='report_meta_id', allow_none=True, as_string=True)
    key = f.String(attribute='report_meta_key')
    value = f.String(attribute='report_meta_value')


class FavouritePlotSchema(Schema):
    class Meta:
        type_ = 'favourites'
        self_view = 'rest_api.favouriteplot'
        self_view_kwargs = {
            'favourite_id': '<id>'
        }

    id = f.Integer(attribute='plot_favourite_id', allow_none=True, as_string=True)
    title = f.String()
    description = f.String()
    plot_type = f.String(validate=validate.OneOf([
        'report_plot',
        'distribution',
        'trend',
        'comparison'
    ]))
    data = JsonString()
    created_at = f.DateTime(required=False)

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'user_id': '<user_id>'
        },
        many=False,
        type_='users',
        id_field='user_id',
        include_resource_linkage=True,
        schema='UserSchema'
    )


class DashboardSchema(Schema):
    class Meta:
        type_ = 'dashboards'

    id = f.Integer(attribute='dashboard_id', required=False, as_string=True)
    title = f.String()
    data = JsonString()
    is_public = f.Bool()
    modified_at = f.DateTime()
    created_at = f.DateTime()

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'user_id': '<user_id>'
        },
        many=False,
        type_='users',
        id_field='user_id',
        include_resource_linkage=True,
        schema='UserSchema'
    )


class ReportMetaTypeSchema(Schema):
    """
    This is an artificial type that doesn't have a backing model
    """

    class Meta:
        type_ = 'report_meta_types'

    id = f.String(attribute='report_meta_key')


class UserSchema(Schema):
    class Meta:
        type_ = "users"
        self_view = 'rest_api.user'
        self_view_kwargs = {
            'user_id': '<id>'
        }

    id = f.Int(attribute='user_id', required=False, allow_none=True, as_string=True)
    username = f.String()
    email = f.String()
    salt = f.String()
    password = f.String()
    created_at = f.DateTime()
    first_name = f.String()
    last_name = f.String()
    active = f.Boolean()
    admin = f.Boolean(attribute='is_admin')
    api_token = f.String()

    reports = Relationship(
        related_view='rest_api.reportlist',
        related_view_kwargs={
            'user_id': '<user_id>'
        },
        many=True,
        type_='report',
        required=False,
        schema='ReportSchema'
    )


class PlotSchema(Schema):
    """
    Data that can be used to generate a plot
    """

    class Meta:
        type_ = 'plots'
        unknown = INCLUDE

    id = f.String(dump_only=True)
    type = f.String()
    x = f.List(f.Raw())
    y = f.List(f.Raw())
    text = f.List(f.Raw())
    hoverinfo = f.Str()
    line = f.Dict()
    mode = f.String()
    name = f.String()
    fill = f.String()
    fillcolor = f.String()
    showlegend = f.Bool()


class TrendSchema(PlotSchema):
    """
    Data that can be used to generate a trend plot
    """
    x = f.List(f.DateTime())
    y = f.List(f.Number())


class FilterObjectSchema(BaseSchema):
    """
    A single filter object, e.g.
    {
        'type': 'daterange',
        'value': [],
        'cmp': 'in'
    }
    """

    type = f.String(validate=validate.OneOf(['date', 'daterange', 'timedelta', 'reportmeta', 'samplemeta']))
    value = f.Raw()
    key = f.Raw()
    cmp = f.String(validate=validate.OneOf(['eq', 'ne', 'le', 'lt', 'ge', 'gt', 'in', 'not in']))


class TrendInputSchema(BaseSchema):
    """
    Schema for the request for trend data (not the response)
    """
    fields = JsonString(invert=True)
    filter = FilterReference()
