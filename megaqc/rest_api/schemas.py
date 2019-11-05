"""fi
These schemas describe the format of the web requests to and from the API. They incidentally share most fields with the
database models, but they can be opinionated about REST-specific fields
"""
from marshmallow import post_load, validate, Schema as BaseSchema, INCLUDE
from marshmallow.schema import SchemaMeta
from marshmallow_jsonapi import fields as f, SchemaOpts
from marshmallow_jsonapi.flask import Relationship as BaseRelationship, Schema as JsonApiSchema
from marshmallow_jsonapi.utils import resolve_params
from marshmallow_sqlalchemy.schema import ModelSchema, ModelSchemaOpts, ModelSchemaMeta

from megaqc.extensions import db
from megaqc.model import models
from megaqc.user import models as user_models
from megaqc.rest_api.fields import JsonString, FilterReference


class CombinedOpts(SchemaOpts, ModelSchemaOpts):
    pass


class CombinedMeta(ModelSchemaMeta, SchemaMeta):
    @classmethod
    def get_declared_fields(mcs, klass, cls_fields, inherited_fields, dict_cls):
        return SchemaMeta.get_declared_fields(
            klass=klass,
            cls_fields=cls_fields,
            inherited_fields=inherited_fields,
            dict_cls=dict_cls
        )


class Relationship(BaseRelationship):
    def extract_value(self, data):
        ret = super().extract_value(data)
        if isinstance(ret, (int, str)) and hasattr(self.schema.opts, 'model') and hasattr(self.schema.opts, 'sqla_session'):
            return self.schema.opts.sqla_session.query(self.schema.opts.model).get(ret)
        return ret


# By using this metaclass, we stop all the default fields being copied into the schema, allowing us to rename them
# class OptionalLinkSchema(ModelSchema, JsonApiSchema, metaclass=CombinedMeta):
class OptionalLinkSchema(JsonApiSchema):
    def __init__(self, use_links=True, *args, **kwargs):
        self.use_links = use_links

        # include_all = kwargs.pop('include_data', False) is True

        super().__init__(*args, **kwargs)

        # if include_all:
        #     self.include_all_data()

    # @post_load()
    # def make_instance(self, data, **kwargs):
    #     """Deserialize data to an instance of the model. Update an existing row
    #     if specified in `self.instance` or loaded by primary key(s) in the data;
    #     else create a new row.
    #
    #     :param data: Data to deserialize.
    #     """
    #     instance = self.instance or self.get_instance(data)
    #     if instance is not None:
    #         for key, value in data.items():
    #             setattr(instance, key, value)
    #         return instance
    #     kwargs, association_attrs = self._split_model_kwargs_association(data)
    #     instance = self.opts.model(**kwargs)
    #     for attr, value in association_attrs.items():
    #         setattr(instance, attr, value)
    #     return instance

    def get_resource_links(self, item):
        kwargs = resolve_params(item, self.opts.self_url_kwargs or {})
        for arg in kwargs.values():
            if arg is None:
                return None

        # if not self.use_links:
        #     return None
        return super().get_resource_links(item)

    # def include_all_data(self):
    #     """
    #     Recursively set include_data for all relationships to this schema
    #     """
    #     for field in self.fields.values():
    #         if isinstance(field, BaseRelationship):
    #             field.include_data = True
    #             field.schema.include_all_data()
    @post_load()
    def remove_empty_id(self, item, **kwargs):
        """
        Hack to deal with empty ID field that has to be sent
        """
        id_field = self.fields['id'].attribute

        if hasattr(item, id_field):
            if getattr(item, id_field) is None:
                delattr(item, id_field)
        elif id_field in item and item[id_field] is None:
            del item[id_field]

        return item


# Make every JSON API schema use this
Schema = OptionalLinkSchema


class SampleDataTypeSchema(Schema):
    class Meta:
        sqla_session = db.session
        type_ = 'data_types'
        model = models.SampleDataType

    id = f.Integer(attribute='sample_data_type_id', allow_none=True, as_string=True)
    section = f.String(attribute='data_section')
    key = f.String(attribute='data_key')


class SampleDataSchema(Schema):
    class Meta:
        sqla_session = db.session
        type_ = 'sample_data'
        model = models.SampleData
        # self_view = 'rest_api.sampledata'
        # self_view_many = 'rest_api.sampledatalist'
        # self_view_kwargs = {
        #     'sample_id': '<sample_id>'
        # }

    id = f.Integer(attribute='sample_data_id', allow_none=True, as_string=True)
    value = f.String()

    # We can't link to the parent sample because of
    # https://github.com/marshmallow-code/marshmallow-jsonapi/issues/247

    report = Relationship(
        related_view='rest_api.report',
        related_view_kwargs={
            'id': '<report_id>'
        },
        many=False,
        type_='reports',
        include_resource_linkage=True,
        id_field='report_id',
        schema='ReportSchema'
    )
    sample = Relationship(
        related_view='rest_api.sample',
        related_view_kwargs={
            'id': '<sample_id>'
        },
        many=False,
        type_='samples',
        include_resource_linkage=True,
        id_field='sample_id',
        schema='SampleSchema'
    )

    data_type = Relationship(
        related_view='rest_api.datatypelist',
        related_view_kwargs={
            'id': '<sample_data_type_id>'
        },
        many=False,
        type_='data_types',
        include_resource_linkage=True,
        id_field='sample_data_type_id',
        schema='SampleDataTypeSchema'
    )


