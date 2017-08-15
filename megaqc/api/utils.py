
from datetime import datetime
from megaqc.model.models import *
from megaqc.extensions import db
from megaqc.utils import multiqc_colors
from sqlalchemy import func
from collections import defaultdict
from math import log



import colorlover as clv
import plotly.offline as py
import plotly.graph_objs as go

import string
import json


def handle_report_data(user, report_data):
    report_id = Report.get_next_id()
    report_title = report_data.get('title', "Report_{}".format(datetime.now().strftime("%y%m%d")))
    new_report = Report(user_id=user.user_id, title=report_title)
    new_report.save()
    for key in report_data:
        if key.startswith("config"):
            new_meta = ReportMeta(report_meta_id=ReportMeta.get_next_id(), report_meta_key=key, report_meta_value=report_data[key], report_id=new_report.report_id)

    for idx, general_headers in enumerate(report_data.get('report_general_stats_headers')):
        for general_header in general_headers:
            data_key = general_header
            config = json.dumps(general_headers[general_header])
            existing_key = db.session.query(SampleDataType).filter(SampleDataType.data_id==general_headers[general_header].get('rid')).first()
            if not existing_key:
                new_id = (db.session.query(func.max(SampleDataType.sample_data_type_id)).first()[0] or 0) +1
                new_type = SampleDataType(sample_data_type_id=new_id,
                                            data_key=data_key,
                                            data_section=general_headers[general_header].get('namespace'),
                                            data_id=general_headers[general_header].get('rid'))
                new_type.save()
                type_id = new_id
            else:
                type_id = existing_key.sample_data_type_id

            new_id = (db.session.query(func.max(SampleDataConfig.sample_data_config_id)).first()[0] or 0) +1
            new_config = SampleDataConfig(sample_data_config_id=new_id,sample_data_config_value=config)
            new_config.save()
            config_id = new_id

            for sample in report_data.get('report_general_stats_data')[idx]:
                new_data_id = (db.session.query(func.max(SampleData.sample_data_id)).first()[0] or 0) +1
                value = report_data.get('report_general_stats_data')[idx][sample][data_key]
                new_data = SampleData(sample_data_id=new_data_id,
                                    report_id=report_id,
                                    sample_data_type_id=type_id,
                                    data_config_id=config_id,
                                    sample_name=sample,
                                    value=str(value))
                new_data.save()


    for plot in report_data.get('report_plot_data'):
        config = json.dumps(report_data['report_plot_data'][plot]['config'])
        existing_plot_config = db.session.query(PlotConfig).filter(PlotConfig.data==config).first()
        if not existing_plot_config:
            config_id = PlotConfig.get_next_id()
        else:
            config_id = existing_plot_config.config_id
        new_plot_config = PlotConfig(config_id=config_id,
                name=report_data['report_plot_data'][plot]['plot_type'],
                section=plot,
                data=config)
        new_plot_config.save()

        if report_data['report_plot_data'][plot]['plot_type']=="bar_graph":

            for dst_idx, dataset in enumerate(report_data['report_plot_data'][plot]['datasets']):
                for sub_dict in dataset:
                    data_key = sub_dict['name']
                    existing_category = db.session.query(PlotCategory).filter(PlotCategory.category_name==data_key).first()
                    if not existing_category:
                        category_id = PlotCategory.get_next_id()
                    else:
                        category_id = existing_category.plot_category_id
                    data=json.dumps({x:y for x,y in sub_dict.items() if x != 'data'})
                    existing_category = PlotCategory(plot_category_id=PlotCategory.get_next_id(),
                                                        report_id=report_id,
                                                        config_id=config_id,
                                                        category_name=data_key,
                                                        data=data)
                    existing_category.save()
                    for sa_idx, actual_data in enumerate(sub_dict['data']):
                        new_dataset_row = PlotData(plot_data_id=PlotData.get_next_id(),
                                       report_id=report_id,
                                       config_id=config_id,
                                       sample_name=report_data['report_plot_data'][plot]['samples'][dst_idx][sa_idx],
                                       plot_category_id=existing_category.plot_category_id,
                                       data=json.dumps(actual_data)
                                )
                        new_dataset_row.save()

        elif report_data['report_plot_data'][plot]['plot_type']=="xy_line":
            for dst_idx, dataset in enumerate(report_data['report_plot_data'][plot]['datasets']):
                for sub_dict in dataset:
                    try:
                        data_key = report_data['report_plot_data'][plot]['config']['data_labels'][dst_idx]['ylab']
                    except KeyError:
                        data_key = report_data['report_plot_data'][plot]['config']['ylab']

                    existing_category = db.session.query(PlotCategory).filter(PlotCategory.category_name==data_key).first()
                    if not existing_category:
                        category_id = PlotCategory.get_next_id()
                    else:
                        category_id = existing_category.plot_category_id
                    data=json.dumps({x:y for x,y in sub_dict.items() if x != 'data'})
                    existing_category = PlotCategory(plot_category_id=PlotCategory.get_next_id(),
                                                    report_id=report_id,
                                                    config_id=config_id,
                                                    category_name=data_key,
                                                    data=data)
                    existing_category.save()

                    for sa_idx, actual_data in enumerate(sub_dict['data']):
                       new_dataset_row = PlotData(plot_data_id=PlotData.get_next_id(),
                                       report_id=report_id,
                                       config_id=config_id,
                                       sample_name=sub_dict['name'],
                                       plot_category_id=existing_category.plot_category_id,
                                       data=json.dumps(sub_dict['data'])
                                )
                    new_dataset_row.save()



