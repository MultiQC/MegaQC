# -*- coding: utf-8 -*-
"""
Database module, including the SQLAlchemy database object and DB-related
utilities.
"""
from builtins import object
from copy import copy

from flask_migrate import stamp
from past.builtins import basestring
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError

from .compat import basestring
from .extensions import db

# Alias common SQLAlchemy names
Column = db.Column


class CRUDMixin(object):
    """
    Mixin that adds convenience methods for CRUD (create, read, update, delete)
    operations.
    """

    @classmethod
    def get_or_create(cls, kwargs):
        instance = db.session.query(cls).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            return instance

    @classmethod
    def create(cls, **kwargs):
        """
        Create a new record and save it the database.
        """
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """
        Update specific fields of a record.
        """
        for attr, value in list(kwargs.items()):
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """
        Save the record.
        """
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """
        Remove the record from the database.
        """
        db.session.delete(self)
        return commit and db.session.commit()

    @property
    def primary_key(self):
        return getattr(self, self.__class__.primary_key_name())

    @classmethod
    def primary_key_columns(cls):
        return inspect(cls).primary_key

    @classmethod
    def primary_key_name(cls):
        return cls.primary_key_columns()[0].name


class Model(CRUDMixin, db.Model):
    """
    Base model class that includes CRUD convenience methods.
    """

    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """
    A mixin that adds a surrogate integer 'primary key' column named ``id`` to
    any declarative-mapped class.
    """

    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """
        Get record by ID.
        """
        if any(
            (
                isinstance(record_id, basestring) and record_id.isdigit(),
                isinstance(record_id, (int, float)),
            ),
        ):
            return cls.query.get(int(record_id))
        return None


def init_db(url):
    """
    Initialise a new database.
    """
    if "postgresql" in url:
        try:
            # attempt to connect to an existing database using provided credentials
            engine = create_engine(url)
            engine.connect().close()
        except OperationalError as conn_err:
            # connection failed, so connect to default postgres DB and create new megaqc db and user
            parsed_url = make_url(url)

            # save for megaqc user / DB creation
            config_user = parsed_url.username
            config_pass = parsed_url.password
            config_db = parsed_url.database

            # default db settings
            parsed_url.database = 'postgres'
            parsed_url.username = 'postgres'
            parsed_url.password = None
            default_engine = create_engine(parsed_url)
            conn = default_engine.connect()

            print("Initializing the postgres user and db")
            # create user, using password if given
            create_user_cmd = f"CREATE USER {config_user}"
            if config_pass:
                create_user_cmd += f" WITH ENCRYPTED PASSWORD '{config_pass}'"
            try:
                conn.execute(create_user_cmd)
                print(f"User {config_user} created successfully")
            except ProgrammingError as user_err:
                # it's okay if user already exists
                if not isinstance(user_err.__cause__, DuplicateObject):
                    raise user_err
                print(f"User {config_user} already exists")
                conn.execute("rollback")

            # create database
            conn.execute(f"CREATE DATABASE {config_db} OWNER {config_user}")
            conn.close()
            print("Database created successfully")

            # use engine with newly created db / user, if it fails again something bigger wrong
            engine = create_engine(url)
            engine.connect().close()
    else:
        engine = create_engine(url)

    """Initializes the database."""
    db.metadata.bind = engine
    db.metadata.create_all()
    print("Initialized the database.")
