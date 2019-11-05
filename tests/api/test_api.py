"""
Generic tests for normal resources that follow a schema for GET, POST, DELETE etc
"""
import pytest
from sqlalchemy.orm import make_transient

from megaqc.rest_api import schemas, views
from megaqc.model import models
from megaqc.user import models as user_models
from megaqc.rest_api import views
from megaqc.extensions import db
from tests import factories
from flask import url_for
from marshmallow_jsonapi.fields import Relationship, BaseRelationship
from sqlalchemy import inspect

def object_as_dict(obj, relationships=False):
    ret = { c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs }
    if relationships:
        ret.update({c.key: getattr(obj, c.key) for c in inspect(obj).mapper.relationships})
    return ret

all_factories = factories.BaseFactory.__subclasses__()
resource_details = [tuple[:2] for tuple in views.restful.resources if
                    issubclass(tuple[0], views.ResourceDetail)]
resource_lists = [tuple[:2] for tuple in views.restful.resources if
                  issubclass(tuple[0], views.ResourceList)]

def resource_from_endpoint(app, endpoint):
    return app.view_functions[endpoint].view_class


def find_factory(model):
    for factory in all_factories:
        if factory._meta.model == model:
            return factory

def relationship_fields(model):
    return [rel.key for rel in inspect(model).relationships.values()]

def instance_pk(instance):
    column_name = inspect(instance.__class__).primary_key[0].name
    return column_name, getattr(instance, column_name)

def matching_resource(data, instance, model):
    found = False
    for result in data:
        # Remove relationships because we can't validate them easily
        for field in relationship_fields(model):
            if field in result:
                del result[field]

        if result.items() <= object_as_dict(instance).items():
            return True

    return False

def clone_model(instance):
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
    rels = {key: getattr(instance, key) for key in relationship_fields(instance.__class__)}
    return factory(**rels)