def generate_plot(plot_type, sample_names):
    if " -- " in plot_type:
        # Plot type also contains data_key : True for most xy_lines
        plot_type=plot_type.split(" -- ")
        rows = db.session.query(PlotConfig, PlotData, PlotCategory).join(PlotData).join(PlotCategory).filter(PlotConfig.section==plot_type[0],PlotCategory.category_name==plot_type[1],PlotData.sample_name.in_(sample_names)).all()
    else:
        rows = db.session.query(PlotConfig, PlotData, PlotCategory).join(PlotData).join(PlotCategory).filter(PlotConfig.section==plot_type,PlotData.sample_name.in_(sample_names)).all()

    if rows[0][0].name == "bar_graph":
        #not using sets to keep the order
        samples = []
        series = []
        colors = []
        total_per_sample = defaultdict(lambda:0)
        plot_data=defaultdict(lambda:defaultdict(lambda:0))
        plot_data_perc=defaultdict(lambda:defaultdict(lambda:0))
        config = json.loads(rows[-1][0].data)#grab latest config
        for row in rows:
            if row[1].sample_name not in samples:
                samples.append(row[1].sample_name)
            if row[2].category_name not in series:
                series.append(row[2].category_name)
                cat_config = json.loads(row[2].data)
                if 'color' in cat_config:
                    colors.append(cat_config['color'])
            plot_data[row[2].category_name][row[1].sample_name]=float(row[1].data)
            total_per_sample[row[1].sample_name] = total_per_sample[row[1].sample_name] + float(row[1].data) # count total per sample for percentages
        for key in plot_data:
            for sample in plot_data[key]:
                plot_data_perc[key][sample] = 100 * plot_data[key][sample] / total_per_sample[sample]
        plots=[]
        if not colors:
            colors = multiqc_colors()
        for idx, d in enumerate(series):
            my_trace = go.Bar(
                y=samples,
                x=[plot_data[d][x] for x in samples],
                name=d,
                orientation = 'h',
                marker = dict(
                    color = colors[idx%(len(colors)+1)],
                    line = dict(
                        color = colors[idx%(len(colors)+1)],
                        width = 3)
                )
            )
            if config.get('tt_percentages', True) is False: #default is True
                my_trace.text=['{:.2f}%'.format(plot_data[d][x]/total_per_sample[x] * 100) for x in samples]
            plots.append(my_trace)

        for idx, d in enumerate(series):
            my_trace = go.Bar(
                y=samples,
                x=[plot_data_perc[d][x] for x in samples],
                name=d,
                orientation = 'h',
                visible=False,
                marker = dict(
                    color = colors[idx%11],#there are 10 defaults
                    line = dict(
                        color = colors[idx%11],
                        width = 3)
                )
            )
            if config.get('tt_percentages', True) is False: #default is True
                my_trace.text=['{:.2f}%'.format(plot_data[d][x]/total_per_sample[x] * 100) for x in samples]
            plots.append(my_trace)

        layout = go.Layout(
                barmode='stack'
        )
        updated_layout = config_translate('bar_graph', config, len(series), layout )
        fig = go.Figure(data=plots, layout=updated_layout)
        plot_div = py.plot(fig, output_type='div')
        return plot_div

    elif rows[0][0].name == "xy_line":
        plots=[]
        config = json.loads(rows[-1][0].data)#grab latest config
        for idx, row in enumerate(rows):
            xs=[]
            ys=[]
            data = json.loads(row[1].data)
            config = json.loads(row[0].data)
            if "categories" in config:
                for d_idx, d in enumerate(data):
                    xs.append(" "+str(config['categories'][d_idx]))
                    ys.append(d)

            else:
                for d in data:
                    xs.append(d[0])
                    ys.append(d[1])
            category_conf = json.loads(row[2].data)
            if 'color' in category_conf:
                line_color = category_conf['color']
            else:
                line_color = multiqc_colors()[idx%11]
            my_trace = go.Scatter(
                y=ys,
                x=xs,
                name=row[2].category_name,
                mode='lines',
                marker = dict(
                    color = line_color,
                    line = dict(
                        color = line_color,
                        width = 1)
                )
            )
            plots.append(my_trace)
        layout = go.Layout(
                xaxis={'type':'category'} 
            )
        updated_layout = config_translate('xy_line', config, len(rows), layout)
        fig = go.Figure(data=plots, layout=updated_layout)
        plot_div = py.plot(fig, output_type='div')
        return plot_div

