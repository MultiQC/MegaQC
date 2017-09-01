
from datetime import datetime, timedelta
from hashlib import md5
from megaqc.model.models import *
from megaqc.extensions import db
from megaqc.utils import settings
from megaqc.api.constants import comparators, type_to_tables_fields, valid_join_conditions
from sqlalchemy import func, distinct, cast, Numeric
from sqlalchemy.orm import aliased
from sqlalchemy.sql import not_, or_, and_
from collections import defaultdict, OrderedDict

import plotly.offline as py
import plotly.graph_objs as go

import json

def generate_hash(data):
    data.pop("config_creation_date")
    string=json.dumps(data)
    md5er=md5()
    md5er.update(string)
    ret = md5er.hexdigest()
    return ret

def handle_report_data(user, report_data):
    report_id = Report.get_next_id()
    report_hash=generate_hash(report_data)
    if db.session.query(Report).filter(Report.report_hash==report_hash).first():
        return (False, 'Report already uploaded')
    new_report = Report(report_hash=report_hash, user_id=user.user_id)
    new_report.save()

    # Save the user as a report meta value
    # TODO: Replace this with special cases in get_report_metadata_fields()
    user_report_meta = ReportMeta(
                            report_meta_id = ReportMeta.get_next_id(),
                            report_meta_key = 'username',
                            report_meta_value = user.username,
                            report_id = new_report.report_id
                        )
    user_report_meta.save()

    # Get top-level `config_` JSON keys (strings only).
    # eg. config_title / config_short_version / config_creation_date etc
    for key in report_data:
        if key.startswith("config") and not isinstance(report_data[key], list) and not isinstance(report_data[key], dict) and report_data[key]:
            new_meta = ReportMeta(report_meta_id=ReportMeta.get_next_id(), report_meta_key=key, report_meta_value=report_data[key], report_id=new_report.report_id)
            new_meta.save()

    # Save the raw parsed data (stuff that ends up in the multiqc_data directory)
    for s_key in report_data.get('report_saved_raw_data', {}):
        section = s_key.replace('multiqc_', '')
        # Go through each sample
        for s_name in report_data['report_saved_raw_data'][s_key]:
            existing_sample = db.session.query(Sample).filter(Sample.sample_name==s_name).first()
            if existing_sample:
                sample_id = existing_sample.sample_id
            else:
                new_sample=Sample(sample_id=Sample.get_next_id(), sample_name=s_name, report_id=report_id)
                new_sample.save()
                sample_id=new_sample.sample_id

            # Go through each data key
            for d_key in report_data['report_saved_raw_data'][s_key][s_name]:
                # Save / load the data type
                existing_key = db.session.query(SampleDataType).filter(SampleDataType.data_id==d_key).first()
                if not existing_key:
                    new_id = (db.session.query(func.max(SampleDataType.sample_data_type_id)).first()[0] or 0) +1
                    new_type = SampleDataType(
                                    sample_data_type_id=new_id,
                                    data_key="{}__{}".format(section, d_key),
                                    data_section=section,
                                    data_id=d_key
                                )
                    new_type.save()
                    type_id = new_id
                else:
                    type_id = existing_key.sample_data_type_id

                # Save the data value
                new_data_id = (db.session.query(func.max(SampleData.sample_data_id)).first()[0] or 0) + 1
                value = report_data['report_saved_raw_data'][s_key][s_name][d_key]
                new_data = SampleData(
                                sample_data_id=new_data_id,
                                report_id=report_id,
                                sample_data_type_id=type_id,
                                sample_id=sample_id,
                                value=str(value)
                            )
                new_data.save()

    # Save report plot data and configs
    for plot in report_data.get('report_plot_data'):
        #  skip custom plots
        if 'mqc_hcplot_' in plot:
            continue
        # TODO: Add support for scatter / beeswarm / heatmap
        if report_data['report_plot_data'][plot]['plot_type'] not in ["bar_graph", "xy_line"]:
            continue
        # Save the plot config as a JSON string
        config = json.dumps(report_data['report_plot_data'][plot]['config'])
        for dst_idx, dataset in enumerate(report_data['report_plot_data'][plot]['datasets']):
            try:
                if isinstance(report_data['report_plot_data'][plot]['config']['data_labels'][dst_idx], dict):
                    dataset = report_data['report_plot_data'][plot]['config']['data_labels'][dst_idx]['ylab']
                else:
                    dataset = report_data['report_plot_data'][plot]['config']['data_labels'][dst_idx]
            except KeyError:
                try:
                    dataset = report_data['report_plot_data'][plot]['config']['ylab']
                except KeyError:
                    dataset = report_data['report_plot_data'][plot]['config']['title']
            existing_plot_config = db.session.query(PlotConfig).filter(PlotConfig.config_type==report_data['report_plot_data'][plot]['plot_type'], PlotConfig.config_name==plot, PlotConfig.config_dataset==dataset).first()
            if not existing_plot_config:
                config_id = PlotConfig.get_next_id()
                new_plot_config = PlotConfig(
                    config_id=config_id,
                    config_type = report_data['report_plot_data'][plot]['plot_type'],
                    config_name = plot,
                    config_dataset = dataset,
                    data = config
                )
                new_plot_config.save()
            else:
                config_id = existing_plot_config.config_id

        # Save bar graph data
        if report_data['report_plot_data'][plot]['plot_type'] == "bar_graph":

            for dst_idx, dataset in enumerate(report_data['report_plot_data'][plot]['datasets']):
                for sub_dict in dataset:
                    data_key = sub_dict['name']
                    existing_category = db.session.query(PlotCategory).filter(PlotCategory.category_name==data_key).first()
                    data = json.dumps({x:y for x,y in sub_dict.items() if x != 'data'})
                    if not existing_category:
                        category_id = PlotCategory.get_next_id()
                        existing_category = PlotCategory(
                                                plot_category_id = PlotCategory.get_next_id(),
                                                report_id = report_id,
                                                config_id = config_id,
                                                category_name = data_key,
                                                data = data
                                            )
                        existing_category.save()
                    else:
                        existing_category.data = data
                        existing_category.save()
                        category_id = existing_category.plot_category_id
                    for sa_idx, actual_data in enumerate(sub_dict['data']):
                        existing_sample = db.session.query(Sample).filter(Sample.sample_name==report_data['report_plot_data'][plot]['samples'][dst_idx][sa_idx]).first()
                        if existing_sample:
                            sample_id = existing_sample.sample_id
                        else:
                            new_sample=Sample(sample_id=Sample.get_next_id(), sample_name=sub_dict['name'], report_id=report_id)
                            new_sample.save()
                            sample_id=new_sample.sample_id
                        new_dataset_row = PlotData(plot_data_id=PlotData.get_next_id(),
                                       report_id=report_id,
                                       config_id=config_id,
                                       sample_id=sample_id,
                                       plot_category_id=existing_category.plot_category_id,
                                       data=json.dumps(actual_data)
                                )
                        new_dataset_row.save()

        # Save line plot data
        elif report_data['report_plot_data'][plot]['plot_type'] == "xy_line":
            for dst_idx, dataset in enumerate(report_data['report_plot_data'][plot]['datasets']):
                for sub_dict in dataset:
                    try:
                        data_key = report_data['report_plot_data'][plot]['config']['data_labels'][dst_idx]['ylab']
                    except KeyError:
                        data_key = report_data['report_plot_data'][plot]['config']['ylab']

                    existing_category = db.session.query(PlotCategory).filter(PlotCategory.category_name==data_key).first()
                    data = json.dumps({x:y for x,y in sub_dict.items() if x != 'data'})
                    if not existing_category:
                        category_id = PlotCategory.get_next_id()
                        existing_category = PlotCategory(
                                                plot_category_id = PlotCategory.get_next_id(),
                                                report_id = report_id,
                                                config_id = config_id,
                                                category_name = data_key,
                                                data = data
                                            )
                        existing_category.save()
                    else:
                        existing_category.data = data
                        existing_category.save()
                        category_id = existing_category.plot_category_id

                    for sa_idx, actual_data in enumerate(sub_dict['data']):
                        existing_sample = db.session.query(Sample).filter(Sample.sample_name==sub_dict['name']).first()
                        if existing_sample:
                            sample_id = existing_sample.sample_id
                        else:
                            new_sample=Sample(sample_id=Sample.get_next_id(), sample_name=sub_dict['name'], report_id=report_id)
                            new_sample.save()
                            sample_id=new_sample.sample_id
                        new_dataset_row = PlotData(plot_data_id=PlotData.get_next_id(),
                                       report_id=report_id,
                                       config_id=config_id,
                                       sample_id=sample_id,
                                       plot_category_id=category_id,
                                       data=json.dumps(sub_dict['data'])
                                )
                    new_dataset_row.save()

    # We made it this far - everything must have worked!
    return (True, 'Data upload successful')


