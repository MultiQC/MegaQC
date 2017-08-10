
from datetime import datetime
from megaqc.model.models import *
from megaqc.extensions import db
from sqlalchemy import func
from collections import defaultdict


#TODO remove when plot_config.hash is fixed
from passlib.utils import getrandstr, rng

import colorlover as clv
import plotly.offline as py
import plotly.graph_objs as go

import string
import json


def handle_report_data(user, report_data):
    report_id = (db.session.query(func.max(Report.report_id)).first()[0] or 0) + 1
    report_title = report_data.get('title', "Report_{}".format(datetime.now().strftime("%y%m%d")))
    new_report = Report(report_id=report_id, hash=report_data['config_report_id'], user_id=user.user_id, title=report_title)
    new_report.save()
    #TODO : Add report meta handling

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

            existing_config = db.session.query(SampleDataConfig).filter(SampleDataConfig.sample_data_config_value==config).first()
            if not existing_config:
                new_id = (db.session.query(func.max(SampleDataConfig.sample_data_config_id)).first()[0] or 0) +1
                new_config = SampleDataConfig(sample_data_config_id=new_id,sample_data_config_value=config)
                new_config.save()
                config_id = new_id
            else:
                config_id = existing_config.sample_data_config_id

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
        config =  json.dumps(report_data['report_plot_data'][plot]['config'])
        #TODO figure out config_hash
        existing_plot_config=db.session.query(PlotConfig).filter(PlotConfig.data==config).first()
        if not existing_plot_config:
            config_id = (db.session.query(func.max(PlotConfig.config_id)).first()[0] or 0) +1
            new_plot_config = PlotConfig(config_id=config_id,
                    config_hash=getrandstr(rng, string.digits+string.letters, 10),
                    name=report_data['report_plot_data'][plot]['plot_type'],
                    section=plot,
                    data=config)
            new_plot_config.save()
        else:
            config_id = existing_plot_config.plot_config_id

        if report_data['report_plot_data'][plot]['plot_type']=="bar_graph":

            for dst_idx, dataset in enumerate(report_data['report_plot_data'][plot]['datasets']):
                for sub_dict in dataset:
                    data_key = sub_dict['name']
                    for sa_idx, actual_data in enumerate(sub_dict['data']):
                        new_dataset_row = PlotData(plot_data_id=PlotData.get_next_id(),
                                       report_id=report_id,
                                       config_id=config_id,
                                       sample_name=report_data['report_plot_data'][plot]['samples'][dst_idx][sa_idx],
                                       data_key=sub_dict['name'],
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

                    for sa_idx, actual_data in enumerate(sub_dict['data']):
                       new_dataset_row = PlotData(plot_data_id=PlotData.get_next_id(),
                                       report_id=report_id,
                                       config_id=config_id,
                                       sample_name=sub_dict['name'],
                                       data_key=data_key,
                                       data=json.dumps(sub_dict['data'])
                                )
                    new_dataset_row.save()



def generate_plot(plot_type, sample_names):
    if plot_type == "featureCounts_assignment_plot":
        rows = db.session.query(PlotConfig, PlotData).join(PlotData).filter(PlotConfig.section==plot_type, PlotData.sample_name.in_(sample_names)).all()
        samples = set()
        series = set()
        plot_data=defaultdict(lambda:defaultdict(lambda:0))
        for row in rows:
            samples.add(row[1].sample_name)
            series.add(row[1].data_key)
            plot_data[row[1].data_key][row[1].sample_name]=float(row[1].data)
        samples = list(samples)
        print samples
        plots=[]
        scale_idx=str(min(11, max(3,len(series)))) #colorlover only has scales between 3 and 11
        colors = clv.scales[scale_idx]['div']['RdYlBu']
        for idx, d in enumerate(series):
            my_trace = go.Bar(
                y=samples,
                x=[plot_data[d][x] for x in samples],
                name=d,
                orientation = 'h',
                marker = dict(
                    color = colors[idx%12],
                    line = dict(
                        color = colors[idx%12],
                        width = 3)
                )
            )
            plots.append(my_trace)

        layout = go.Layout(
                barmode='stack'
        )
        fig = go.Figure(data=plots, layout=layout)
        plot_div = py.plot(fig, output_type='div')
        return plot_div
    elif plot_type == "xy_line":
        pass
