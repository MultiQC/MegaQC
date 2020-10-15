import pytest
from flask import request

from tests import factories


@pytest.yield_fixture("function")
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture("function")
def token(db):
    user = factories.UserFactory(is_admin=False)
    db.session.add(user)
    db.session.commit()
    return user.api_token


@pytest.fixture("function")
def admin_token(db):
    user = factories.UserFactory(is_admin=True)
    db.session.add(user)
    db.session.commit()
    return user.api_token
