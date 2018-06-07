# -*- coding: utf-8 -*-
import datetime as dt

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, ForeignKey, Column, Boolean, Integer, Float, String, TIMESTAMP, Binary, DateTime, func

from megaqc.database import CRUDMixin
from megaqc.extensions import db


user_plotconfig_map = db.Table('user_plotconfig_map',
            db.Column('user_id', Integer, db.ForeignKey('users.user_id')),
            db.Column('plot_config_id', Integer, db.ForeignKey('plot_config.config_id'))
            )

user_sampletype_map = db.Table('user_sampletype_map',
            db.Column('user_id', Integer, db.ForeignKey('users.user_id')),
            db.Column('sample_data_type_id', Integer, db.ForeignKey('sample_data_type.sample_data_type_id'))
            )

class Report(db.Model, CRUDMixin):
    """a MultiQC report"""

    __tablename__ = 'report'
    report_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    report_hash = Column(String, index=True)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    uploaded_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Report({rid!r})>'.format(rid=self.report_id)


class ReportMeta(db.Model, CRUDMixin):
    __tablename__ = 'report_meta'
    report_meta_id = Column(Integer, primary_key=True)
    report_meta_key = Column(String(80), nullable=False)
    report_meta_value = Column(String(1024), nullable=False)
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)


class PlotConfig(db.Model, CRUDMixin):
    __tablename__ = 'plot_config'
    config_id = Column(Integer, primary_key=True)
    config_type = Column(String(80),  nullable=False)
    config_name = Column(String(80), nullable=False)
    config_dataset = Column(String(80), nullable=True)
    data = Column(String, nullable=False)

    fav_users = db.relationship('User', secondary=user_plotconfig_map, backref="favourite_plotconfigs")


class PlotData(db.Model, CRUDMixin):
    __tablename__ = "plot_data"
    plot_data_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)
    config_id = Column(Integer, ForeignKey('plot_config.config_id'))
    plot_category_id = Column(Integer(), ForeignKey('plot_category.plot_category_id'))
    sample_id = Column(Integer, ForeignKey('sample.sample_id'), index=True)
    data = Column(String, nullable=False)


class PlotCategory(db.Model, CRUDMixin):
    __tablename__ = "plot_category"
    plot_category_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'))
    config_id = Column(Integer, ForeignKey('plot_config.config_id'))
    category_name = Column(String(128), nullable=True)
    data = Column(String(2048), nullable=False)


class PlotFavourite(db.Model, CRUDMixin):
    __tablename__ = "plot_favourite"
    plot_favourite_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    title = Column(String(2048), nullable=False)
    description = Column(String(2048), nullable=True)
    plot_type = Column(String(128), nullable=False)
    data = Column(String(2048), nullable=False)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)


class Dashboard(db.Model, CRUDMixin):
    __tablename__ = "dashboard"
    dashboard_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    title = Column(String(2048), nullable=False)
    data = Column(String(2048), nullable=False)
    is_public = Column(Boolean, default=False, index=True)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)


class SampleDataType(db.Model, CRUDMixin):
    __tablename__ = "sample_data_type"
    sample_data_type_id = Column(Integer, primary_key=True)
    data_id = Column(String(128))
    data_section = Column(String(80))
    data_key = Column(String(128), nullable=False)

class SampleData(db.Model, CRUDMixin):
    __tablename__ = "sample_data"
    sample_data_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)
    sample_data_type_id = Column(Integer, ForeignKey('sample_data_type.sample_data_type_id'))
    sample_id = Column(Integer, ForeignKey('sample.sample_id'), index=True)
    value = Column(String(1024))


class Sample(db.Model, CRUDMixin):
    __tablename__ = "sample"
    sample_id = Column(Integer, primary_key=True)
    sample_name = Column(String(80))
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)


class SampleFilter(db.Model, CRUDMixin):
    __tablename__ = "sample_filter"
    sample_filter_id = Column(Integer, primary_key=True)
    sample_filter_name = Column(String(80))
    sample_filter_tag = Column(String(80))
    is_public = Column(Boolean, index=True)
    sample_filter_data = Column(String(2048), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)


class Upload(db.Model, CRUDMixin):
    __tablename__ = "uploads"
    upload_id = Column(Integer, primary_key=True)
    status = Column(String(80), index=True)
    path = Column(String(2048))
    message = Column(String(2048))
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.user_id'))
