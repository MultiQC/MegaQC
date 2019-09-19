"""
Generic tests for normal resources that follow a schema for GET, POST, DELETE etc
"""
import pytest
from megaqc.rest_api import schemas
from megaqc.model import models
from megaqc.user import models as user_models
from tests import factories
from flask import url_for
from marshmallow_jsonapi.fields import Relationship

argnames = ['single_endpoint', 'many_endpoint', 'schema', 'factory', 'id_field', 'model', 'no_post']
argvalues = {
    'report': [
        lambda m: url_for('rest_api.report', report_id=m.report_id),
        lambda m: url_for('rest_api.reportlist'),
        schemas.ReportSchema,
        factories.ReportFactory,
        'report_id',
        models.Report,
        []
    ],
    'upload': [
        lambda m: url_for('rest_api.upload', upload_id=m.upload_id),
        lambda m: url_for('rest_api.uploadlist'),
        schemas.UploadSchema,
        factories.UploadFactory,
        'upload_id',
        models.Upload,
        []
    ],
    'sample': [
        lambda m: url_for('rest_api.sample', sample_id=m.sample_id),
        lambda m: url_for('rest_api.sampleslist'),
        schemas.SampleSchema,
        factories.SampleFactory,
        'sample_id',
        models.Sample,
        []
    ],
    'filter': [
        lambda m: url_for('rest_api.filter', filter_id=m.sample_filter_id),
        lambda m: url_for('rest_api.filterlist'),
        schemas.SampleFilterSchema,
        factories.SampleFilterFactory,
        'sample_filter_id',
        models.SampleFilter,
        ['user']
    ],
    'filter_group': [
        None,
        lambda m: url_for('rest_api.filtergrouplist'),
        schemas.FilterGroupSchema,
        factories.SampleFilterFactory,
        'sample_filter_tag',
        models.SampleFilter,
        ['user']
    ],
    'user': [
        lambda m: url_for('rest_api.user', user_id=m.user_id),
        lambda m: url_for('rest_api.userlist'),
        schemas.UserSchema,
        factories.UserFactory,
        'user_id',
        user_models.User,
        ['salt', 'reports', 'api_token']
    ],
    'sample_data': [
        lambda m: url_for('rest_api.sampledata', sample_id=m.sample_id),
        lambda m: url_for('rest_api.sampledata', sample_id=m.sample_id),
        schemas.SampleDataSchema,
        factories.SampleDataFactory,
        'sample_data_id',
        models.SampleData,
        []
    ],
    'report_meta': [
        lambda m: None,
        lambda m: url_for('rest_api.reportmeta', report_id=m.report_id),
        schemas.ReportMetaSchema,
        factories.ReportMetaFactory,
        'report_meta_id',
        models.ReportMeta,
        []
    ],
    'sample_data_type': [
        lambda m: url_for('rest_api.sampledatatype', type_id=m.sample_data_type_id),
        lambda m: url_for('rest_api.sampledatatypelist'),
        schemas.SampleDataTypeSchema,
        factories.SampleDataTypeFactory,
        'sample_data_type_id',
        models.SampleDataType,
        []
    ],
    'favourite': [
        lambda m: url_for('rest_api.favouriteplot', favourite_id=m.plot_favourite_id),
        lambda m: url_for('rest_api.favouriteplotlist'),
        schemas.FavouritePlotSchema,
        factories.FavouritePlotFactory,
        'plot_favourite_id',
        models.PlotFavourite,
        []
    ],
    'dashboard': [
        lambda m: url_for('rest_api.dashboard', dashboard_id=m.dashboard_id),
        lambda m: url_for('rest_api.dashboardlist'),
        schemas.DashboardSchema,
        factories.DashboardFactory,
        'dashboard_id',
        models.Dashboard,
        []
    ],
}


@pytest.mark.parametrize(argnames, [
    argvalues['report'],
    argvalues['upload'],
    argvalues['sample'],
    argvalues['filter'],
    argvalues['user'],
    argvalues['sample_data'],
    argvalues['report_meta'],
    argvalues['sample_data_type'],
    argvalues['filter_group'],
    argvalues['favourite'],
    argvalues['dashboard'],
])
def test_get_many_resources(client, single_endpoint, many_endpoint, schema, factory, id_field, admin_token, model,
                            no_post, session):
    """
    GET /resources
    """

    # Construct an instance of the model
    instance = factory()
    session.commit()

    # Do the request
    rv = client.get(many_endpoint(instance), headers={'access_token': admin_token})

    # Check the request was successful
    assert rv.status_code == 200

    # This also does data validation
    data = schema(many=True).load(rv.json)

    # Check we got at least the instance we created
    assert len(data) > 0

    # And it had the right ID
    assert data[-1][id_field] == str(getattr(instance, id_field))


# We can't post samples, reports or uploads in the normal way, so don't test them here
@pytest.mark.parametrize(argnames, [
    argvalues['filter'],
    argvalues['user'],
    argvalues['sample_data'],
    argvalues['report_meta']
])
def test_post_resource(client, single_endpoint, many_endpoint, schema, factory, id_field, admin_token, model, session,
                       no_post):
    """
    POST /resources
    """

    # Construct an instance of the model
    instance = factory()
    if instance in session:
        session.expunge(instance)
    session.commit()

    # Work out which fields are relationships
    relationships = set([key for key, value in schema._declared_fields.items() if isinstance(value, Relationship)])
    no_post = set(no_post)

    # Serialize it
    request = schema(many=False, use_links=False, exclude=no_post, include_data=relationships - no_post).dump(instance)

    count_1 = session.query(model).count()

    # Do the request
    rv = client.post(many_endpoint(instance), json=request, headers={'access_token': admin_token})

    # Check the request was successful
    assert rv.status_code == 201

    # Check that we now have data
    count_2 = session.query(model).count()
    assert count_2 - count_1 == 1

    # Validate the returned data
    data = schema(many=False).load(rv.json)


@pytest.mark.parametrize(argnames, [
    argvalues['report'],
    argvalues['upload'],
    argvalues['sample'],
    argvalues['filter'],
    argvalues['user']
])
def test_delete_resource(session, client, single_endpoint, many_endpoint, schema, factory, id_field, model, token,
                         admin_token, no_post):
    """
    DELETE /resources/1
    """

    # Construct an instance of the model
    instance = factory()

    count_1 = session.query(model).count()

    # An admin should be able to delete anything (this doesn't test when resources shouldn't be deletable by regular
    # users
    rv = client.delete(single_endpoint(instance), headers={'access_token': admin_token})

    # Check the request was successful, as an admin
    assert rv.status_code == 200

    # Check that we deleted the row from the DB
    count_2 = session.query(model).count()
    assert count_1 - count_2 == 1


@pytest.mark.parametrize(argnames, [
    argvalues['report'],
    argvalues['upload'],
    argvalues['sample'],
    argvalues['filter'],
    argvalues['user'],
    argvalues['sample_data_type']
])
def test_get_resource(session, client, single_endpoint, many_endpoint, schema, factory, id_field, model,
                      admin_token, no_post):
    """
    GET /resources/1
    """

    # Construct an instance of the model
    instance = factory()
    session.add(instance)
    session.commit()

    # Do the request
    rv = client.get(single_endpoint(instance), headers={'access_token': admin_token})

    # Check the request was successful
    assert rv.status_code == 200

    # This also does data validation
    data = schema(many=False).load(rv.json)

    # And it had the right ID
    assert data[id_field] == str(getattr(instance, id_field))
