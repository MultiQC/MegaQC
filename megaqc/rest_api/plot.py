import re

import numpy
from numpy import absolute, delete, take, zeros
from plotly.colors import DEFAULT_PLOTLY_COLORS
from scipy.stats import f, zscore
from sklearn.covariance import EmpiricalCovariance

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


def trend_data(
    fields, filter, line, distance, plot_prefix, control_limits, center_line
):
    """
    Returns data suitable for a plotly plot.
    """
    subquery = build_filter_query(filter)
    plots = []
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
            models.Report.created_at.asc(),
        )
        .filter(Sample.sample_id.in_(subquery))
        .distinct()
    )

    # Fields can be specified either as type IDs, or as type names
    if fields[0].isdigit():
        query = query.filter(models.SampleDataType.sample_data_type_id.in_(fields))
    else:
        query = query.filter(models.SampleDataType.data_key.in_(fields))

    data = query.all()

    names, data_types, x, y = zip(*data)
    data_type = data_types[0]
    names = numpy.asarray(names, dtype=str)
    x = numpy.asarray(x)
    y = numpy.asarray(y, dtype=float)

    plots.append(
        dict(
            id="inliers",
            type="scatter",
            text=names,
            hoverinfo="text+x+y",
            x=x[distance < line],
            y=distance[distance < line],
            line=dict(color="rgb(0,0,250)"),
            mode="markers",
            name="Inliers",
        )
    )

    plots.append(
        dict(
            id="outliers",
            type="scatter",
            text=names,
            hoverinfo="text+x+y",
            x=x[distance > line],
            y=distance[distance > line],
            line=dict(color="rgb(250,0,0)"),
            mode="markers",
            name="Outliers",
        )
    )

    plots.append(
        dict(
            id="plot_line",
            type="scatter",
            hoverinfo="text+x+y",
            x=x.tolist(),
            y=line,
            line=dict(color="rgb(250,0,0)"),
            mode="lines",
            name="Criticial line",
        )
    )

    return plots


def cal_distance(fields):
    cov = EmpiricalCovariance()
    y = y.reshape(-1, len(fields))

    # Calculate the distance according to T-square distribution
    cov.fit(y)
    distance = cov.mahalanobis(y)

    # Calculate the critical value according to the F distribution
    n, p = y.shape
    cri = f.isf(0.05, dfn=p, dfd=n - p)
    t = (p * (n - 1) / (n - p)) * cri
    line = numpy.repeat(t, n)
