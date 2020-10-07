import datetime
import itertools

import pytest

from megaqc.model import models
from megaqc.rest_api.filters import DATE_FORMAT, build_filter_query
from tests import factories


def unique(result, column):
    """
    Returns all unique values of the given column.

    :param result: The return value of an SQLAlchemy query()
    :param column: The column to find unique values for
    """
    return set([getattr(row, column) for row in result])


@pytest.fixture()
def filter_test_types(session):
    types = [
        factories.SampleDataTypeFactory.build(data_key="field_1"),
        factories.SampleDataTypeFactory.build(data_key="field_2"),
    ]
    session.add_all(types)
    session.commit()
    return types


@pytest.fixture()
def filter_test_reports(filter_test_types, session):
    types = filter_test_types

    # Constructing test data manually, rather than using factories because of:
    # https://github.com/FactoryBoy/factory_boy/issues/636
    ret = [
        factories.ReportFactory(
            # models.Report(
            created_at=datetime.datetime.now() - datetime.timedelta(days=1),
            samples=[factories.SampleFactory(data=[])],
            meta=[
                factories.ReportMetaFactory.build(
                    report_meta_key="key_1", report_meta_value="1", report=None
                ),
                factories.ReportMetaFactory.build(
                    report_meta_key="key_2", report_meta_value=1, report=None
                ),
            ],
        ),
        # models.Report(
        factories.ReportFactory(
            created_at=datetime.datetime.now() - datetime.timedelta(days=2),
            samples=[factories.SampleFactory(data=[])],
            meta=[
                factories.ReportMetaFactory.build(
                    report_meta_key="key_1", report_meta_value="2", report=None
                ),
                factories.ReportMetaFactory.build(
                    report_meta_key="key_2", report_meta_value=2, report=None
                ),
            ],
        ),
        # models.Report(
        factories.ReportFactory(
            created_at=datetime.datetime.now() - datetime.timedelta(days=3),
            samples=[factories.SampleFactory(data=[])],
            meta=[
                factories.ReportMetaFactory.build(
                    report_meta_key="key_1", report_meta_value="3", report=None
                ),
                factories.ReportMetaFactory.build(
                    report_meta_key="key_2", report_meta_value=3, report=None
                ),
            ],
        ),
    ]

    words = ["aardvark", "badger", "caboose", "dachshund", "eagle"]
    for i, report in enumerate(ret):
        report.samples[0].data = [
            factories.SampleDataFactory.build(
                data_type=types[0], value=i + 1, report=report
            ),
            factories.SampleDataFactory.build(
                data_type=types[1], value=words[i], report=report
            ),
        ]

    session.expunge_all()
    session.add_all(ret)
    session.commit()
    return ret


def test_daterange_in(filter_test_reports):
    # Finds all samples uploaded in the last 2 days
    query = build_filter_query(
        [
            [
                {
                    "type": "daterange",
                    "value": [
                        (datetime.datetime.now() - datetime.timedelta(days=2)).strftime(
                            DATE_FORMAT
                        ),
                        (datetime.datetime.now()).strftime(DATE_FORMAT),
                    ],
                    "cmp": "in",
                }
            ]
        ]
    )
    for report in filter_test_reports:
        print(len(report.samples))
    data = (
        query.with_entities(
            models.Report.created_at,
            models.SampleData.value,
            models.Sample.sample_id,
            models.Report.report_id,
        )
        .group_by(models.Sample.sample_id)
        .all()
    )

    # This should return 2 samples
    assert len(unique(data, "sample_id")) == 2

    # These samples should come from only 2 reports
    reports = unique(data, "report_id")
    assert len(reports) == 2

    # Specifically, it should be the first two reports that are returned
    assert filter_test_reports[0].report_id in reports
    assert filter_test_reports[1].report_id in reports