def generate_plot(plot_type, sample_names):
    if " -- " in plot_type:
        # Plot type also contains data_key : True for most xy_lines
        plot_type=plot_type.split(" -- ")
        rows = db.session.query(PlotConfig, PlotData, PlotCategory, Sample).join(PlotData).join(PlotCategory).join(Sample).filter(PlotConfig.config_name==plot_type[0],PlotCategory.category_name==plot_type[1],Sample.sample_name.in_(sample_names)).all()
    else:
        rows = db.session.query(PlotConfig, PlotData, PlotCategory, Sample).join(PlotData).join(PlotCategory).join(Sample).filter(PlotConfig.config_name==plot_type,Sample.sample_name.in_(sample_names)).all()

    if len(rows) == 0:
        return '<div class="alert alert-danger">No samples found</div>'

    if rows[0][0].config_type == "bar_graph":
        #not using sets to keep the order
        samples = []
        series = []
        colors = []
        total_per_sample = defaultdict(lambda:0)
        plot_data=defaultdict(lambda:defaultdict(lambda:0))
        plot_data_perc=defaultdict(lambda:defaultdict(lambda:0))
        config = json.loads(rows[-1][0].data)#grab latest config
        for row in rows:
            if row[3].sample_name not in samples:
                samples.append(row[3].sample_name)
            if row[2].category_name not in series:
                series.append(row[2].category_name)
                cat_config = json.loads(row[2].data)
                if 'color' in cat_config:
                    colors.append(cat_config['color'])
            plot_data[row[2].category_name][row[3].sample_name]=float(row[1].data)
            total_per_sample[row[3].sample_name] = total_per_sample[row[3].sample_name] + float(row[1].data) # count total per sample for percentages
        for key in plot_data:
            for sample in plot_data[key]:
                plot_data_perc[key][sample] = 100 * plot_data[key][sample] / total_per_sample[sample]
        plots = []
        if not colors:
            colors = settings.default_plot_colors
        for idx, d in enumerate(series):
            my_trace = go.Bar(
                y = samples,
                x = [plot_data[d][x] for x in samples],
                name = d,
                text = row[3].sample_name,
                orientation = 'h',
                marker = dict(
                    color = colors[idx%(len(colors)+1)],
                    line = dict(
                        color = colors[idx%(len(colors)+1)],
                        width = 3
                    )
                ),
                hoverinfo = 'text+x'
            )
            if config.get('tt_percentages', True) is False: #default is True
                my_trace.text=['{:.2f}%'.format(plot_data[d][x]/total_per_sample[x] * 100) for x in samples]
            plots.append(my_trace)

        for idx, d in enumerate(series):
            my_trace = go.Bar(
                y = samples,
                x = [plot_data_perc[d][x] for x in samples],
                name = d,
                text = row[3].sample_name,
                orientation = 'h',
                visible = False,
                marker = dict(
                    color = colors[idx%11],#there are 10 defaults
                    line = dict(
                        color = colors[idx%11],
                        width = 3)
                ),
                hoverinfo = 'text+x'
            )
            if config.get('tt_percentages', True) is False: #default is True
                my_trace.text=['{:.2f}%'.format(plot_data[d][x]/total_per_sample[x] * 100) for x in samples]
            plots.append(my_trace)

        updated_layout = config_translate(
            'bar_graph',
            config,
            len(series),
            go.Layout(
                barmode='stack',
                hovermode = 'closest',
                height = 500,
                margin = dict(
                    t = 80,
                    b = 80,
                    l = 80,
                    r = 40
                )
            )
        )
        fig = go.Figure(data=plots, layout=updated_layout)
        plot_div = py.plot(
            fig,
            output_type='div',
            show_link = False,
            config = dict(
                modeBarButtonsToRemove = [
                    'sendDataToCloud',
                    'resetScale2d',
                    'hoverClosestCartesian',
                    'hoverCompareCartesian',
                    'toggleSpikelines'
                ],
                displaylogo = False
            )
        )
        return plot_div

    elif rows[0][0].config_type == "xy_line":
        plots = []
        config = json.loads(rows[-1][0].data) # grab latest config
        for idx, row in enumerate(rows):
            xs = []
            ys = []
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
            line_color = settings.default_plot_colors[ idx % len(settings.default_plot_colors) ]
            plots.append(go.Scatter(
                y = ys,
                x = xs,
                name = row[3].sample_name,
                text = row[3].sample_name,
                mode = 'lines',
                marker = dict(
                    color = line_color,
                    line = dict(
                        color = line_color,
                        width = 1
                    )
                ),
                hoverinfo = 'text'
            ))
        updated_layout = config_translate(
            'xy_line',
            config,
            len(rows),
            go.Layout(
                xaxis = {'type': 'category'},
                showlegend = False,
                hovermode = 'closest',
                height = 500,
                margin = dict(
                    t = 80,
                    b = 80,
                    l = 80,
                    r = 40
                )
            )
        )
        fig = go.Figure(data=plots, layout=updated_layout)
        plot_div = py.plot(
            fig,
            output_type = 'div',
            show_link = False,
            config = dict(
                modeBarButtonsToRemove = [
                    'sendDataToCloud',
                    'resetScale2d',
                    'hoverClosestCartesian',
                    'hoverCompareCartesian',
                    'toggleSpikelines'
                ],
                displaylogo = False
            )
        )
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
        # for stacked bar graphs, axes are reversed Plotly
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
            # Treat them as shapes
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

