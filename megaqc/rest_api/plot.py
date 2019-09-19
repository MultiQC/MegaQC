from megaqc.model import models
from megaqc.rest_api.filters import build_filter_query
import numpy


def trend_data(fields, filters, plot_prefix):
    """
    Returns data suitable for a plotly plot
    """
    query = build_filter_query(filters)
    plots = []
    for field in fields:

        # Choose the columns to select, and further filter it down to samples with the column we want to plot
        query = query.with_entities(
            models.Sample.sample_name,
            models.SampleDataType.data_key,
            models.Report.created_at,
            models.SampleData.value
        ).order_by(
            models.Report.created_at.asc(),
        ).distinct()

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
        names = numpy.asarray(names, dtype=str)
        x = numpy.asarray(x)
        y = numpy.asarray(y, dtype=float)

        # Add the raw data
        plots.append(dict(
            id=plot_prefix + '_raw_' + field,
            type='scatter',
            text=names,
            hoverinfo='text+x+y',
            x=x,
            y=y,
            line=dict(color='rgb(250,0,0)'),
            mode='markers',
            name='Raw Data'
        ))

        # Add the mean
        y2 = numpy.repeat(numpy.mean(y), len(x))
        plots.append(dict(
            id=plot_prefix + '_mean_' + field,
            type='scatter',
            x=x,
            y=y2.tolist(),
            line=dict(color='rgb(0,100,80)'),
            mode='lines',
            name='Mean'
        ))

        # Add the stdev
        x3 = numpy.concatenate((x, numpy.flip(x, axis=0)))
        stdev = numpy.repeat(numpy.std(y), len(x))
        upper = y2 + stdev
        lower = y2 - stdev
        y3 = numpy.concatenate((lower, upper))
        plots.append(dict(
            id=plot_prefix + '_stdev_' + field,
            type='scatter',
            x=x3.tolist(),
            y=y3.tolist(),
            fill='tozerox',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Standard Deviation'
        ))

    return plots
