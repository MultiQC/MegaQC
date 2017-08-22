
from datetime import datetime, timedelta
from megaqc.model.models import *
from megaqc.extensions import db
from megaqc.utils import settings
from megaqc.api.constants import comparators, type_to_fields
from sqlalchemy import func, distinct
from sqlalchemy.sql import not_, or_
from collections import defaultdict

import plotly.offline as py
import plotly.graph_objs as go

import json


def handle_report_data(user, report_data):
    report_id = Report.get_next_id()
    new_report = Report(user_id=user.user_id)
    new_report.save()

    # Save the user as a report meta value
    user_report_meta = ReportMeta(report_meta_id=ReportMeta.get_next_id(), report_meta_key='username', report_meta_value=user.username, report_id=new_report.report_id)
    user_report_meta.save()

    for key in report_data:
        if key.startswith("config") and not isinstance(report_data[key], list) and not isinstance(report_data[key], dict):
            new_meta = ReportMeta(report_meta_id=ReportMeta.get_next_id(), report_meta_key=key, report_meta_value=report_data[key], report_id=new_report.report_id)
            new_meta.save()

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
            colors = settings.default_plot_colors
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
                line_color = settings.default_plot_colors[idx%(len(settings.default_plot_colors)+1)]
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

def get_samples(filters=None, count=False):
    if not filters:
        filters=[]
    if count:
        sample_query = db.session.query(func.count(distinct(PlotData.sample_name))).join(Report)
    else:
        sample_query = db.session.query(distinct(PlotData.sample_name)).join(Report)

    sample_query = build_filter(sample_query, filters)
    print sample_query.statement.compile(dialect=db.session.bind.dialect, compile_kwargs={"literal_binds": True})


    if count:
        samples = sample_query.first()[0]
    else:
        samples = sample_query.all()

    return samples

def get_report_metadata_fields(filters=None):
    if not filters:
        filters=[]
    report_metadata_query = db.session.query(distinct(ReportMeta.report_meta_key)).join(Report)
    report_metadata_query = build_filter(report_metadata_query, filters)
    field_keys = [row[0] for row in report_metadata_query.all()]

    # Add a priority and nice name, check in config
    fields = []
    for f in field_keys:
        if settings.report_metadata_fields.get(f, {}).get('hidden', False):
            continue
        fields.append({
            'key': f,
            'nicename': settings.report_metadata_fields.get(f, {}).get('nicename', f.replace('_', ' ')),
            'priority': settings.report_metadata_fields.get(f, {}).get('priority', 1)
        })
    fields = sorted(fields, key=lambda k: k['priority'], reverse=True)

    return fields

def get_sample_metadata_fields(filters=None):
    if not filters:
        filters=[]
    sample_metadata_query = db.session.query(distinct(SampleDataType.data_key), SampleDataType.data_section).join(SampleData).join(Report)
    sample_metadata_query = build_filter(sample_metadata_query, filters)
    fields = [{'key':row[0], 'section':row[1]} for row in sample_metadata_query.all()]
    fields.sort(key=lambda x: x['section'])
    return fields

def get_report_plot_types(filters=None):
    if not filters:
        filters= []
    plot_types = []

    # Get bar graphs
    bg_pt_query = db.session.query(distinct(PlotConfig.section))
    bg_pt_query = build_filter(bg_pt_query, filters)
    bg_pt_query = bg_pt_query.filter(PlotConfig.name == 'bar_graph')
    for row in bg_pt_query.all():
        plot_types.append({
            'name': row[0],
            'type': 'bargraph'
        })

    # Get line graphs
    lg_pt_query = db.session.query(distinct(PlotConfig.section), PlotCategory.category_name).join(PlotCategory)
    lg_pt_query = build_filter(lg_pt_query, filters)
    lg_pt_query = lg_pt_query.filter(PlotConfig.name == 'xy_line')
    for row in lg_pt_query.all():
        plot_types.append({
            'name': '{} -- {}'.format(row[0], row[1]),
            'plot_id': row[0],
            'plot_ds_name': row[1],
            'type': 'linegraph'
        })

    # Sort and return the results
    plot_types = sorted(plot_types, key=lambda k: k['name'], reverse=True)
    return plot_types

def build_filter(query, filters):
    #Build sqlalchemy filters for the provided query based on constants and the provided filters
    alchemy_cmps=[]
    for one_filter in filters:
        params=[]
        cmps=[]
        if one_filter['type'] == 'daterange':
            #daterange : make values actual datetimes
            params = [datetime.strptime(x, "%Y-%m-%d") for x in one_filter['value']]
            params[1] = params[1] + timedelta(1) #right border is midnight, you usually want to include the date you use as right border
            #in and not in are handled by making 2 filters, default is "in"
            if one_filter['cmp'] == "not in":
                cmps=["<=", ">="]
            else:
                cmps=[">=", "<="]

        elif one_filter['type'] == 'date':
            params = [datetime.strptime(one_filter['value'], "%Y-%m-%d")]
            cmps=[one_filter['cmp']]
        elif one_filter['type'] == 'timedelta':
            #timedeltarange : make datetime based on now and reverse the cmp,
            #because time <7 days == time > _date_seven_days_ago
            params = [datetime.now() - timedelta(int(one_filter['value']))]
            if one_filter['cmp'] in ['gt', '>']:
                cmps=['<=']
            elif one_filter['cmp'] in ['lt', '<']:
                cmps=['>=']
            elif one_filter['cmp'] in ['ge', '>=']:
                cmps=['<']
            elif one_filter['cmp'] in ['le', '<=']:
                cmps=['>']
        else:
            #default behaviour
            cmps=[one_filter['cmp']]
            if 'not in' == one_filter['cmp']:
                #not in is a special case, there is no sqlalchemy operator to deal with it, although there is one for "in" and "notlike"
                params=['%{0}%'.format(one_filter['value'])]
            else:
                params=[one_filter['value']]
            key = one_filter.get('key', None)
            if key:
                params.append(key)
                cmps.append("==")
                #if there is a key/value pair, the cmp only applies to the value, the key should be matched
            key = one_filter.get('section', None)
            if one_filter.get('section'):
                params.append(one_filter['section'])
                cmps.append("==")


        for idx, param in enumerate(params):
            #field is a db_column
            field = type_to_fields[one_filter['type']][idx]
            #sql_cmp is a comparison function
            sql_cmp = getattr(field, comparators[cmps[idx]])
            alchemy_cmps.append(sql_cmp(param))
    query = query.filter(*alchemy_cmps)
    return query
