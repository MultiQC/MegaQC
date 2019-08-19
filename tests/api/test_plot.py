from flask import url_for
from plotly.offline import plot
import json

from tests import factories


def test_get_trend_series(db, client):
    # Create 5 reports each with 1 sample. Each has a single field called 'test_field'
    data_type = factories.SampleDataTypeFactory()
    report = factories.ReportFactory.create_batch(5, samples__data__data_type=data_type)
    db.session.add_all(report)
    db.session.commit()

    response = client.get(url_for('rest_api.trend_data', filter=json.dumps([]), fields=json.dumps([data_type.data_key])))

    # Check the request was successful
    assert response.status_code == 200

    # Check that there are 3 series (mean, stdev, raw data)
    assert len(response.json) == 3

    # Test that this is valid plot data
    plot({'data': response.json}, validate=True, auto_open=False)
