# -*- coding: utf-8 -*-
"""Factories to help in tests."""
<<<<<<< HEAD
import json

from factory import PostGenerationMethodCall, Sequence, Faker, SubFactory, RelatedFactoryList
=======
from factory import PostGenerationMethodCall, Sequence, Faker, SubFactory, RelatedFactory, RelatedFactoryList, \
    SelfAttribute
>>>>>>> Finish tests for build_filter_query
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice

from megaqc.database import db
from megaqc.model import models
from megaqc.user.models import User


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class SubFactoryList(SubFactory):
    """Calls a factory 'size' times before the object has been generated.

    Attributes:
        factory (Factory): the factory to call "size-times"
        defaults (dict): extra declarations for calling the related factory
        factory_related_name (str): the name to use to refer to the generated
            object when calling the related factory
        size (int|lambda): the number of times 'factory' is called, ultimately
            returning a list of 'factory' objects w/ size 'size'.
    """

    def __init__(self, factory, size=2, **defaults):
        self.size = size
        super(SubFactoryList, self).__init__(factory, **defaults)

    def generate(self, *args, **kwargs):
        return [
            super(SubFactoryList, self).generate(*args, **kwargs)
            for i in range(self.size if isinstance(self.size, int) else self.size())
        ]


class UserFactory(BaseFactory):
    """User factory."""

    username = Faker('user_name')
    email = Sequence(lambda n: '{}@example.com'.format(n))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True
    first_name = Faker('first_name')
    salt = Faker('md5')
    last_name = Faker('last_name')
    created_at = Faker('date_time')
    api_token = Faker('md5')
    is_admin = False

    class Meta:
        """Factory configuration."""

        model = User


class ReportMetaFactory(BaseFactory):
    class Meta:
        model = models.ReportMeta

<<<<<<< HEAD
    report_meta_key = Faker('word')
    report_meta_value = Faker('pystr')

    report = SubFactory('tests.factories.ReportFactory')


class UploadFactory(BaseFactory):
    class Meta:
        model = models.Upload

    status = Faker('word')
    path = Faker('file_path')
    message = Faker('sentence')
    created_at = Faker('date_time')
    modified_at = Faker('date_time')

    user = SubFactory(UserFactory)

=======
    report_meta_id = Faker('pyint')
    report_meta_key = Faker('word')
    report_meta_value = Faker('pystr')

>>>>>>> Finish tests for build_filter_query

class ReportFactory(BaseFactory):
    class Meta:
        model = models.Report

<<<<<<< HEAD
=======
    # report_id = Faker('pyint')
>>>>>>> Finish tests for build_filter_query
    report_hash = Faker('sha1')
    created_at = Faker('date_time')
    uploaded_at = Faker('date_time')

<<<<<<< HEAD
    user = SubFactory(UserFactory)
=======
    # user = SubFactory(UserFactory)
>>>>>>> Finish tests for build_filter_query
    meta = RelatedFactoryList(ReportMetaFactory, 'report', size=3)
    samples = RelatedFactoryList('tests.factories.SampleFactory', 'report', size=3)


class SampleFactory(BaseFactory):
    class Meta:
        model = models.Sample

<<<<<<< HEAD
=======
    # sample_id = Faker('pyint')
>>>>>>> Finish tests for build_filter_query
    sample_name = Faker('word')

    report = SubFactory(ReportFactory, samples=[])
    data = RelatedFactoryList('tests.factories.SampleDataFactory', 'sample')


class SampleDataTypeFactory(BaseFactory):
    class Meta:
        model = models.SampleDataType

<<<<<<< HEAD
=======
    sample_data_type_id = Faker('pyint')
>>>>>>> Finish tests for build_filter_query
    data_section = Faker('word')
    data_key = Faker('word')


class SampleDataFactory(BaseFactory):
    class Meta:
        model = models.SampleData

<<<<<<< HEAD
    value = Faker('pyint')

    sample = SubFactory(SampleFactory, data=[])
    data_type = SubFactory(SampleDataTypeFactory)


class SampleFilterFactory(BaseFactory):
    class Meta:
        model = models.SampleFilter

    sample_filter_tag = Faker('word')
    sample_filter_name = Faker('word')
    is_public = Faker('pybool')
    sample_filter_data = '[]'
    user = SubFactory(UserFactory)


class FavouritePlotFactory(BaseFactory):
    class Meta:
        model = models.PlotFavourite

    title = Faker('word')
    description = Faker('sentence')
    plot_type = FuzzyChoice([
        'report_plot',
        'distribution',
        'trend',
        'comparison'
    ])
    data = json.dumps({'filter': [], 'fields': []})
    created_at = Faker('date_time')
    user = SubFactory(UserFactory)


class DashboardFactory(BaseFactory):
    class Meta:
        model = models.Dashboard

    title = Faker('word')
    data = json.dumps({})
    is_public = Faker('pybool')
    modified_at = Faker('date_time')
    created_at = Faker('date_time')
=======
    sample_data_id = Faker('pyint')
    value = Faker('pyint')

    # sample = SubFactory(SampleFactory)
    data_type = SubFactory(SampleDataTypeFactory)
>>>>>>> Finish tests for build_filter_query
