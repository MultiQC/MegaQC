import pytest
from pkg_resources import resource_stream

from megaqc.model import models
from megaqc.rest_api import schemas
from tests import factories


@pytest.fixture()
def upload(session):
    r = factories.UploadFactory()
    session.add(r)
    session.commit()
    return r


def test_post_upload_list(db, client, token):
    """
    Test uploading a report
    """
    rv = client.post(
        '/rest_api/v1/uploads',
        data={'report': resource_stream('tests', 'multiqc_data.json')},
        headers={'access_token': token}
    )

    # Check the request was successful
    assert rv.status_code == 201

    data = schemas.UploadSchema().load(rv.json)

    # Check that there is a new Upload
    uploads = db.session.query(models.Upload).count()
    assert uploads == 1


def test_get_upload_path(session, upload, client, token, admin_token):
    """
    Check that the 'path' field is only returned to admins
    """
    user_rv = client.get('/rest_api/v1/uploads/{}'.format(upload.upload_id), headers={'access_token': token})
    data = schemas.UploadSchema(many=False).load(user_rv.json)

    # A regular user shouldn't receive the filepath
    assert 'path' not in data

    admin_rv = client.get('/rest_api/v1/uploads/{}'.format(upload.upload_id), headers={'access_token': admin_token})
    data = schemas.UploadSchema(many=False).load(admin_rv.json)

    # An admin should receive the filepath
    assert 'path' in data