def get_samples(filters=None, count=False, ids=False):
    if not filters:
        filters=[]
    if count:
        sample_query = db.session.query(func.count(distinct(Sample.sample_name)))
        sample_query = build_filter(sample_query, filters, Sample)
        return sample_query.one()[0]
    elif ids:
        sample_query = db.session.query(distinct(Sample.sample_id))
        sample_query = build_filter(sample_query, filters, Sample)
        samples = [x[0] for x in sample_query.all()]
        return samples
    else:
        sample_query = db.session.query(distinct(Sample.sample_name))
        sample_query = build_filter(sample_query, filters, Sample)
        samples = [x[0] for x in sample_query.all()]
        return samples

def get_report_metadata_fields(filters=None):
    if not filters:
        filters=[]
    report_metadata_query = db.session.query(distinct(ReportMeta.report_meta_key)).join(Report)
    report_metadata_query = build_filter(report_metadata_query, filters, Report)
    return [row[0] for row in report_metadata_query.all()]

def get_sample_metadata_fields(filters=None):
    if not filters:
        filters=[]
    sample_metadata_query = db.session.query(distinct(SampleDataType.data_key), SampleDataType.data_section).join(SampleData)
    sample_metadata_query = build_filter(sample_metadata_query, filters, SampleData)
    sample_fields = []
    for row in sample_metadata_query.all():
        if settings.sample_metadata_fields.get(row[0], {}).get('hidden', False):
            continue
        # Generate a default nice name (can be overwritten by config below)
        nicename = row[0][len(row[1]):] if row[0].startswith(row[1]) else row[0]
        nice_section = row[1].title() if row[1].islower() else row[1]
        nicename = "{0}: {1}".format(nice_section.replace('_', ' '), nicename.replace('_', ' '))
        sample_fields.append({
            'key': row[0],
            'section': row[1],
            'nicename': settings.report_metadata_fields.get(row[0], {}).get('nicename', nicename),
            'priority': settings.report_metadata_fields.get(row[0], {}).get('priority', 1)
        })

    # Sort alphabetically, then by section and then overwrite with priority if given
    sample_fields.sort(key=lambda x: x['nicename'].lower())
    sample_fields.sort(key=lambda x: x['section'])
    sample_fields.sort(key=lambda x: x['priority'], reverse=True)
    return sample_fields

