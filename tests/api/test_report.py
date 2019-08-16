import pytest
from pkg_resources import resource_stream

from megaqc.model import models, schemas
from tests import factories

@pytest.fixture()
def report(session):
    r = factories.ReportFactory()
    session.add(r)
    session.commit()
    return r

def test_get_report_list(report, session, client):
    rv = client.get('/rest_api/v1/reports')

    # Check the request was successful
    assert rv.status_code == 200

    json = rv.json

    # Check we only got 1 report
    assert len(json) == 1

    # And it had the right ID
    assert json[0]['report_id'] == report.report_id

    # Check that the returned data matches the schema
    errors = schemas.ReportSchema(many=True, session=session).validate(json)
    assert len(errors) == 0


def test_post_report_list(db, client, token):
    rv = client.post(
        '/rest_api/v1/reports',
        data={'report': resource_stream('tests', 'multiqc_data.json')},
        headers={'access_token': token}
    )

    # Check the request was successful
    assert rv.status_code == 200

    # Check that there is a new Upload
    uploads = db.session.query(models.Upload).count()
    assert uploads == 1


def test_get_report(session, report, client):
    rv = client.get('/rest_api/v1/reports/{}'.format(report.report_id))

    # Check the request was successful
    assert rv.status_code == 200

    # Check that the returned data matches the schema
    errors = schemas.ReportSchema(many=False, session=session).validate(rv.json)
    assert len(errors) == 0


def test_delete_report(session, report, client, token, admin_token):
    # Check that there is one report
    uploads = session.query(models.Report).count()
    assert uploads == 1

    # Non-logged in users and non-admin users shouldn't be able to delete reports
    assert client.delete('/rest_api/v1/reports/{}'.format(report.report_id)).status_code == 403
    assert client.delete('/rest_api/v1/reports/{}'.format(report.report_id), headers={'access_token': token}).status_code == 403

    rv = client.delete('/rest_api/v1/reports/{}'.format(report.report_id), headers={'access_token': admin_token})

    # Check the request was successful, as an admin
    assert rv.status_code == 200

    # Check that we deleted the report
    uploads = session.query(models.Report).count()
    assert uploads == 0