def config_translate(plot_type, config, series_nb, plotly_layout=go.Layout()):
    plotly_layout.title = config.get('title')
    xaxis={}
    xaxis['title']=config.get('xlab')
    yaxis={}
    yaxis['title']=config.get('ylab')
    if 'ymin' in config and 'ymax' in config:
        my_range=[float(config['ymin']), float(config['ymax'])]
        if 'logswitch_active' in config:
            my_range = map(math.log, my_range)
    #TODO : Figure out how yfloor and yceiling should be handled
    if plot_type=="bar_graph":
        #for stacked bar graphs, axes are reversed between Highcharts and Plotly
        plotly_layout.yaxis= xaxis
        plotly_layout.xaxis= yaxis

        updatemenus=list([
            dict(
                buttons=list([
                    dict(
                        args=[{'visible': [i<series_nb for i in xrange(series_nb*2)]}],
                        label='Count',
                        method='restyle'
                    ),
                    dict(
                        args=[{'visible': [i>=series_nb for i in xrange(series_nb*2)]}],
                        label='Percentage',
                        method='restyle'
                    )
                ]),
                direction = 'left',
                showactive = True,
                type = 'buttons',
                x = -0.1,
                xanchor = 'left',
                y = -0.1,
                yanchor = 'top'
            ),
        ])
        plotly_layout['updatemenus'] = updatemenus
    elif plot_type=="xy_line":
        plotly_layout.yaxis= yaxis
        plotly_layout.xaxis= xaxis

        if 'xPlotBands' in config:
            #Treat them as shapes
            shapes=[]
            for band in config['xPlotBands']:
                shape = {'type': 'rect',
                        'yref': 'paper',
                        'x0': band['from'],
                        'y0': 0,
                        'x1': band['to'],
                        'y1': 1,
                        'line': {
                            'color': band['color'],
                            'width': 1,
                        },
                        'fillcolor': band['color'],
                        'opacity': 0.5
                        }
                shapes.append(shape)
            plotly_layout.shapes=shapes

        if 'yPlotBands' in config:
            #Treat them as shapes
            shapes=[]
            for band in config['yPlotBands']:
                shape = {'type': 'rect',
                        'xref': 'paper',
                        'x0': 0,
                        'y0': band['from'],
                        'x1': 1,
                        'y1': band['to'],
                        'line': {
                            'color': band['color'],
                            'width': 1,
                        },
                        'fillcolor': band['color'],
                        'opacity': 0.5
                        }
                shapes.append(shape)
            plotly_layout.shapes=shapes

    return plotly_layout
