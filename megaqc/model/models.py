# -*- coding: utf-8 -*-
import datetime as dt
import json

from sqlalchemy import ForeignKey, Column, Boolean, Integer, Unicode, DateTime, JSON, \
    CheckConstraint, Table, UniqueConstraint
from sqlalchemy import event
from sqlalchemy.orm import relationship

from megaqc.database import CRUDMixin
from megaqc.rest_api.filters import build_filter_query
from megaqc.extensions import db

user_plotconfig_map = db.Table('user_plotconfig_map',
                               db.Column('user_id', Integer,
                                         db.ForeignKey('users.user_id')),
                               db.Column('plot_config_id', Integer,
                                         db.ForeignKey('plot_config.config_id'))
                               )

user_sampletype_map = db.Table('user_sampletype_map',
                               db.Column('user_id', Integer,
                                         db.ForeignKey('users.user_id')),
                               db.Column('sample_data_type_id', Integer,
                                         db.ForeignKey(
                                             'sample_data_type.sample_data_type_id'))
                               )


class Report(db.Model, CRUDMixin):
    """a MultiQC report"""

    __tablename__ = 'report'
    report_id = Column(Integer, primary_key=True)
    # If the user is deleted, we still want to retain the report
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'),
                     index=True)
    report_hash = Column(Unicode, index=True, unique=True)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    uploaded_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)

    user = relationship('User', back_populates='reports')
    meta = relationship('ReportMeta', back_populates='report', passive_deletes='all')
    samples = relationship('Sample', back_populates='report', passive_deletes='all')
    sample_data = relationship('SampleData', back_populates='report',
                               passive_deletes='all')


class ReportMeta(db.Model, CRUDMixin):
    __tablename__ = 'report_meta'
    report_meta_id = Column(Integer, primary_key=True)
    report_meta_key = Column(Unicode, nullable=False)
    report_meta_value = Column(Unicode, nullable=False)
    # If the report is deleted, remove the report metadata
    report_id = Column(Integer, ForeignKey('report.report_id', ondelete='CASCADE'),
                       index=True, nullable=False)

    report = relationship('Report', back_populates='meta')

    @classmethod
    def get_keys(cls, session):
        """
        Returns all unique metadata keys
        """
        return session.query(ReportMeta.report_meta_key).distinct()

    @classmethod
    def get_keys(cls, session):
        """
        Returns all unique metadata keys
        """
        return session.query(ReportMeta.report_meta_key).distinct()


class PlotConfig(db.Model, CRUDMixin):
    __tablename__ = 'plot_config'
    config_id = Column(Integer, primary_key=True)
    config_type = Column(Unicode, nullable=False)
    config_name = Column(Unicode, nullable=False)
    config_dataset = Column(Unicode, nullable=True)
    data = Column(Unicode, nullable=False)

    fav_users = db.relationship('User', secondary=user_plotconfig_map,
                                backref="favourite_plotconfigs")


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

    user = relationship('User', back_populates='favourite_plots')


class Dashboard(db.Model, CRUDMixin):
    __tablename__ = "dashboard"
    dashboard_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    title = Column(Unicode, nullable=False)
    data = Column(Unicode, nullable=False)
    is_public = Column(Boolean, default=False, index=True)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)

    user = relationship('User', back_populates='dashboards')


class SampleDataType(db.Model, CRUDMixin):
    __tablename__ = "sample_data_type"
    sample_data_type_id = Column(Integer, primary_key=True)
    data_id = Column(Unicode)
    data_section = Column(Unicode)
    data_key = Column(Unicode, nullable=False)

    @classmethod
    def get_keys(cls, session):
        """
        Returns all unique metadata keys
        """
        return session.query(SampleDataType.report_meta_key).distinct()

    sample_data = relationship('SampleData', back_populates='data_type')


class SampleData(db.Model, CRUDMixin):
    __tablename__ = "sample_data"
    sample_data_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id', ondelete='CASCADE'),
                       index=True)
    sample_data_type_id = Column(Integer,
                                 ForeignKey('sample_data_type.sample_data_type_id',
                                            ondelete='CASCADE'), nullable=False)
    sample_id = Column(Integer, ForeignKey('sample.sample_id', ondelete='CASCADE'),
                       index=True, nullable=False)
    value = Column(Unicode)

    sample = relationship('Sample', back_populates='data')
    report = relationship('Report', back_populates='sample_data')
    data_type = relationship('SampleDataType', back_populates='sample_data')


