# -*- coding: utf-8 -*-
"""
Defines fixtures available to all tests.
"""

from pathlib import Path

import pytest
from webtest import TestApp

from megaqc.app import create_app
from megaqc.database import db as _db
from megaqc.database import init_db
from megaqc.settings import TestConfig

from .factories import UserFactory


@pytest.yield_fixture(scope="function")
def multiqc_data():
    here = Path(__file__).parent
    with (here / "multiqc_data.json").open() as fp:
        return fp.read()


@pytest.yield_fixture(scope="function")
def app():
    """
    An application for the tests.
    """
    config = TestConfig()
    _app = create_app(config)
    ctx = _app.test_request_context()
    ctx.push()
    init_db(config.SQLALCHEMY_DATABASE_URI)

    yield _app

    ctx.pop()


@pytest.fixture(scope="function")
def testapp(app):
    """
    A Webtest app.
    """
    return TestApp(app)


@pytest.yield_fixture(scope="function")
def db(app):
    """
    A database for the tests.
    """
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """
    A user for the tests.
    """
    user = UserFactory(password="myprecious")
    db.session.commit()
    return user
