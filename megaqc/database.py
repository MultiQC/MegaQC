# -*- coding: utf-8 -*-
"""
Database module, including the SQLAlchemy database object and DB-related
utilities.
"""
from builtins import object

from past.builtins import basestring
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

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
            create_engine(url).connect().close()
        except:
            print("Initializing the postgres user and db")
            engine = create_engine("postgres://postgres@localhost:5432/postgres")
            conn = engine.connect()
            conn.execute("commit")
            conn.execute("CREATE USER megaqc_user;")
            conn.execute("commit")
            conn.execute("CREATE DATABASE megaqc OWNER megaqc_user;")
            conn.execute("commit")
            conn.close()
    else:
        engine = create_engine(url)

    """Initializes the database."""
    db.metadata.bind = engine
    db.metadata.create_all()
    print("Initialized the database.")
