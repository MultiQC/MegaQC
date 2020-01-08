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
    count_1 = db.session.query(models.Upload).count()

    rv = client.post(
        '/rest_api/v1/uploads',
        data={'report': resource_stream('tests', 'multiqc_data.json')},
        headers={
            'access_token': token,
            'Content-Type': 'multipart/form-data',
            'Accept': 'application/json'
        }
    )

    # Check the request was successful
    assert rv.status_code == 201, rv.json

    # Validate the response
    schemas.UploadSchema().validate(rv.json)

    # Check that there is a new Upload
    count_2 = db.session.query(models.Upload).count()
    assert count_2 == count_1 + 1
