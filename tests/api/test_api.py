"""
Generic tests for normal resources that follow a schema for GET, POST, DELETE etc
"""
import pytest
from flask import url_for
from sqlalchemy import inspect
from sqlalchemy.orm import RelationshipProperty
from marshmallow import EXCLUDE

from tests import factories


def unset_dump_only(schema):
    for field in schema.declared_fields.values():
        field.dump_only = False
    schema._init_fields()


def dump_only_fields(schema):
    """
    Returns a list of field names for the dump_only fields
    """
    return [key for key, field in schema._declared_fields.items() if field.dump_only]


def object_as_dict(obj, relationships=False):
    """
    Converts an SQLAlchemy instance to a dictionary
    :param relationships: If true, also include relationships in the output dict
    """
    properties = inspect(obj).mapper.all_orm_descriptors

    if not relationships:
        properties = {
            key: value for key, value in properties.items()
            if not hasattr(value, 'prop') or not isinstance(value.prop,
                                                            RelationshipProperty)
        }

    return {key: getattr(obj, key) for key, value in properties.items()}


def resource_from_endpoint(app, endpoint):
    """
    Given a string endpoint, e.g. "rest_api.upload", returns the Resource object for that
    URL
    """
    return app.view_functions[endpoint].view_class


all_factories = factories.BaseFactory.__subclasses__()


def find_factory(model):
    """
    Returns a factory that will build an instance of the provided model
    """
    for factory in all_factories:
        if factory._meta.model == model:
            return factory


def relationship_fields(model):
    """
    Returns a list of keys that each correspond to a relationship on this model
    """
    return [rel.key for rel in inspect(model).relationships.values()]


def instance_pk(instance):
    """
    Returns a tuple of (column_name, column_value) for the first primary key on this
    instance
    """
    column_name = inspect(instance.__class__).primary_key[0].name
    return column_name, getattr(instance, column_name)


def find_matching_resource(data, instance, model):
    """
    Given an array of dictionaries, checks if at least one of the dictionaries matches
    the provided instance
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
    Given a single dictionary, checks if it matches the provided SQLAlchemy model instance
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
    Clones an SQLAlchemy instance
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
    Generate a new object using the factory, except that relationships are copied from the
    provided instance, ensuring that no new objects are created
    """
    rels = {key: getattr(instance, key) for key in
            relationship_fields(instance.__class__)}
    return factory(**rels)


@pytest.mark.parametrize('endpoint', [
    'rest_api.uploadlist',
    'rest_api.sampledatalist',
    'rest_api.reportlist',
    'rest_api.reportmetalist',
    'rest_api.samplelist',
    'rest_api.metatypelist',
    'rest_api.datatypelist',
    'rest_api.userlist',
    'rest_api.filterlist',
    'rest_api.filtergrouplist',
    'rest_api.favouriteplotlist',
    'rest_api.dashboardlist'
])
def test_get_many_resources(endpoint, session, client, admin_token, app):
    """
    GET /resource
    """
    resource = resource_from_endpoint(app, endpoint)
    model = resource.data_layer['model']
    factory = find_factory(model)

    # Construct an instance of the model
    instance = factory()
    session.commit()

    # Do the request
    url = url_for(endpoint)
    rv = client.get(url, headers={
        'access_token': admin_token,
        'Content-Type': 'application/json'
    })

    # Check the request was successful
    assert rv.status_code == 200, rv.json

    # Load the data using the schema. This also does data validation
    ret = rv.json
    del ret['meta']
    del ret['jsonapi']
    schema = resource.schema(many=True)

    # We actually want to load the "dump_only" fields here, so that we can validate they
    # were dumped correctly. We don't normally want to do this, which is why this is a
    # test function only
    unset_dump_only(schema)
    data = schema.load(ret)

    # Check we got at least one instance
    assert len(data) > 0

    match = find_matching_resource(data, instance, model)
    assert match


@pytest.mark.parametrize(
    ['endpoint', 'foreign_key'],
    [
        ['rest_api.user_uploadlist', 'user_id'],
        ['rest_api.user_reportlist', 'user_id'],
        ['rest_api.report_reportmetalist', 'report_id'],
        ['rest_api.report_samplelist', 'report_id'],
        ['rest_api.sample_sampledatalist', 'sample_id'],
        ['rest_api.user_filterlist', 'user_id'],
        ['rest_api.user_favouriteplotlist', 'user_id'],
        ['rest_api.user_dashboardlist', 'user_id'],
    ])