def test_daterange_not_in(filter_test_reports):
    # Finds all samples uploaded in the last 2 days
    query = build_filter_query(
        [
            [
                {
                    "type": "daterange",
                    "value": [
                        (datetime.datetime.now() - datetime.timedelta(days=2)).strftime(
                            DATE_FORMAT
                        ),
                        (datetime.datetime.now()).strftime(DATE_FORMAT),
                    ],
                    "cmp": "not in",
                }
            ]
        ]
    )
    data = (
        query.with_entities(
            models.Report.created_at,
            models.SampleData.value,
            models.Sample.sample_id,
            models.Report.report_id,
        )
        .group_by(models.Sample.sample_id)
        .all()
    )

    # This should return 1 sample
    assert len(unique(data, "sample_id")) == 1

    # These samples should come from only 1 reports
    reports = unique(data, "report_id")
    assert len(reports) == 1

    # Specifically, it should be the last report that is returned
    assert filter_test_reports[2].report_id in reports


def test_timedelta_in(filter_test_reports):
    # Finds all samples uploaded in the last 2 days
    query = build_filter_query([[{"type": "timedelta", "value": [2], "cmp": "in"}]])
    data = query.with_entities(
        models.Report.created_at,
        models.SampleData.value,
        models.Sample.sample_id,
        models.Report.report_id,
    ).all()

    # This should return 2 samples
    assert len(unique(data, "sample_id")) == 2

    # These samples should come from only 2 reports
    reports = unique(data, "report_id")
    assert len(reports) == 2

    # Specifically, it should be the first two reports that are returned
    assert filter_test_reports[0].report_id in reports
    assert filter_test_reports[1].report_id in reports


def test_timedelta_not_in(filter_test_reports):
    # Finds all samples uploaded in the last 2 days, but using timedelta
    query = build_filter_query([[{"type": "timedelta", "value": [2], "cmp": "not in"}]])
    data = query.with_entities(
        models.Report.created_at,
        models.SampleData.value,
        models.Sample.sample_id,
        models.Report.report_id,
    ).all()

    # This should return 1 sample
    assert len(unique(data, "sample_id")) == 1

    # These samples should come from only 1 reports
    reports = unique(data, "report_id")
    assert len(reports) == 1

    # Specifically, it should be the last report that is returned
    assert filter_test_reports[2].report_id in reports


@pytest.mark.parametrize(
    ["meta_key", "value"],
    itertools.product(
        # Test this using a string meta property, and an integer meta property
        ["key_1", "key_2"],
        # Likewise, test the value using a string and an integer
        [2, "2"],
    ),
)
def test_reportmeta_equals(filter_test_reports, meta_key, value):
    # db.session.add_all(filter_test_reports)

    # Finds all samples that have a certain metadata key
    query = build_filter_query(
        [[{"type": "reportmeta", "key": meta_key, "value": [value], "cmp": "eq"}]]
    )
    data = query.with_entities(
        models.Report.created_at,
        models.SampleData.value,
        models.Sample.sample_id,
        models.Report.report_id,
    ).all()

    # We should get one report
    reports = unique(data, "report_id")
    assert len(reports) == 1

    # We should get one sample
    samples = unique(data, "sample_id")
    assert len(samples) == 1

    # And that one sample should be the second sample
    assert reports.pop() == filter_test_reports[1].report_id


def test_reportmeta_not_equals(filter_test_reports):
    # Finds all samples that don't have a certain metadata key
    query = build_filter_query(
        [[{"type": "reportmeta", "key": "key_1", "value": [2], "cmp": "ne"}]]
    )
    data = query.with_entities(
        models.Report.created_at,
        models.SampleData.value,
        models.Sample.sample_id,
        models.Report.report_id,
    ).all()

    # We should get two reports
    reports = unique(data, "report_id")
    assert len(reports) == 2

    # We should get two samples
    samples = unique(data, "sample_id")
    assert len(samples) == 2

    # And neither sample should be sample 2
    for report in data:
        assert report.report_id != filter_test_reports[1].report_id


