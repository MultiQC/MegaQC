# -*- coding: utf-8 -*-
import datetime as dt

from sqlalchemy import event
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, ForeignKey, Column, Boolean, Integer, Float, Unicode, TIMESTAMP, Binary, DateTime, func
from sqlalchemy import JSON
import enum

from megaqc.database import CRUDMixin
from megaqc.extensions import db

import megaqc.api.utils

user_plotconfig_map = db.Table('user_plotconfig_map',
                               db.Column('user_id', Integer, db.ForeignKey('users.user_id')),
                               db.Column('plot_config_id', Integer, db.ForeignKey('plot_config.config_id'))
                               )

user_sampletype_map = db.Table('user_sampletype_map',
                               db.Column('user_id', Integer, db.ForeignKey('users.user_id')),
                               db.Column('sample_data_type_id', Integer,
                                         db.ForeignKey('sample_data_type.sample_data_type_id'))
                               )


class Report(db.Model, CRUDMixin):
    """a MultiQC report"""

    __tablename__ = 'report'
    report_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    report_hash = Column(Unicode, index=True, unique=True)
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
    report_meta_key = Column(Unicode, nullable=False)
    report_meta_value = Column(Unicode, nullable=False)
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)


class PlotConfig(db.Model, CRUDMixin):
    __tablename__ = 'plot_config'
    config_id = Column(Integer, primary_key=True)
    config_type = Column(Unicode, nullable=False)
    config_name = Column(Unicode, nullable=False)
    config_dataset = Column(Unicode, nullable=True)
    data = Column(Unicode, nullable=False)

    fav_users = db.relationship('User', secondary=user_plotconfig_map, backref="favourite_plotconfigs")


class PlotData(db.Model, CRUDMixin):
    __tablename__ = "plot_data"
    plot_data_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)
    config_id = Column(Integer, ForeignKey('plot_config.config_id'))
    plot_category_id = Column(Integer(), ForeignKey('plot_category.plot_category_id'))
    sample_id = Column(Integer, ForeignKey('sample.sample_id'), index=True)
    data = Column(Unicode, nullable=False)


class PlotCategory(db.Model, CRUDMixin):
    __tablename__ = "plot_category"
    plot_category_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'))
    config_id = Column(Integer, ForeignKey('plot_config.config_id'))
    category_name = Column(Unicode, nullable=True)
    data = Column(Unicode, nullable=False)


class PlotFavourite(db.Model, CRUDMixin):
    __tablename__ = "plot_favourite"
    plot_favourite_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    title = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=True)
    plot_type = Column(Unicode, nullable=False)
    data = Column(Unicode, nullable=False)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)


class Dashboard(db.Model, CRUDMixin):
    __tablename__ = "dashboard"
    dashboard_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    title = Column(Unicode, nullable=False)
    data = Column(Unicode, nullable=False)
    is_public = Column(Boolean, default=False, index=True)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)


class SampleDataType(db.Model, CRUDMixin):
    __tablename__ = "sample_data_type"
    sample_data_type_id = Column(Integer, primary_key=True)
    data_id = Column(Unicode)
    data_section = Column(Unicode)
    data_key = Column(Unicode, nullable=False)


class SampleData(db.Model, CRUDMixin):
    __tablename__ = "sample_data"
    sample_data_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)
    sample_data_type_id = Column(Integer, ForeignKey('sample_data_type.sample_data_type_id'))
    sample_id = Column(Integer, ForeignKey('sample.sample_id'), index=True)
    value = Column(Unicode)


class Sample(db.Model, CRUDMixin):
    __tablename__ = "sample"
    sample_id = Column(Integer, primary_key=True)
    sample_name = Column(Unicode)
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)

    alerts = relationship("Alert", back_populates='sample')

    def generate_alerts(self):
        """
        Triggers any alerts that should be created by the creation of this sample
        """

        # This is awful and the sample filtering should be done in the database
        sample_alerts = [alert for alert in db.session.query(AlertThreshold).all() if alert.sample_id == self.sample_id]
        db.session.bulk_save_objects(sample_alerts)


@event.listens_for(Sample, 'after_insert')
def new_alert_threshold(mapper, connection, target: Sample):
    """
    Whenever a Sample is inserted into the DB, create Alerts for it
    """
    target.generate_alerts()


class SampleFilter(db.Model, CRUDMixin):
    __tablename__ = "sample_filter"
    sample_filter_id = Column(Integer, primary_key=True)
    sample_filter_name = Column(Unicode)
    sample_filter_tag = Column(Unicode)
    is_public = Column(Boolean, index=True)
    sample_filter_data = Column(Unicode, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)


class Upload(db.Model, CRUDMixin):
    __tablename__ = "uploads"
    upload_id = Column(Integer, primary_key=True)
    status = Column(Unicode, index=True)
    path = Column(Unicode)
    message = Column(Unicode)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.user_id'))


class AlertThreshold(db.Model, CRUDMixin):
    __tablename__ = "alert_threshold"
    alert_threshold_id = Column(Integer, primary_key=True)
    threshold = Column(JSON)
    name = Column(Unicode)
    description = Column(Unicode)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    importance = Column(Integer)

    alerts = relationship("Alert", back_populates='threshold')

    def calculate_alerts(self):
        """
        Triggers any Alerts that should be created by the creation of this alert
        """
        samples = megaqc.api.utils.get_samples(self.threshold)
        alerts = [Alert(sample=sample, threshold=self, message='') for sample in samples]
        return alerts

    def generate_alerts(self):
        """
        Creates any Alerts that should be created by the creation of this alert
        """
        db.session.bulk_save_objects(self.calculate_alerts())


@event.listens_for(AlertThreshold, 'after_insert')
def new_alert_threshold(mapper, connection, target: AlertThreshold):
    """
    Whenever an AlertThreshold is inserted into the DB, create Alerts for it
    """
    target.generate_alerts()


class Alert(db.Model, CRUDMixin):
    __tablename__ = "alert"
    alert_id = Column(Integer, primary_key=True)
    alert_threshold_id = Column(Integer, ForeignKey('alert_threshold.alert_threshold_id'), index=True)
    sample_id = Column(Integer, ForeignKey('sample.sample_id'), index=True)
    message = Column(Unicode)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)

    threshold = relationship("AlertThreshold", back_populates='alerts')
    sample = relationship("Sample", back_populates='alerts')
