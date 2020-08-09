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


def postgres_create_user(username, conn, cur, password=None):
    """
    Create a postgres user, including a password if provided.
    """
    from psycopg2.sql import Identifier, Placeholder, SQL
    from psycopg2.errors import DuplicateObject, ProgrammingError

    # Run the CREATE USER
    try:
        if password:
            cur.execute(
                SQL("CREATE USER {} WITH ENCRYPTED PASSWORD {}").format(
                    Identifier(username), Placeholder()
                ),
                [password],
            )
        else:
            cur.execute(SQL("CREATE USER {}").format(Identifier(username)))

        print(f"User {username} created successfully")
    except DuplicateObject as e:
        # it's okay if user already exists
        print(f"User {username} already exists")


def postgres_create_database(conn, cur, database, user):
    """
    Create a Postgres database, with the given owner.
    """
    from psycopg2.sql import Identifier, SQL

    # create database
    cur.execute(
        SQL("CREATE DATABASE {} OWNER {}").format(
            Identifier(database), Identifier(user)
        )
    )
    print("Database created successfully")


def init_db(url):
    """
    Initialise a new database.
    """
    if "postgresql" in url:
        try:
            # Attempt to connect to an existing database using provided credentials
            engine = create_engine(url)
            engine.connect().close()

        except OperationalError as conn_err:
            # Connection failed, so connect to default postgres DB and create new megaqc db and user
            config_url = make_url(url)
            postgres_url = copy(config_url)

            # Default db settings
            postgres_url.database = "postgres"
            postgres_url.username = "postgres"
            postgres_url.password = None

            default_engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
            conn = default_engine.raw_connection()
            # conn.autocommit = True

            # We use separate transactions here so that a failure in one doesn't affect the other
            with conn.cursor() as cur:
                print("Initializing the postgres user")
                postgres_create_user(
                    config_url.username,
                    conn=conn,
                    cur=cur,
                    password=config_url.password,
                )
            with conn.cursor() as cur:
                print("Initializing the postgres database")
                postgres_create_database(
                    conn=conn,
                    cur=cur,
                    database=config_url.database,
                    user=config_url.username,
                )

            # Ue engine with newly created db / user, if it fails again something bigger wrong
            engine = create_engine(url)
            engine.connect().close()
    else:
        engine = create_engine(url)

    """Initializes the database."""
    db.metadata.bind = engine
    db.metadata.create_all()

    # Tell alembic that we're at the latest migration, since we just created everything from scratch
    stamp()

    print("Initialized the database.")
