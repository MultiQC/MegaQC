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


@pytest.mark.parametrize(
    "file_name",
    [
        "multiqc_data.json",  # MultiQC Pre-1.20
        "multiqc_data_v120.json",  # MultiQC 1.20 Plotly-backed format
        "multiqc_data_v120_hc.json",  # MultiQC 1.20 with `--template highcharts` legacy backend
    ],
)
def test_post_upload_list(db, client, token, file_name):
    """
    Test uploading a report.
    """
    count_1 = db.session.query(models.Upload).count()

    rv = client.post(
        "/rest_api/v1/uploads",
        data={"report": resource_stream("tests", file_name)},
        headers={
            "access_token": token,
            "Content-Type": "multipart/form-data",
            "Accept": "application/json",
        },
    )

    # Check the request was successful
    assert rv.status_code == 201, f"Failed to upload {file_name}: {rv.json}"

    # Validate the response
    schemas.UploadSchema().validate(rv.json)

    # Check that there is a new Upload
    count_2 = db.session.query(models.Upload).count()
    assert count_2 == count_1 + 1, f"Count did not increase after uploading {file_name}"
