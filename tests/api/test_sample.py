from megaqc.model import models, schemas
import pytest
from tests import factories


@pytest.fixture()
def sample(session):
    s = factories.SampleFactory.build()
    session.add(s)
    session.commit()
    return s


def test_get_sample_list(sample, db, client):
    rv = client.get('/rest_api/v1/samples')

    # Check the request was successful
    assert rv.status_code == 200

    # Check that the returned data matches the schema
    errors = schemas.SampleSchema(many=True, session=db.session).validate(rv.json)
    assert len(errors) == 0


def test_get_sample(sample, db, client):
    rv = client.get('/rest_api/v1/samples/{}'.format(sample.sample_id))

    # Check the request was successful
    assert rv.status_code == 200

    # Check that the returned data matches the schema
    errors = schemas.SampleSchema(many=False, session=db.session).validate(rv.json)
    assert len(errors) == 0


def test_delete_sample(sample, db, client, token, admin_token):
    # Check that there is one sample
    uploads = db.session.query(models.Sample).count()
    assert uploads == 1

    # Non-logged in users and non-admin users shouldn't be able to delete samples
    assert client.delete('/rest_api/v1/reports/{}'.format(sample.sample_id)).status_code == 403
    assert client.delete(
        '/rest_api/v1/reports/{}'.format(sample.sample_id),
        headers={'access_token': token}
    ).status_code == 403

    rv = client.delete('/rest_api/v1/samples/{}'.format(sample.sample_id), headers={'access_token': admin_token})

    # Check the request was successful
    assert rv.status_code == 200

    # Check that we deleted the sample
    uploads = db.session.query(models.Sample).count()
    assert uploads == 0
