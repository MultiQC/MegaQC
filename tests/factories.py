# -*- coding: utf-8 -*-
"""
Factories to help in tests.
"""
import json
from functools import partial
from typing import Any, Callable, Dict, Optional, Type, Union

from factory import (
    Factory,
    Faker,
    PostGenerationMethodCall,
    RelatedFactoryList,
    SelfAttribute,
    Sequence,
    SubFactory,
)
from factory.alchemy import SQLAlchemyModelFactory
from factory.builder import BuildStep, Resolver
from factory.fuzzy import FuzzyChoice

from megaqc.database import db
from megaqc.model import models
from megaqc.user.models import User


class SubFactoryList(SubFactory):
    """
    Calls a factory 'size' times while generating an object.

    Copied from: https://github.com/FactoryBoy/factory_boy/issues/823#issuecomment-932400478

    Attributes:
        factory (fb.Factory): the factory to call "size-times"
        size (int|Callable[[], int]): the number of times 'factory' is called, ultimately returning a list of 'factory' objects w/ size 'size'.
    """

    def __init__(
        self,
        factory: Type[Factory],
        size: Union[int, Callable[[], int]] = 2,
        **kwargs: Optional[Any],
    ) -> None:
        if callable(size):
            size = size()

        self.size = size

        into: Type = kwargs.get("into", list)
        if into not in (list, tuple, set):
            into = list

        self.into = into

        super(SubFactoryList, self).__init__(factory, **kwargs)

    def evaluate(
        self,
        instance: Resolver,
        step: BuildStep,
        extra: Dict[str, Optional[Any]],
    ) -> Sequence:
        """
        Evaluate the current definition and fill its attributes.

        Args:
            instance: The object holding currently computed attributes
            step: a factory.builder.BuildStep
            extra: additional, call-time added kwargs for the step.
        """
        evaluator = partial(super(SubFactoryList, self).evaluate, instance, step, extra)

        return self.into((evaluator() for _ in range(self.size)))


class BaseFactory(SQLAlchemyModelFactory):
    """
    Base factory.
    """

    class Meta:
        """
        Factory configuration.
        """

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """
    User factory.
    """

    # user_id = Faker('pyint')
    username = Faker("user_name")
    email = Sequence(lambda n: "{}@example.com".format(n))
    password = PostGenerationMethodCall("set_password", "example")
    active = True
    first_name = Faker("first_name")
    salt = Faker("md5")
    last_name = Faker("last_name")
    created_at = Faker("date_time")
    api_token = Faker("md5")
    is_admin = False

    class Meta:
        """
        Factory configuration.
        """

        model = User


class ReportMetaFactory(BaseFactory):
    class Meta:
        model = models.ReportMeta

    # report_meta_id = Faker('pyint')
    report_meta_key = Faker("word")
    report_meta_value = Faker("pystr")

    report = SubFactory("tests.factories.ReportFactory")


class UploadFactory(BaseFactory):
    class Meta:
        model = models.Upload

    # upload_id = Faker('pyint')
    status = Faker("word")
    path = Faker("file_path")
    message = Faker("sentence")
    created_at = Faker("date_time")
    modified_at = Faker("date_time")

    user = SubFactory(UserFactory)


class ReportFactory(BaseFactory):
    class Meta:
        model = models.Report

    # report_id = Faker('pyint')
    report_hash = Faker("sha1")
    created_at = Faker("date_time")
    uploaded_at = Faker("date_time")

    user = SubFactory(UserFactory)
    meta = SubFactoryList(ReportMetaFactory, size=3, report=None)
    samples = SubFactoryList("tests.factories.SampleFactory", size=3, report=None)
    # samples = RelatedFactoryList('tests.factories.SampleFactory', 'report', size=3)


class SampleFactory(BaseFactory):
    class Meta:
        model = models.Sample

    # sample_id = Faker('pyint')
    sample_name = Faker("word")

    report = SubFactory(ReportFactory, samples=[])
    # data = SubFactoryList('tests.factories.SampleDataFactory', report=SelfAttribute('..report'))
    data = SubFactoryList("tests.factories.SampleDataFactory", report=None)


class SampleDataTypeFactory(BaseFactory):
    class Meta:
        model = models.SampleDataType

    # sample_data_type_id = Faker('pyint')
    data_section = Faker("word")
    data_key = Faker("word")


class SampleDataFactory(BaseFactory):
    class Meta:
        model = models.SampleData

    # sample_data_id = Faker('pyint')
    value = Faker("pyint")

    report = SubFactory(ReportFactory, samples=[])
    sample = SubFactory(SampleFactory, data=[])
    data_type = SubFactory(SampleDataTypeFactory)


class SampleFilterFactory(BaseFactory):
    class Meta:
        model = models.SampleFilter

    # sample_filter_id = Faker('pyint')
    sample_filter_tag = Faker("word")
    sample_filter_name = Faker("word")
    is_public = Faker("pybool")
    sample_filter_data = "[]"
    user = SubFactory(UserFactory)


class FavouritePlotFactory(BaseFactory):
    class Meta:
        model = models.PlotFavourite

    # plot_favourite_id = Faker('pyint')
    title = Faker("word")
    description = Faker("sentence")
    plot_type = FuzzyChoice(["report_plot", "distribution", "trend", "comparison"])
    data = json.dumps({"filter": [], "fields": []})
    created_at = Faker("date_time")
    user = SubFactory(UserFactory)


class DashboardFactory(BaseFactory):
    class Meta:
        model = models.Dashboard

    # dashboard_id = Faker('pyint')
    title = Faker("word")
    data = json.dumps({})
    is_public = Faker("pybool")
    modified_at = Faker("date_time")
    created_at = Faker("date_time")

    user = SubFactory(UserFactory)