# Use the "cmp" operator to compare the value with the number 2, and then assert that the array of report IDs is
# equal to the "correct" array
@pytest.mark.parametrize(
    ["cmp", "value", "correct", "data_type"],
    [
        ["eq", 2, [1], 0],
        ["ne", 2, [0, 2], 0],
        ["le", 2, [0, 1], 0],
        ["lt", 2, [0], 0],
        ["ge", 2, [1, 2], 0],
        ["gt", 2, [2], 0],
        ["gt", 2, [2], 0],
        ["like", "%ardv%", [0], 1],
        ["like", "%", [0, 1, 2], 1],
        ["contains", "ardv", [0], 1],
        ["contains", "%ardv%", [], 1],
        ["startswith", "aard", [0], 1],
        ["startswith", "bad", [1], 1],
        ["endswith", "vark", [0], 1],
        ["endswith", "ger", [1], 1],
        ["notlike", "%ardv%", [1, 2], 1],
        ["notlike", "%", [], 1],
        ["notcontains", "ardv", [1, 2], 1],
        ["notcontains", "%ardv%", [0, 1, 2], 1],
        ["notstartswith", "aard", [1, 2], 1],
        ["notstartswith", "bad", [0, 2], 1],
        ["notendswith", "vark", [1, 2], 1],
        ["notendswith", "ger", [0, 2], 1],
    ],
)
def test_samplemeta_operator(
    filter_test_reports, filter_test_types, cmp, value, correct, data_type
):
    """
    Tests all comparison operators, and the samplemeta filter.
    """
    # Finds all samples that have less than 2 for some value
    query = build_filter_query(
        [
            [
                {
                    "type": "samplemeta",
                    "key": filter_test_types[data_type].data_key,
                    "value": [value],
                    "cmp": cmp,
                }
            ]
        ]
    )
    data = query.with_entities(
        models.Report.created_at,
        models.SampleData.value,
        models.Sample.sample_id,
        models.Report.report_id,
    ).all()

    # We should get the right number of reports
    reports = unique(data, "report_id")
    assert len(reports) == len(correct)

    # We should get two samples
    samples = unique(data, "sample_id")
    assert len(samples) == len(correct)

    # And the sample should be sample 1
    for sample in correct:
        assert filter_test_reports[sample].report_id in reports


def test_and_query(filter_test_types, filter_test_reports):
    """
    Find the intersections of two queries.
    """

    # Finds all samples that have greater than 1 for some sample value, AND greater than 2 for some report metadata
    query = build_filter_query(
        [
            [
                {
                    "type": "samplemeta",
                    "key": filter_test_types[0].data_key,
                    "value": [1],
                    "cmp": "gt",
                },
                {"type": "reportmeta", "key": "key_1", "value": [2], "cmp": "gt"},
            ]
        ]
    )
    data = query.with_entities(
        models.Report.created_at,
        models.SampleData.value,
        models.Sample.sample_id,
        models.Report.report_id,
    ).all()

    # We should get two reports
    reports = unique(data, "report_id")
    assert len(reports) == 1

    # We should get two samples
    samples = unique(data, "sample_id")
    assert len(samples) == 1

    # And the sample returned should be the third sample
    assert filter_test_reports[2].report_id in reports


def test_or_query(filter_test_types, filter_test_reports):
    """
    Find the intersections of two queries.
    """

    # Finds all samples that have greater than 2 for some sample value, OR less than 2 for some report metadata
    query = build_filter_query(
        [
            [
                {
                    "type": "samplemeta",
                    "key": filter_test_types[0].data_key,
                    "value": [2],
                    "cmp": "gt",
                },
            ],
            [{"type": "reportmeta", "key": "key_1", "value": [2], "cmp": "lt"}],
        ]
    )
    data = query.with_entities(
        models.Report.created_at,
        models.SampleData.value,
        models.Sample.sample_id,
        models.Report.report_id,
    ).all()

    # We should get two reports
    reports = unique(data, "report_id")
    assert len(reports) == 2

    # We should get two samples
    samples = unique(data, "sample_id")
    assert len(samples) == 2

    # And the sample returned should not be the second sample
    assert filter_test_reports[1].report_id not in reports
