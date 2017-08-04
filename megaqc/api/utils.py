
from datetime import datetime
from megaqc.model.models import *
from megaqc.extensions import db
from sqlalchemy import func

#TODO remove when plot_config.hash is fixed
from passlib.utils import getrandstr, rng
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
                    name=report_data['report_plot_data'][plot]['config']['title'],
                    section=plot,
                    data=config)
            new_plot_config.save()
        else:
            config_id = existing_plot_config.plot_config_id

        for dataset in report_data['report_plot_data'][plot]['datasets']:
            for sample_dict in dataset:
               new_dataset_row = PlotData(plot_data_id=PlotData.get_next_id(),
                                   report_id=report_id,
                                   config_id=config_id,
                                   sample_name=sample_dict['name'],
                                   data=json.dumps(sample_dict['data'])
                            )
               new_dataset_row.save()