class SampleSchema(Schema):
    class Meta:
        sqla_session = db.session
        model = models.Sample
        type_ = 'samples'
        self_view = 'rest_api.sample'
        self_view_many = 'rest_api.samplelist'
        self_view_kwargs = {
            'id': '<id>'
        }

    id = f.Integer(attribute='sample_id', allow_none=True, as_string=True)
    name = f.String(attribute='sample_name')

    data = Relationship(
        related_view='rest_api.sample_sampledatalist',
        related_view_kwargs={
            'id': '<sample_id>'
        },
        many=True,
        type_='sample_data',
        # include_resource_linkage=True,
        schema="SampleDataSchema"
    )
    report = Relationship(
        related_view='rest_api.report',
        related_view_kwargs={
            'id': '<report_id>'
        },
        many=False,
        type_='reports',
        id_field='report_id',
        include_resource_linkage=True,
        schema='ReportSchema'
    )


class SampleFilterSchema(OptionalLinkSchema):
    class Meta:
        sqla_session = db.session
        type_ = "filters"
        model = models.SampleFilter
        self_view = 'rest_api.filter'
        self_view_many = 'rest_api.filterlist'
        self_view_kwargs = {
            'id': '<id>'
        }

    id = f.Integer(attribute='sample_filter_id', allow_none=True, as_string=True)
    tag = f.String(attribute='sample_filter_tag')
    name = f.String(attribute='sample_filter_name')
    public = f.Boolean(attribute='is_public')
    data = JsonString(attribute='sample_filter_data')

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'id': '<user_id>'
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
        model = models.SampleFilter
        sqla_session = db.session
        type_ = "filter_groups"

    id = f.String(attribute='sample_filter_tag', allow_none=True)


class ReportSchema(Schema):
    """
    This is an abstraction of Report + ReportMeta
    """

    class Meta:
        sqla_session = db.session
        model = models.Report
        type_ = 'reports'
        self_view = 'rest_api.report'
        self_view_many = 'rest_api.reportlist'
        self_view_kwargs = {
            'id': '<id>'
        }
        strict = True

    id = f.Integer(attribute='report_id', allow_none=True, as_string=True)
    hash = f.String(attribute='report_hash')
    created_at = f.DateTime()
    uploaded_at = f.DateTime()

    meta = Relationship(
        related_view='rest_api.report_reportmetalist',
        related_view_kwargs={
            'id': '<report_id>'
        },
        many=True,
        type_='report_meta',
        # include_resource_linkage=True,
        schema='ReportMetaSchema'
    )

    samples = Relationship(
        related_view='rest_api.report_samplelist',
        related_view_kwargs={
            'id': '<report_id>'
        },
        id_field='sample_id',
        many=True,
        type_='samples',
        # include_resource_linkage=True,
        schema='SampleSchema'
    )

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'id': '<user_id>'
        },
        many=False,
        type_='users',
        id_field='user_id',
        include_resource_linkage=True,
        schema='UserSchema'
    )


class UploadSchema(Schema):
    class Meta:
        sqla_session = db.session
        model = models.Upload
        type_ = 'uploads'
        self_view = 'rest_api.upload'
        self_view_many = 'rest_api.uploadlist'
        self_view_kwargs = {
            'id': '<id>'
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
            'id': '<user_id>'
        },
        many=False,
        type_='users',
        id_field='user_id',
        include_resource_linkage=True,
        schema='UserSchema'
    )


class ReportMetaSchema(Schema):
    class Meta:
        sqla_session = db.session
        model = models.ReportMeta
        type_ = 'report_meta'
        # self_view = 'rest_api.reportmeta'
        # self_view_kwargs = {
        #     'report_id': '<id>'
        # }

    id = f.Integer(attribute='report_meta_id', allow_none=True, as_string=True)
    key = f.String(attribute='report_meta_key')
    value = f.String(attribute='report_meta_value')

    report = Relationship(
        related_view='rest_api.report',
        related_view_kwargs={
            'id': '<report_id>'
        },
        many=False,
        type_='reports',
        id_field='report_id',
        include_resource_linkage=True,
        schema='ReportSchema'
    )


class FavouritePlotSchema(Schema):
    class Meta:
        sqla_session = db.session
        model = models.PlotFavourite
        type_ = 'favourites'
        self_view = 'rest_api.favouriteplot'
        self_view_kwargs = {
            'id': '<id>'
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
            'id': '<user_id>'
        },
        many=False,
        type_='users',
        id_field='user_id',
        include_resource_linkage=True,
        schema='UserSchema'
    )


class DashboardSchema(Schema):
    class Meta:
        sqla_session = db.session
        model = models.Dashboard
        type_ = 'dashboards'

    id = f.Integer(attribute='dashboard_id', allow_none=True, as_string=True)
    title = f.String()
    data = JsonString()
    is_public = f.Bool()
    modified_at = f.DateTime()
    created_at = f.DateTime()

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'id': '<user_id>'
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
        model = models.ReportMeta
        sqla_session = db.session
        type_ = 'report_meta_types'

    id = f.String(attribute='report_meta_key')


class UserSchema(Schema):
    class Meta:
        sqla_session = db.session
        model = user_models.User
        type_ = "users"
        self_view = 'rest_api.user'
        self_view_kwargs = {
            'id': '<id>'
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
        related_view='rest_api.user_reportlist',
        related_view_kwargs={
            'id': '<user_id>'
        },
        many=True,
        type_='reports',
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

    type = f.String(validate=validate.OneOf(
        ['date', 'daterange', 'timedelta', 'reportmeta', 'samplemeta']))
    value = f.Raw()
    key = f.Raw()
    cmp = f.String(
        validate=validate.OneOf(['eq', 'ne', 'le', 'lt', 'ge', 'gt', 'in', 'not in']))


class TrendInputSchema(BaseSchema):
    """
    Schema for the request for trend data (not the response)
    """
    fields = JsonString(invert=True)
    filter = FilterReference()