def test_get_many_resources_associated(endpoint, foreign_key, session, client,
                                       admin_token, app):
    """
    Tests a list resource that is the child of another resource, e.g. /reports/1/samples
    """
    resource = resource_from_endpoint(app, endpoint)
    model = resource.data_layer['model']
    factory = find_factory(model)

    # Construct an instance of the model, and a second one that we don't want returned,
    # since it has a different parent
    instance = factory()
    dummy_instance = factory()
    session.commit()

    # The rule object gives us access to URL parameters
    url = url_for(endpoint, id=getattr(instance, foreign_key))

    # Do the request
    rv = client.get(url, headers={
        'access_token': admin_token,
        'Content-Type': 'application/json'
    })
    # Check the request was successful
    assert rv.status_code == 200, rv.json

    ret = rv.json
    del ret['meta']
    del ret['jsonapi']

    # This also does data validation
    data = resource.schema(many=True).load(ret)

    # Check we got at least the instance we created
    assert len(data) > 0

    match = find_matching_resource(data, instance, model)
    assert match
    # assert instance in data
    # assert dummy_instance not in data


@pytest.mark.parametrize('endpoint', [
    'rest_api.upload',
    'rest_api.sampledata',
    'rest_api.report',
    'rest_api.sample',
    'rest_api.datatype',
    'rest_api.user',
    'rest_api.filter',
    'rest_api.favouriteplot',
    'rest_api.dashboard'
])
def test_get_single_resource(endpoint, session, client, admin_token, app):
    """
    GET /resource/1
    """
    resource = resource_from_endpoint(app, endpoint)
    model = resource.data_layer['model']
    factory = find_factory(model)

    # Construct an instance of the model
    instance = factory()
    session.commit()

    # Do the request
    pk = instance_pk(instance)[1]
    url = url_for(endpoint, id=pk)
    rv = client.get(url, headers={
        'access_token': admin_token,
        'Content-Type': 'application/json'
    })

    # Check the request was successful
    assert rv.status_code == 200, rv.json

    # Load the data using the schema. This also does data validation
    ret = rv.json
    del ret['jsonapi']
    schema = resource.schema(many=False)
    # See above for explanation
    unset_dump_only(schema)
    data = schema.load(ret)

    # Check we got at least one instance
    assert is_matching_resource(data, instance, model)


@pytest.mark.parametrize('endpoint', [
    'rest_api.upload',
    'rest_api.report',
    'rest_api.sample',
    'rest_api.datatype',
    'rest_api.user',
    'rest_api.filter',
    'rest_api.favouriteplot',
    'rest_api.dashboard'
])
def test_delete_single_resource(endpoint, session, client, admin_token, app):
    """
    DELETE /resource/1
    """
    resource = resource_from_endpoint(app, endpoint)
    model = resource.data_layer['model']
    factory = find_factory(model)

    # Construct an instance of the model
    instance = factory()
    session.commit()

    count_1 = session.query(model).count()

    # Do the request
    pk = instance_pk(instance)[1]
    url = url_for(endpoint, id=pk)
    rv = client.delete(url, headers={
        'access_token': admin_token,
        'Content-Type': 'application/json'
    })

    # Check the request was successful
    assert rv.status_code == 200, rv.json

    # Check the item was deleted
    count_2 = session.query(model).count()
    assert count_2 == count_1 - 1


@pytest.mark.parametrize('endpoint', [
    'rest_api.reportlist',
    'rest_api.samplelist',
    'rest_api.datatypelist',
    'rest_api.userlist',
    'rest_api.filterlist',
    'rest_api.favouriteplotlist',
    'rest_api.dashboardlist'
])
def test_post_resource(endpoint, admin_token, session, client, app):
    """
    POST /resources
    """
    resource = resource_from_endpoint(app, endpoint)

    # Construct an instance of the model
    model = resource.data_layer['model']
    factory = find_factory(model)
    instance = factory()
    session.commit()

    clone = factory_clone(instance, factory)
    # clone = clone_model(instance)
    session.expunge(clone)

    # If we're pretending to be a client, we don't want to send the dump_only fields
    # that might be computed
    dump_only = dump_only_fields(resource.schema)
    request = resource.schema(many=False, use_links=False, exclude=dump_only).dump(
        clone
    )

    count_1 = session.query(model).count()

    # Do the request
    url = url_for(endpoint)
    rv = client.post(url, json=request, headers={'access_token': admin_token})

    # Check the request was successful
    assert rv.status_code == 201, rv.json['errors']

    ret = rv.json
    del ret['jsonapi']

    # Check that we now have data
    count_2 = session.query(model).count()
    assert count_2 - count_1 == 1

    # Validate the returned data
    data = resource.schema(many=False, unknown=EXCLUDE).load(ret)
