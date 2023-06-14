from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from itertools import cycle
from typing import Any, Collection, Dict, Iterable, Iterator, List, Optional, Tuple

import numpy
import numpy.typing as npt
from numpy import absolute, delete, take, zeros
from plotly.colors import DEFAULT_PLOTLY_COLORS, qualitative
from scipy.stats import f, norm, zscore
from sklearn.covariance import EmpiricalCovariance
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy.orm.query import Query

from megaqc.extensions import db
from megaqc.model import models
from megaqc.model.models import *
from megaqc.rest_api.filters import build_filter_query


def rgb_to_rgba(rgb, alpha):
    """
    Appends an alpha (transparency) value to an RGB string.
    """
    match = re.match(r"rgb\((\d+), (\d+), (\d+)\)", rgb)
    return "rgba({}, {}, {}, {})".format(
        match.group(1), match.group(2), match.group(3), alpha
    )


@dataclass
class DataColumn:
    """
    A processed "column" of data, which corresponds to a single data type and the data
    associated with that.
    """

    name: str
    sample_names: npt.NDArray[numpy.str_]
    x: npt.NDArray[numpy.datetime64]
    y: npt.NDArray[numpy.float_]


def extract_query_data(query: Query, ncol: int) -> Iterable[DataColumn]:
    """
    Converts a query into processed data for manipulation.
    """
    encoder = OneHotEncoder()
    data = query.all()
    for column in zip(*[iter(data)] * (len(data) // ncol)):
        names, data_types, x, y = zip(*column)
        x = numpy.array(x, dtype=datetime)
        try:
            yield DataColumn(
                y=numpy.asarray(y, float),
                x=x,
                name=data_types[0],
                sample_names=numpy.array(names),
            )
        except:
            result = encoder.fit_transform(
                numpy.asarray(y, dtype=numpy.object_).reshape(-1, 1)
            ).toarray()
            transformed_types = encoder.get_feature_names_out(data_types[0:1])
            for y, data_type in zip(result.T, transformed_types):
                yield DataColumn(
                    y=y, name=data_type, x=x, sample_names=numpy.array(names)
                )


# Parameters correspond to fields in
# `TrendInputSchema`
def trend_data(
    fields: Sequence[str],
    filters: List[Optional[SampleFilter]],
    statistic: str,
    plot_prefix: str,
    **kwargs,
) -> Iterator[dict]:
    """
    Returns data suitable for a plotly plot.
    """
    # filter_details = db.session.query(SampleFilter).where(SampleFilter.sample_filter_id.in_(filters))

    colours = cycle(iter(qualitative.Alphabet))
    for i, filter in enumerate(filters):
        prefix = f"{plot_prefix}_{i}"
        # Special case for the None filter, which should return all samples
        subquery = build_filter_query([] if filter is None else filter.filter_json)
        # Choose the columns to select, and further filter it down to samples with the column we want to plot
        query = (
            db.session.query(Sample)
            .join(SampleData, isouter=True)
            .join(SampleDataType, isouter=True)
            .join(Report, Report.report_id == Sample.report_id, isouter=True)
            .with_entities(
                models.Sample.sample_name,
                models.SampleDataType.nice_name,
                models.Report.created_at,
                models.SampleData.value,
            )
            .order_by(
                models.SampleDataType.sample_data_type_id
                # models.Report.created_at.asc(),
            )
            .filter(Sample.sample_id.in_(subquery))
            .distinct()
        )

        args = dict(
            fields=fields,
            query=query,
            colours=colours,
            plot_prefix=prefix,
            filter_name="All Samples" if filter is None else filter.sample_filter_name,
            **kwargs,
        )
        if statistic == "measurement":
            yield from univariate_trend_data(**args)
        elif statistic == "iforest":
            yield from iforest_trend_data(
                **args
            )  # return hotelling_trend_data(fields=fields, query=query, **kwargs)
        else:
            raise ValueError("Invalid transform!")


def maha_distance(y, alpha=0.05):
    cov = EmpiricalCovariance()
    # Calculate the distance according to T-square distribution
    cov.fit(y)
    distance = cov.mahalanobis(y)

    # Calculate the critical value according to the F distribution
    n, p = y.shape
    cri = f.isf(alpha, dfn=p, dfd=n - p)
    t = (p * (n - 1) / (n - p)) * cri

    return distance, t


def iforest_trend_data(
    query: Any,
    fields: Sequence[str],
    plot_prefix: str,
    statistic_options: dict,
    colours: Iterator[str],
    filter_name: str,
) -> Iterator[dict]:
    """
    Yields plotly series for the "Isolation Forest" statistic.
    """
    # Fields can be specified either as type IDs, or as type names
    if fields[0].isdigit():
        query = query.filter(models.SampleDataType.sample_data_type_id.in_(fields))
    else:
        query = query.filter(models.SampleDataType.data_key.in_(fields))

    query_data = list(extract_query_data(query, len(fields)))
    y = numpy.column_stack([column.y for column in query_data])
    x = query_data[0].x
    names = query_data[0].sample_names

    clf = IsolationForest(
        n_estimators=100, contamination=statistic_options["contamination"]
    )
    outliers = clf.fit_predict(y) < 0
    scores = -clf.decision_function(y)
    # line = numpy.repeat(0, n)

    yield dict(
        id=plot_prefix + "_inliers",
        type="scatter",
        text=names,
        hoverinfo="text+x+y",
        x=x[~outliers],
        y=scores[~outliers],
        line=dict(color=next(colours)),
        mode="markers",
        name=f"{filter_name} Inliers",
    )

    yield dict(
        id=plot_prefix + "outliers",
        type="scatter",
        text=names,
        hoverinfo="text+x+y",
        x=x[outliers],
        y=scores[outliers],
        line=dict(color=next(colours)),
        mode="markers",
        name=f"{filter_name} Outliers",
    )


def univariate_trend_data(
    query: Any,
    fields: Sequence[str],
    plot_prefix: str,
    statistic_options: dict,
    colours: Iterator[str],
    filter_name: str,
) -> Iterator[dict]:
    """
    Returns the plot series for the "raw measurement" statistic.
    """
    center_line = statistic_options["center_line"]
    for field in fields:
        # Fields can be specified either as type IDs, or as type names
        if field.isdigit():
            field_query = query.filter(
                models.SampleDataType.sample_data_type_id == field
            )
        else:
            field_query = query.filter(models.SampleDataType.data_key == field)

        # Each dummy variable needs to be a unique series
        for i, column in enumerate(extract_query_data(field_query, 1)):
            # We are only considering 1 field at a time
            colour = next(colours)
            name = f"{column.name} {filter_name}"

            yield dict(
                id=f"{plot_prefix}_raw_{i}_{field}",
                type="scatter",
                text=column.sample_names,
                hoverinfo="text+x+y",
                x=column.x,
                y=column.y,
                line=dict(color=colour),
                mode="markers",
                name=f"{name} Samples",
            )

            # Add the mean
            if center_line == "mean":
                y2 = numpy.repeat(numpy.mean(column.y), len(column.x))
                yield dict(
                    id=f"{plot_prefix}_mean_{i}_{field}",
                    type="scatter",
                    x=column.x,
                    y=y2.tolist(),
                    line=dict(color=colour),
                    mode="lines",
                    name=f"{name} Mean",
                )
            elif center_line == "median":
                y2 = numpy.repeat(numpy.median(column.y), len(column.x))
                yield dict(
                    id=f"{plot_prefix}_median_{i}_{field}",
                    type="scatter",
                    x=column.x,
                    y=y2.tolist(),
                    line=dict(color=colour),
                    mode="lines",
                    name=f"{name} Median",
                )
            else:
                # The user could request control limits without a center line. Assume they
                # want a mean in this case
                y2 = numpy.repeat(numpy.mean(column.y), len(column.x))
