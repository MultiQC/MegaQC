import re

import numpy
from megaqc.extensions import db
from megaqc.model import models
from megaqc.model.models import *
from megaqc.rest_api.filters import build_filter_query
from numpy import absolute, delete, take, zeros
from plotly.colors import DEFAULT_PLOTLY_COLORS
from scipy.stats import zscore


def rgb_to_rgba(rgb, alpha):
    """
    Appends an alpha (transparency) value to an RGB string.
    """
    match = re.match(r"rgb\((\d+), (\d+), (\d+)\)", rgb)
    return "rgba({}, {}, {}, {})".format(
        match.group(1), match.group(2), match.group(3), alpha
    )


def trend_data(fields, filter, plot_prefix, control_limits, center_line):
    """
    Returns data suitable for a plotly plot.
    """
    subquery = build_filter_query(filter)
    plots = []
    for field, colour in zip(fields, DEFAULT_PLOTLY_COLORS):

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
            .order_by(models.Report.created_at.asc(),)
            .filter(Sample.sample_id.in_(subquery))
            .distinct()
        )

        # Fields can be specified either as type IDs, or as type names
        if field.isdigit():
            query = query.filter(models.SampleDataType.sample_data_type_id == field)
        else:
            query = query.filter(models.SampleDataType.data_key == field)

        data = query.all()

        # If the query returned nothing, skip this field
        if len(data) == 0:
            break

        names, data_types, x, y = zip(*data)
        data_type = data_types[0]
        names = numpy.asarray(names, dtype=str)
        x = numpy.asarray(x)
        y = numpy.asarray(y, dtype=float)

        # Anything outside the control limits is an outlier
        outliers = absolute(zscore(y)) > control_limits["sigma"]
        inliers = ~outliers

        # Add the outliers
        plots.append(
            dict(
                id=plot_prefix + "_outlier_" + field,
                type="scatter",
                text=names[outliers],
                hoverinfo="text+x+y",
                x=x[outliers],
                y=y[outliers],
                line=dict(color="rgb(250,0,0)"),
                mode="markers",
                name="{} Outliers".format(data_type),
            )
        )

        # Add the non-outliers
        plots.append(
            dict(
                id=plot_prefix + "_raw_" + field,
                type="scatter",
                text=names[inliers],
                hoverinfo="text+x+y",
                x=x[inliers],
                y=y[inliers],
                line=dict(color=colour),
                mode="markers",
                name="{} Samples".format(data_type),
            )
        )

        # Add the mean
        if center_line == "mean":
            y2 = numpy.repeat(numpy.mean(y), len(x))
            plots.append(
                dict(
                    id=plot_prefix + "_mean_" + field,
                    type="scatter",
                    x=x,
                    y=y2.tolist(),
                    line=dict(color=colour),
                    mode="lines",
                    name="{} Mean".format(data_type),
                )
            )
        elif center_line == "median":
            y2 = numpy.repeat(numpy.median(y), len(x))
            plots.append(
                dict(
                    id=plot_prefix + "_median_" + field,
                    type="scatter",
                    x=x,
                    y=y2.tolist(),
                    line=dict(color=colour),
                    mode="lines",
                    name="{} Median".format(data_type),
                )
            )
        else:
            # The user could request control limits without a center line. Assume they
            # want a mean in this case
            y2 = numpy.repeat(numpy.mean(y), len(x))

        # Add the stdev
        if control_limits["enabled"]:
            x3 = numpy.concatenate((x, numpy.flip(x, axis=0)))
            stdev = numpy.repeat(numpy.std(y) * control_limits["sigma"], len(x))
            upper = y2 + stdev
            lower = y2 - stdev
            y3 = numpy.concatenate((lower, upper))
            plots.append(
                dict(
                    id=plot_prefix + "_stdev_" + field,
                    type="scatter",
                    x=x3.tolist(),
                    y=y3.tolist(),
                    fill="tozerox",
                    fillcolor=rgb_to_rgba(colour, 0.5),
                    line=dict(color="rgba(255,255,255,0)"),
                    name="{} Control Limits".format(data_type),
                )
            )

    return plots