@pytest.mark.parametrize('endpoint', [
    'rest_api.uploadlist',
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
def test_get_many_resources_new(endpoint, session, client, admin_token, app):
    resource = resource_from_endpoint(app, endpoint)
    model = resource.data_layer['model']
    factory = find_factory(model)

    # Construct an instance of the model
    instance = factory()
    session.commit()

    # Do the request
    url = url_for(endpoint)
    rv = client.get(url, headers={'access_token': admin_token,
                                  'Content-Type': 'application/json'})

    # Check the request was successful
    assert rv.status_code == 200

    # Load the data using the schema. This also does data validation
    ret = rv.json
    del ret['meta']
    del ret['jsonapi']
    data = resource.schema(many=True).load(ret)

    # Check we got at least one instance
    assert len(data) > 0

    match = matching_resource(data, instance, model)
    assert match
    # # Check it's the same instance as we created
    # assert data[-1] is instance



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
def test_get_many_resources_associated(endpoint, foreign_key, session, client, admin_token, app):
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
    rv = client.get(url, headers={'access_token': admin_token,
                                  'Content-Type': 'application/json'})
    # Check the request was successful
    assert rv.status_code == 200

    ret = rv.json
    del ret['meta']
    del ret['jsonapi']

    # This also does data validation
    data = resource.schema(many=True).load(ret)

    # Check we got at least the instance we created
    assert len(data) > 0

    match = matching_resource(data, instance, model)
    assert match
    # assert instance in data
    # assert dummy_instance not in data


@pytest.mark.parametrize('endpoint', [
    'rest_api.uploadlist',
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

    # # Remove the object from the database, because we're going to submit it via the API
    # session.expunge_all()
    # session.expunge(instance)
    session.commit()

    clone = factory_clone(instance, factory)
    # clone = clone_model(instance)
    session.expunge(clone)

    # # Work out which fields are relationships, so we can attach all of it in the request
    # relationships = set([key for key, value in resource.schema._declared_fields.items() if
    #                      isinstance(value, Relationship)])

    # Serialize it
    # TODO: work out how to include all relationships, not just top level ones
    request = resource.schema(many=False, use_links=False).dump(clone)

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
    data = resource.schema(many=False).load(ret)
# @pytest.mark.parametrize(argnames, [
#     argvalues['report'],
#     argvalues['upload'],
#     argvalues['sample'],
#     argvalues['filter'],
#     argvalues['user'],
#     argvalues['sample_data'],
#     argvalues['report_meta'],
#     argvalues['sample_data_type'],
#     argvalues['filter_group'],
#     argvalues['favourite'],
#     argvalues['dashboard'],
# ])
# def test_get_many_resources(client, single_endpoint, many_endpoint, schema, factory, id_field, admin_token, model,
#                             no_post, session):
#     """
#     GET /resources
#     """
#
#     # Construct an instance of the model
#     instance = factory()
#     session.commit()
#
#     # Do the request
#     rv = client.get(many_endpoint(instance), headers={'access_token': admin_token})
#
#     # Check the request was successful
#     assert rv.status_code == 200
#
#     # This also does data validation
#     data = schema(many=True).load(rv.json)
#
#     # Check we got at least the instance we created
#     assert len(data) > 0
#
#     # And it had the right ID
#     assert data[-1][id_field] == str(getattr(instance, id_field))
#
#
# # We can't post samples, reports or uploads in the normal way, so don't test them here
# @pytest.mark.parametrize(argnames, [
#     argvalues['filter'],
#     argvalues['user'],
#     argvalues['sample_data'],
#     argvalues['report_meta']
# ])
# def test_post_resource(client, single_endpoint, many_endpoint, schema, factory, id_field, admin_token, model, session,
#                        no_post):
#     """
#     POST /resources
#     """
#
#     # Construct an instance of the model
#     instance = factory()
#     if instance in session:
#         session.expunge(instance)
#     session.commit()
#
#     # Work out which fields are relationships
#     relationships = set([key for key, value in schema._declared_fields.items() if isinstance(value, Relationship)])
#     no_post = set(no_post)
#
#     # Serialize it
#     request = schema(many=False, use_links=False, exclude=no_post, include_data=relationships - no_post).dump(instance)
#
#     count_1 = session.query(model).count()
#
#     # Do the request
#     rv = client.post(many_endpoint(instance), json=request, headers={'access_token': admin_token})
#
#     # Check the request was successful
#     assert rv.status_code == 201
#
#     # Check that we now have data
#     count_2 = session.query(model).count()
#     assert count_2 - count_1 == 1
#
#     # Validate the returned data
#     data = schema(many=False).load(rv.json)
#
#
# @pytest.mark.parametrize(argnames, [
#     argvalues['report'],
#     argvalues['upload'],
#     argvalues['sample'],
#     argvalues['filter'],
#     argvalues['user']
# ])
# def test_delete_resource(session, client, single_endpoint, many_endpoint, schema, factory, id_field, model, token,
#                          admin_token, no_post):
#     """
#     DELETE /resources/1
#     """
#
#     # Construct an instance of the model
#     instance = factory()
#
#     count_1 = session.query(model).count()
#
#     # An admin should be able to delete anything (this doesn't test when resources shouldn't be deletable by regular
#     # users
#     rv = client.delete(single_endpoint(instance), headers={'access_token': admin_token})
#
#     # Check the request was successful, as an admin
#     assert rv.status_code == 200
#
#     # Check that we deleted the row from the DB
#     count_2 = session.query(model).count()
#     assert count_1 - count_2 == 1
#
#
# @pytest.mark.parametrize(argnames, [
#     argvalues['report'],
#     argvalues['upload'],
#     argvalues['sample'],
#     argvalues['filter'],
#     argvalues['user'],
#     argvalues['sample_data_type']
# ])
# def test_get_resource(session, client, single_endpoint, many_endpoint, schema, factory, id_field, model,
#                       admin_token, no_post):
#     """
#     GET /resources/1
#     """
#
#     # Construct an instance of the model
#     instance = factory()
#     session.add(instance)
#     session.commit()
#
#     # Do the request
#     rv = client.get(single_endpoint(instance), headers={'access_token': admin_token})
#
#     # Check the request was successful
#     assert rv.status_code == 200
#
#     # This also does data validation
#     data = schema(many=False).load(rv.json)
#
#     # And it had the right ID
#     assert data[id_field] == str(getattr(instance, id_field))
