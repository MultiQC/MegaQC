from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy.orm.collections import InstrumentedList
import json

from megaqc.model.models import *
from megaqc.user.models import *
from megaqc.extensions import ma
import marshmallow
from marshmallow import fields
from flask_restful import url_for


class BaseModelSchema(ModelSchema):

    @marshmallow.pre_load
    def set_nested_session(self, data):
        """Allow nested schemas to use the parent schema's session. This is a
        longstanding bug with marshmallow-sqlalchemy.

        https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/67
        https://github.com/marshmallow-code/marshmallow/issues/658#issuecomment-328369199
        """
        nested_fields = {k: v for k, v in self.fields.items() if type(v) == marshmallow.fields.Nested}
        for field in nested_fields.values():
            field.schema.session = self.session


class ResourceHyperlink(ma.Field):
    """
    Serializes as a hyperlink to a flask_restful Resource
    """

    def __init__(self, endpoint, url_args=None, *args, **kwargs):
        super(ResourceHyperlink, self).__init__(*args, **kwargs)

        # If the user passes in a list of args, we assume a field with the exact same name appears on the relation
        if isinstance(url_args, list):
            self.url_args = {key: None for key in url_args}
        else:
            self.url_args = url_args

        self.endpoint = endpoint

    def convert_url(self, object):
        args = {}
        for key, value in self.url_args.items():
            if value is None:
                args[key] = getattr(object, key)
            else:
                args[key] = getattr(object, value)

        return url_for(self.endpoint, **args)

    def _serialize(self, value, attr, obj):
        """
        :param value: The current value of this attribute (the SQLAlchemy model)
        :param attr: The name of the attribute
        :param obj: The current object we're serializing
        """
        if isinstance(value, InstrumentedList):
            return [self.convert_url(relation) for relation in value]
        else:
            return self.convert_url(value)

    def _deserialize(self, value, attr, data):
        return None
        # raise NotImplementedError()


class JsonString(ma.Field):
    """
    Serializes a JSON structure as JSON, but deserializes it as a string (for DB storage)
    """

    def _serialize(self, value, attr, obj):
        return json.loads(value)

    def _deserialize(self, value, attr, data):
        return json.dumps(value)


class SampleDataTypeSchema(BaseModelSchema):
    class Meta:
        model = SampleDataType


class SampleDataSchema(BaseModelSchema):
    key = ma.Method('type_key')
    section = ma.Method('type_section')

    def type_key(self, obj):
        return obj.data_type.data_key

    def type_section(self, obj):
        return obj.data_type.data_section

    class Meta:
        model = SampleData


class SampleSchema(BaseModelSchema):
    data = ma.Nested(SampleDataSchema, many=True, exclude=['sample', 'sample_data_id', 'data_type'])

    class Meta:
        model = Sample


class SampleFilterSchema(BaseModelSchema):
    # We don't use the model for the schema, since we want to rename all the fields
    class Meta:
        model = SampleFilter
        exclude = ('sample_filter_tag', 'sample_filter_name', 'is_public', 'sample_filter_id', 'sample_filter_data')

    tag = fields.String(attribute='sample_filter_tag')
    name = fields.String(attribute='sample_filter_name')
    public = fields.Boolean(attribute='is_public')
    id = fields.Integer(attribute='sample_filter_id')
    data = JsonString(attribute='sample_filter_data')
    user = ResourceHyperlink(endpoint='rest_api.user', url_args=[
        'user_id',
    ])


class ReportMetaSchema(BaseModelSchema):
    class Meta:
        model = ReportMeta


class ReportSchema(BaseModelSchema):
    samples = ResourceHyperlink(endpoint='rest_api.sample', url_args=[
        'report_id',
        'sample_id'
    ])

    report_meta = ma.Method('meta_dict')

    def meta_dict(self, obj):
        d = {}
        for record in obj.meta:
            d[record.report_meta_key] = record.report_meta_value
        return d

    class Meta:
        model = Report


class PlotConfigSchema(BaseModelSchema):
    class Meta:
        model = PlotConfig


class PlotDataSchema(BaseModelSchema):
    class Meta:
        model = PlotData


class PlotCategorySchema(BaseModelSchema):
    class Meta:
        model = PlotCategory


class PlotFavouriteSchema(BaseModelSchema):
    class Meta:
        model = PlotFavourite


class DashboardSchema(BaseModelSchema):
    class Meta:
        model = Dashboard


class UploadSchema(BaseModelSchema):
    class Meta:
        model = Upload


class RoleSchema(BaseModelSchema):
    class Meta:
        model = Role


class UserSchema(BaseModelSchema):
    id = fields.Integer(attribute='user_id')
    admin = fields.Boolean(attribute='is_admin')
    roles = fields.Function(lambda obj: [role.name for role in obj.roles])
    filters = fields.List(ma.HyperlinkRelated('rest_api.filter', url_key='filter_id'))
    reports = fields.List(ma.HyperlinkRelated('rest_api.report', url_key='report_id'))

    class Meta:
        model = User
        exclude = ('is_admin', 'user_id')