def get_plot_types(filters=None):
    if not filters:
        filters=[]
    pt_query = db.session.query(distinct(PlotConfig.config_name),PlotConfig.config_dataset, PlotConfig.data, PlotConfig.config_type).join(PlotCategory).join(PlotData)
    pt_query = build_filter(pt_query, filters, PlotData)
    plot_types=[]
    for row in pt_query.all():
        if row[3]=='xy_line':
            plot_type_obj={
                'name': '{} -- {}'.format(row[0], row[1]),
                'nicename':json.loads(row[2]).get('title', row[0].replace('_', ' ')),
                'plot_id': row[0],
                'plot_ds_name': row[1],
                'type': 'linegraph'
            }
        elif row[3]=='bar_graph':
            plot_type_obj={
                'name': row[0],
                'nicename':json.loads(row[2]).get('title', row[0].replace('_', ' ')),
                'type':'bargraph'}

        plot_types.append(plot_type_obj)

    plot_types = sorted(plot_types, key=lambda k: k['name'])
    return plot_types

def aggregate_new_parameters(filters=None, short=True):
    if not filters:
        filters=[]

    sample_ids = get_samples(filters, ids=True)
    samples = get_samples(filters)
    if filters:
        new_filters=[[{'type':'sampleids',
                  'cmp':'inlist',
                  'value': sample_ids}]]
    else:
        new_filters=[]

    plot_types  =get_plot_types(new_filters)
    if not short:
        report_field_keys = get_report_metadata_fields(new_filters)
        sample_fields = get_sample_metadata_fields(new_filters)
        return len(samples), report_field_keys, sample_fields, plot_types
    else:
        return len(samples), plot_types


