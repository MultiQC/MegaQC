import pytest
from tests import factories
from flask import request


@pytest.yield_fixture('function')
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture('function')
def token(db):
    user = factories.UserFactory(is_admin=False)
    db.session.add(user)
    db.session.commit()
    return user.api_token


@pytest.fixture('function')
def admin_token(db):
    user = factories.UserFactory(is_admin=True)
    db.session.add(user)
    db.session.commit()
    return user.api_token


@pytest.fixture()
def session(db):
    sess = db.session
    return sess
