import pytest
from flask import url_for
from marshmallow import EXCLUDE
from sqlalchemy import inspect
from sqlalchemy.orm import RelationshipProperty

from tests import factories

single_resource_endpoints = [
    "rest_api.upload",
    "rest_api.sampledata",
    "rest_api.report",
    "rest_api.sample",
    "rest_api.datatype",
    "rest_api.user",
    "rest_api.filter",
    "rest_api.favouriteplot",
    "rest_api.dashboard",
]

list_resource_endpoints = [
    "rest_api.uploadlist",
    "rest_api.sampledatalist",
    "rest_api.reportlist",
    "rest_api.reportmetalist",
    "rest_api.samplelist",
    "rest_api.metatypelist",
    "rest_api.datatypelist",
    "rest_api.userlist",
    "rest_api.filterlist",
    "rest_api.filtergrouplist",
    "rest_api.favouriteplotlist",
    "rest_api.dashboardlist",
]


def unset_dump_only(schema):
    """
    Unset the "dump_only" property for every field in this schema.
    """
    for field in schema.declared_fields.values():
        field.dump_only = False
    schema._init_fields()


def dump_only_fields(schema):
    """
    Returns a list of field names for the dump_only fields.
    """
    return [key for key, field in schema._declared_fields.items() if field.dump_only]


def object_as_dict(obj, relationships=False):
    """
    Converts an SQLAlchemy instance to a dictionary.

    :param relationships: If true, also include relationships in the output dict
    """
    properties = inspect(obj).mapper.all_orm_descriptors

    if not relationships:
        properties = {
            key: value
            for key, value in properties.items()
            if not hasattr(value, "prop")
            or not isinstance(value.prop, RelationshipProperty)
        }

    return {key: getattr(obj, key) for key, value in properties.items()}


def resource_from_endpoint(app, endpoint):
    """
    Given a string endpoint, e.g. "rest_api.upload", returns the Resource
    object for that URL.
    """
    return app.view_functions[endpoint].view_class


all_factories = factories.BaseFactory.__subclasses__()


def find_factory(model):
    """
    Returns a factory that will build an instance of the provided model.
    """
    for factory in all_factories:
        if factory._meta.model == model:
            return factory


def relationship_fields(model):
    """
    Returns a list of keys that each correspond to a relationship on this
    model.
    """
    return [rel.key for rel in inspect(model).relationships.values()]


def instance_pk(instance):
    """
    Returns a tuple of (column_name, column_value) for the first primary key on
    this instance.
    """
    column_name = inspect(instance.__class__).primary_key[0].name
    return column_name, getattr(instance, column_name)


def find_matching_resource(data, instance, model):
    """
    Given an array of dictionaries, checks if at least one of the dictionaries
    matches the provided instance.

    :param data: A list of dictionaries
    :param instance: An SQLAlchemy model instance
    :param model: An SQLAlchemy model (subclass of declarative_base())
    """
    for result in data:
        if is_matching_resource(result, instance, model):
            return True
    return False


def is_matching_resource(result, instance, model):
    """
    Given a single dictionary, checks if it matches the provided SQLAlchemy
    model instance.

    :param result: Instance dictionary
    :param instance: An SQLAlchemy model instance
    :param model: An SQLAlchemy model (subclass of declarative_base())
    """
    # Remove relationships because we can't validate them easily
    for field in relationship_fields(model):
        if field in result:
            del result[field]

    if result.items() <= object_as_dict(instance).items():
        return True

    return False


def clone_model(instance):
    """
    Clones an SQLAlchemy instance.
    """
    # Copy the attributes as a dictionary
    dict = object_as_dict(instance, relationships=True)
    # Find the primary key and remove the ID
    column_name = inspect(instance.__class__).primary_key[0].name
    del dict[column_name]
    # Create a new instance using this data
    new_instance = instance.__class__(**dict)
    return new_instance


def factory_clone(instance, factory):
    """
    Generate a new object using the factory, except that relationships are
    copied from the provided instance, ensuring that no new objects are
    created.
    """
    rels = {
        key: getattr(instance, key) for key in relationship_fields(instance.__class__)
    }
    return factory(**rels)