def build_filter(query, filters, source_table):
    #Build sqlalchemy filters for the provided query based on constants and the provided filters
    print filters
    alchemy_or_cmps=[]
    for filter_group in filters:
        alchemy_and_cmps=[]
        for filter_idx, one_filter in enumerate(filter_group):
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
                    try:
                        val=float(one_filter['value'])
                        params=[val]
                    except:
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


            #make named joins
            aliased_fields = []
            current_source=source_table
            current_alias=source_table
            for idx, table in enumerate(type_to_tables_fields[one_filter['type']]):
                aliased_table=aliased(table)
                on_clause =  getattr(current_alias, valid_join_conditions[current_source][table][0]).__eq__(getattr(aliased_table,  valid_join_conditions[current_source][table][1]))
                if idx == 0:
                    query = query.join(aliased_table, on_clause)
                else:
                    query = query.join(aliased_table)

                current_source=table
                current_alias=aliased_table
                for field in type_to_tables_fields[one_filter['type']][table]:
                    aliased_fields.append(getattr(aliased_table, field))

            for idx, param in enumerate(params):
                #field is a db_column
                field = aliased_fields[idx]
                if isinstance(params[idx], float):
                    field=cast(field, Numeric)
                #sql_cmp is a comparison function
                sql_cmp = getattr(field, comparators[cmps[idx]])
                alchemy_and_cmps.append(sql_cmp(param))
        alchemy_or_cmps.append(and_(*alchemy_and_cmps))

    query = query.filter(or_(*alchemy_or_cmps))
    #print query.statement.compile(dialect=db.session.bind.dialect, compile_kwargs={"literal_binds": True})
    return query

def get_user_filters(user):
    clauses=[]
    sfq = db.session.query(SampleFilter)
    clauses.append(SampleFilter.user_id==user.user_id)
    if not user.is_admin:
        clauses.append(SampleFilter.is_public==True)
    sfq.filter(or_(*clauses))
    sfs = sfq.all()
    data=[{'name':x.sample_filter_name,'set':x.sample_filter_tag, 'id':x.sample_filter_id, 'filters':json.loads(x.sample_filter_data)} for x in sfs]
    return data

