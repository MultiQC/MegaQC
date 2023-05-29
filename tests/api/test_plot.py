import json

from flask import url_for
from marshmallow.utils import EXCLUDE
from plotly.offline import plot

from megaqc.rest_api.schemas import TrendSchema
from tests import factories


def test_trend_data_measurement(db, client):
    # Create 5 reports each with 1 sample. Each has a single field called 'test_field'
    data_type = factories.SampleDataTypeFactory()
    report = factories.ReportFactory.create_batch(5, samples__data__data_type=data_type)
    db.session.add_all(report)
    db.session.commit()

    url = url_for(
        "rest_api.trend_data",
        **{
            "filter": json.dumps([]),
            "fields": json.dumps([data_type.data_key]),
            "statistic": "measurement",
            "statistic_options[center_line]": "mean",
        },
    )
    response = client.get(url, headers={"Content-Type": "application/json"})

    # Check the request was successful
    assert (
        response.status_code == 200
    ), f"Status code {response.status_code}, full response: {response.json}"

    # unknown=EXCLUDE ensures we don't keep the ID field when we load at this point
    data = TrendSchema(many=True, unknown=EXCLUDE).load(response.json)

    # Check that there are 2 series (mean, raw data)
    assert len(data) == 2

    # Test that this is valid plot data
    plot({"data": data}, validate=True, auto_open=False)


def test_trend_data_iforest(db, client):
    # Create 5 reports each with 1 sample. Each has a single field called 'test_field'
    data_type = factories.SampleDataTypeFactory()
    report = factories.ReportFactory.create_batch(5, samples__data__data_type=data_type)
    db.session.add_all(report)
    db.session.commit()

    url = url_for(
        "rest_api.trend_data",
        **{
            "filter": json.dumps([]),
            "fields": json.dumps([data_type.data_key]),
            "statistic": "iforest",
            "statistic_options[contamination]": "0.01",
        },
    )
    response = client.get(url, headers={"Content-Type": "application/json"})

    # Check the request was successful
    assert (
        response.status_code == 200
    ), f"Status code {response.status_code}, full response: {response.json}"

    # unknown=EXCLUDE ensures we don't keep the ID field when we load at this point
    data = TrendSchema(many=True, unknown=EXCLUDE).load(response.json)

    # Check that there are 3 series (mean, inlier, outlier)
    assert len(data) == 2

    # Test that this is valid plot data
    plot({"data": data}, validate=True, auto_open=False)
