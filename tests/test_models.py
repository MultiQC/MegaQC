# -*- coding: utf-8 -*-
"""
Model unit tests.
"""
import datetime as dt

import pytest

from megaqc.user.models import Role, User

from .factories import UserFactory


@pytest.mark.usefixtures("db")
class TestUser:
    """
    User tests.
    """

    def test_created_at_defaults_to_datetime(self):
        """
        Test creation date.
        """
        user = User(username="foo", email="foo@bar.com")
        user.save()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self):
        """
        Test null password.
        """
        user = User(username="foo", email="foo@bar.com")
        user.save()
        assert user.password is None

    def test_factory(self, db):
        """
        Test user factory.
        """
        user = UserFactory(password="myprecious")
        db.session.commit()
        assert bool(user.username)
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.is_admin is False
        assert user.active is True
        assert user.check_password("myprecious")

    def test_check_password(self):
        """
        Check password.
        """
        user = User.create(username="foo", email="foo@bar.com", password="foobarbaz123")
        assert user.check_password("foobarbaz123") is True
        assert user.check_password("barfoobaz") is False

    def test_full_name(self):
        """
        User full name.
        """
        user = UserFactory(first_name="Foo", last_name="Bar")
        assert user.full_name == "Foo Bar"

    def test_roles(self):
        """
        Add a role to a user.
        """
        role = Role(name="admin")
        role.save()
        user = UserFactory()
        user.roles.append(role)
        user.save()
        assert role in user.roles


@pytest.mark.parametrize("strict", [True, False])
def test_active_inactive(session, strict, app):
    """
    The first user to register should be an activated admin, and subsequent
    users should be inactive and regular users.
    """
    app.config["USER_REGISTRATION_APPROVAL"] = strict

    first = User.create(username="foo", email="foo@foo.com", password="foobarbaz123")
    second = User.create(username="bar", email="bar@bar.com", password="foobarbaz123")

    # The first user should always be an active admin
    assert first.active
    assert first.is_admin

    # The second and subsequent users should be active only if it's not in strict mode
    assert second.active != strict
    assert not second.is_admin
