from megaqc.rest_api import schemas
from tests import factories


def test_get_report_meta_list(session, client, token):
    """
    Test the "fake class" report_meta, which has no associated model
    """
    # Create some metadata
    report = factories.ReportFactory.build(meta=[])
    generated = factories.ReportMetaFactory.create_batch(size=2, report=report)
    session.expunge_all()
    session.add_all([*generated, report])

    # Check that it's returned
    rv = client.get('/rest_api/v1/report_meta', headers={'access_token': token})
    assert rv.status_code == 200
    data = schemas.ReportMetaTypeSchema(many=True).load(rv.json)

    created_keys = set([record.report_meta_key for record in generated])
    returned_keys = set([datum['report_meta_key'] for datum in data])

    assert created_keys == returned_keys
