import pytest
from pkg_resources import resource_stream

from megaqc.model import models
from megaqc.rest_api import schemas
from tests import factories


@pytest.fixture()
def report(session):
    r = factories.ReportFactory()
    session.add(r)
    session.commit()
    return r
