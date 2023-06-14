import json

from flask_restful import url_for
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.collections import InstrumentedList
from webargs.fields import DelimitedList

from megaqc.extensions import db, ma
from megaqc.model import models


class JsonString(ma.Field):
    """
    Serializes a JSON structure as JSON, but deserializes it as a string (for DB
    storage), or vice-versa.
    """

    def _jsonschema_type_mapping(self):
        return {
            "type": "string",
        }

    def __init__(self, *args, invert=False, **kwargs):
        self.invert = invert
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if self.invert:
            return json.dumps(value)
        else:
            return json.loads(value)

    def _deserialize(self, value, attr, data, **kwargs):
        if self.invert:
            return json.loads(value)
        else:
            return json.dumps(value)


class ModelAssociation(ma.Field):
    """
    Dumps as a foreign key, e.g. "3", and loads as a model instance, e.g. User.
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

    def _serialize(self, value, attr, obj, **kwargs):
        return inspect(value).identity

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None

        return db.session.query(self.model).get(value)


class FilterReferenceList(DelimitedList):
    def deserialize(self, *args, **kwargs):
        list = super().deserialize(*args, **kwargs)


class FilterReference(ModelAssociation):
    """
    Dumps as a SampleFilter foreign key, e.g. "3", and loads as a filter array.
    """

    def _jsonschema_type_mapping(self):
        return {
            "type": "array",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(models.SampleFilter, *args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return []

        instance = super()._deserialize(value, attr, data, **kwargs)
        if not instance:
            return []

        return instance.filter_json