alert_sample = Table('alert_sample', db.Model.metadata,
                     Column('alert_id', Integer, ForeignKey('alert.alert_id')),
                     Column('sample_id', Integer, ForeignKey('sample.sample_id')),
                     # The same sample can't be part of the same alert multiple times
                     UniqueConstraint('alert_id', 'sample_id')
                     )


class Sample(db.Model, CRUDMixin):
    __tablename__ = "sample"
    sample_id = Column(Integer, primary_key=True)
    sample_name = Column(Unicode)
    report_id = Column(Integer, ForeignKey('report.report_id', ondelete='CASCADE'),
                       index=True, nullable=False)

    report = relationship('Report', back_populates='samples')
    data = relationship('SampleData', back_populates='sample', passive_deletes='all')

    alerts = relationship("Alert", secondary=alert_sample, back_populates='samples')


class SampleFilter(db.Model, CRUDMixin):
    __tablename__ = "sample_filter"
    sample_filter_id = Column(Integer, primary_key=True)
    sample_filter_name = Column(Unicode)
    sample_filter_tag = Column(Unicode)
    is_public = Column(Boolean, index=True)
    sample_filter_data = Column(Unicode, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)

    user = relationship('User', back_populates='filters')

    @property
    def filter_json(self):
        return json.loads(self.sample_filter_data)


class Upload(db.Model, CRUDMixin):
    __tablename__ = "uploads"
    upload_id = Column(Integer, primary_key=True)
    status = Column(Unicode, index=True)
    path = Column(Unicode)
    message = Column(Unicode)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    user = relationship('User', back_populates='uploads')


class AlertThreshold(db.Model, CRUDMixin):
    __tablename__ = "alert_threshold"
    alert_threshold_id = Column(Integer, primary_key=True)
    threshold = Column(JSON)
    name = Column(Unicode)
    description = Column(Unicode)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    importance = Column(
        Integer,
        CheckConstraint('importance <= 10'),
        CheckConstraint('importance >= 1'),
        doc='A number out of 10 indicating how important this alert is, with 10 being '
            'the highest and 1 being the lowest',
    )

    alerts = relationship("Alert", back_populates='threshold')

    def calculate_alerts(self, filters=[]):
        """
        Triggers any Alerts that should be created by the creation of this alert
        :param filters: A list of filters to apply to the alert query, e.g. in order to
        filter down the list of samples to consider
        """
        query = build_filter_query(self.threshold).with_entities(Sample)
        for filter in filters:
            query = query.filter(filter)
        return [Alert(samples=[sample], threshold=self) for sample in query.all()]

    def generate_alerts(self, filters=[]):
        """
        Creates any Alerts that should be created by the creation of this alert

        :param filters: A list of filters to apply to the alert query, e.g. in order to
        filter down the list of samples to consider
        """
        db.session.add_all(self.calculate_alerts(filters))


class Alert(db.Model, CRUDMixin):
    __tablename__ = "alert"
    alert_id = Column(Integer, primary_key=True)
    alert_threshold_id = Column(Integer, ForeignKey('alert_threshold.alert_threshold_id'),
                                index=True)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)

    threshold = relationship("AlertThreshold", back_populates='alerts')
    # Each alert has many samples because it could be a multi-sample statistical rule
    # that caused the violation, not just a single sample violation
    samples = relationship("Sample", secondary=alert_sample, back_populates='alerts')


@event.listens_for(db.session, 'after_flush')
def on_flush(session, context):
    all = session.dirty.union(session.new)
    new_thresholds = [t for t in all if isinstance(t, AlertThreshold)]
    new_threshold_ids = [t.alert_threshold_id for t in new_thresholds]
    new_samples = [s for s in all if isinstance(s, Sample)]
    new_sample_ids = [s.sample_id for s in new_samples]

    old_thresholds = session.query(AlertThreshold).filter(
        AlertThreshold.alert_threshold_id.notin_(new_threshold_ids)).all()

    # Calculate alerts for all new thresholds
    for threshold in new_thresholds:
        threshold.generate_alerts()

    # See if any old alerts should trigger for the new samples
    for threshold in old_thresholds:
        threshold.generate_alerts(filters=[
            Sample.sample_id.in_(new_sample_ids)
        ])

