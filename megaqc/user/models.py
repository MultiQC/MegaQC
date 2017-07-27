# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, ForeignKey, Column, Boolean, Integer, Float, String, TIMESTAMP, Binary, DateTime

from megaqc.database import CRUDMixin
from megaqc.extensions import db

from passlib.hash import argon2
from passlib.utils import getrandstr, rng

import string


class Role(db.Model, CRUDMixin):
    """A role for a user."""

    __tablename__ = 'roles'
    role_id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship('User', backref='roles')

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)


class User(db.Model, CRUDMixin):
    """A user of the app."""

    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(80), unique=True, nullable=False)
    salt = Column(String(80), nullable=True)
    password = Column(Binary(128), nullable=True)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)
    active = Column(Boolean(), default=False)
    is_admin = Column(Boolean(), default=False)
    api_token = Column(String(80), nullable=True)

    def __init__(self, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)
        self.salt = getrandstr(rng, string.digits+string.letters, 80)
        self.api_token = getrandstr(rng, string.digits+string.letters, 80)
        if password:
            self.set_password(password)
        else:
            self.password = None


        if self.user_id == 1:
            self.is_admin = True

    def reset_password(self):
        password = getrandstr(rng, string.digits+string.letters, 10)
        self.set_password(password)
        return password

    def set_password(self, password):
        """Set password."""
        self.password = argon2.using(rounds=4).hash(password+self.salt)

    def check_password(self, value):
        """Check password."""
        return argon2.verify(value+self.salt, self.password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def get_id(self):
        #must return unicode
        return unicode(self.user_id)


    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)
