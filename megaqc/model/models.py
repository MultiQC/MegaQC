# -*- coding: utf-8 -*-
import datetime as dt

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, ForeignKey, Column, Boolean, Integer, Float, String, TIMESTAMP, Binary, DateTime, func

from megaqc.database import CRUDMixin
from megaqc.extensions import db

class Report(db.Model, CRUDMixin):
    """a MultiQC report"""

    __tablename__ = 'report'
    report_id = Column(Integer, primary_key=True)
    title = Column(String(80), unique=True, nullable=False)
    hash = Column(String(80), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    @staticmethod
    def get_next_id():
        return (db.session.query(func.max(Report.report_id)).first()[0] or 0) + 1

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Report({title!r})>'.format(title=self.title)




class ReportMeta(db.Model, CRUDMixin):
    __tablename__ =  'report_meta'
    report_meta_id = Column(Integer, primary_key=True)
    report_meta_key = Column(String(80), nullable=False)
    report_meta_value = Column(String(80), nullable=False)
    report_id = Column(Integer, ForeignKey('report.report_id'))

class  PlotConfig(db.Model, CRUDMixin):
    __tablename__ =  'plot_config'
    config_id = Column(Integer, primary_key=True)
    config_hash = Column(String(80), unique=True, nullable=False)
    name = Column(String(80),  nullable=False)
    section = Column(String(80), nullable=False)
    data = Column(String(80), nullable=False)

class PlotData(db.Model, CRUDMixin):
    __tablename__ = "plot_data"
    plot_data_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'))
    config_id = Column(Integer, ForeignKey('plot_config.config_id'))
    sample_name = Column(String(80), unique=True, nullable=False)
    data = Column(String(2048), nullable=False)

    @staticmethod
    def get_next_id():
        return (db.session.query(func.max(PlotData.plot_data_id)).first()[0] or 0) + 1

class SampleDataConfig(db.Model, CRUDMixin):
    __tablename__ = "sample_data_config"
    sample_data_config_id = Column(Integer, primary_key=True)
    sample_data_config_value = Column(String(2048), nullable=False)

class SampleDataType(db.Model, CRUDMixin):
    __tablename__ = "sample_data_type"
    sample_data_type_id = Column(Integer, primary_key=True)
    data_id = Column(Integer)
    data_section = Column(String(80))
    data_key = Column(String(80), nullable=False) 

class SampleData(db.Model, CRUDMixin):
    __tablename__ = "sample_data"
    sample_data_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'))
    sample_data_type_id = Column(Integer, ForeignKey('sample_data_type.sample_data_type_id'))
    data_config_id = Column(Integer, ForeignKey('sample_data_config.sample_data_config_id'))
    sample_name = Column(String(80))
    value = Column(String(80))

    @staticmethod
    def get_next_id():
        return (db.session.query(func.max(SampleData.sample_data_id)).first()[0] or 0) + 1


