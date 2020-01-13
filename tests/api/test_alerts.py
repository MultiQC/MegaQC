"""
Generic tests for normal resources that follow a schema for GET, POST, DELETE etc
"""
import pytest
from megaqc.model import models


@pytest.fixture()
def gc_threshold():
    return models.AlertThreshold(
        threshold=[
            [
                {
                    'type': 'samplemeta',
                    'key': 'gc_content',
                    'cmp': 'lt',
                    'value': '60'
                }
            ]
        ],
        name="gc_content",
        importance=1
    )


@pytest.fixture()
def report():
    return models.Report()


@pytest.fixture()
def good_sample(report, good_gc_point):
    return models.Sample(
        report=report,
        data=[
            good_gc_point,
        ]
    )

@pytest.fixture()
def bad_sample(report, bad_gc_point):
    return models.Sample(
        report=report,
        data=[
            bad_gc_point,
        ]
    )

@pytest.fixture()
def samples(good_sample, bad_sample):
    return good_sample, bad_sample

@pytest.fixture()
def gc_type():
    return models.SampleDataType(
        data_key='gc_content',
        data_section='fastqc'
    )


@pytest.fixture()
def good_gc_point(gc_type, report):
    return models.SampleData(
        value=41,
        data_type=gc_type,
        report=report
    )


@pytest.fixture()
def bad_gc_point(gc_type, report):
    return models.SampleData(
        value=99,
        data_type=gc_type,
        report=report
    )


def test_alert_sample_before_threshold(session, samples, gc_threshold):
    """
    Tests the creation of a sample and then later a threshold. The hooks should
    automatically create alerts
    """
    assert session.query(models.Alert).count() == 0
    session.add_all(samples)
    session.commit()

    assert session.query(models.Alert).count() == 0
    session.add(gc_threshold)
    session.commit()

    # The alert should only exist when both the threshold and the sample is in the
    # database at the same time
    assert session.query(models.Alert).count() == 1


def test_alert_threshold_before_sample(session, samples, gc_threshold):
    """
    Tests the creation of an alert threshold and then a sample. The hooks should
    automatically create alerts
    """
    assert session.query(models.Alert).count() == 0
    session.add(gc_threshold)
    session.commit()

    assert session.query(models.Alert).count() == 0
    session.add_all(samples)
    session.commit()

    # The alert should only exist when both the threshold and the sample is in the
    # database at the same time
    assert session.query(models.Alert).count() == 1
