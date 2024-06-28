# -*- coding: utf-8 -*-
"""
Application configuration.
"""
from __future__ import print_function

import logging
import os
import sys
import tempfile
from builtins import object

import yaml
from environs import Env

from megaqc.scheduler import upload_reports_job

env = Env()
run_db_check = False


class Config(object):
    """
    Base configuration.
    """

    SECRET_KEY = env.str("MEGAQC_SECRET", "secret-key")  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JOBS = [
        {"id": "job1", "func": upload_reports_job, "trigger": "interval", "seconds": 30, "max_instances": 1}
    ]
    SCHEDULER_API_ENABLED = True
    EXTRA_CONFIG = env("MEGAQC_CONFIG", None)
    SERVER_NAME = None
    DB_PATH = None
    LOG_LEVEL = logging.INFO
    SQLALCHEMY_DBMS = None
    SQLALCHEMY_HOST = "localhost:5432"
    SQLALCHEMY_USER = "megaqc_user"
    SQLALCHEMY_PASS = ""
    SQLALCHEMY_DATABASE = "megaqc"
    # If this is true, every user after the first has to be approved before it becomes active
    USER_REGISTRATION_APPROVAL = True

    def __init__(self):
        if self.EXTRA_CONFIG:
            with open(self.EXTRA_CONFIG) as f:
                self.extra_conf = yaml.load(f, Loader=yaml.FullLoader)
                for key in self.extra_conf:
                    if key in Config.__dict__:
                        setattr(self, key, self.extra_conf[key])
                        if key != "SQLALCHEMY_PASS":
                            print("Setting {} to {}".format(key, self.extra_conf[key]))
                        else:
                            print("Setting {} to {}".format(key, "********"))
                    else:
                        print("Key '{}' not in '{}'".format(key, self.__dict__))

    def update_db_uri(self):
        if self.SQLALCHEMY_DBMS == "sqlite":
            self.SQLALCHEMY_DATABASE_URI = "{}:///{}".format(
                self.SQLALCHEMY_DBMS, self.DB_PATH
            )
            self.SQLALCHEMY_DATABASE_URI_SAN = self.SQLALCHEMY_DATABASE_URI
        elif self.SQLALCHEMY_HOST.startswith("/"):
            # If the host starts with a /, it's probably a unix socket, which has a different URL format
            self.SQLALCHEMY_DATABASE_URI = "{}://{}:{}@/{}?host={}".format(
                self.SQLALCHEMY_DBMS,
                self.SQLALCHEMY_USER,
                self.SQLALCHEMY_PASS,
                self.SQLALCHEMY_DATABASE,
                self.SQLALCHEMY_HOST,
            )
            self.SQLALCHEMY_DATABASE_URI_SAN = "{}://{}:{}@/{}?host={}".format(
                self.SQLALCHEMY_DBMS,
                self.SQLALCHEMY_USER,
                "***" if self.SQLALCHEMY_PASS else "",
                self.SQLALCHEMY_DATABASE,
                self.SQLALCHEMY_HOST,
            )
        else:
            self.SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}/{}".format(
                self.SQLALCHEMY_DBMS,
                self.SQLALCHEMY_USER,
                self.SQLALCHEMY_PASS,
                self.SQLALCHEMY_HOST,
                self.SQLALCHEMY_DATABASE,
            )
            self.SQLALCHEMY_DATABASE_URI_SAN = "{}://{}:{}@{}/{}".format(
                self.SQLALCHEMY_DBMS,
                self.SQLALCHEMY_USER,
                "***" if self.SQLALCHEMY_PASS else "",
                self.SQLALCHEMY_HOST,
                self.SQLALCHEMY_DATABASE,
            )


class ProdConfig(Config):
    """
    Production configuration.
    """

    ENV = "prod"
    DEBUG = False
    SQLALCHEMY_DBMS = "postgresql"
    if "DB_UNIX_SOCKET" in os.environ:
        # Unix sockets dont have a port
        SQLALCHEMY_HOST = os.environ["DB_UNIX_SOCKET"]
    else:
        SQLALCHEMY_HOST = "{}:{}".format(
            env.str("DB_HOST", "localhost"), env.int("DB_PORT", "5432")
        )
    SQLALCHEMY_USER = env.str("DB_USER", "megaqc")
    SQLALCHEMY_PASS = env.str("DB_PASS", "megaqcpswd")
    SQLALCHEMY_DATABASE = env.str("DB_NAME", "megaqc")
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar

    def __init__(self):
        super(ProdConfig, self).__init__()
        self.update_db_uri()
        # Log to the terminal
        print(" * Environment: Prod", file=sys.stderr)
        print(" * Database type: {}".format(self.SQLALCHEMY_DBMS), file=sys.stderr)
        print(
            " * Database path: {}".format(self.SQLALCHEMY_DATABASE_URI_SAN),
            file=sys.stderr,
        )


class DevConfig(Config):
    """
    Development configuration.
    """

    ENV = "dev"
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DBMS = "sqlite"
    DB_NAME = "megaqc.db"
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    DEBUG_TB_ENABLED = True
    CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
    WTF_CSRF_ENABLED = False  # Allows form testing
    SQLALCHEMY_RECORD_QUERIES = True
    LOG_LEVEL = logging.DEBUG

    def __init__(self):
        super(DevConfig, self).__init__()
        self.update_db_uri()
        # Log to the terminal
        print(" * Environment: dev", file=sys.stderr)
        print(" * Database type: {}".format(self.SQLALCHEMY_DBMS), file=sys.stderr)
        print(
            " * Database path: {}".format(self.SQLALCHEMY_DATABASE_URI_SAN),
            file=sys.stderr,
        )


class TestConfig(Config):
    """
    Test configuration.
    """

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DBMS = "sqlite"
    DB_NAME = "megaqc.db"
    DB_PATH = os.path.join(tempfile.mkdtemp(), DB_NAME)
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    LOG_LEVEL = logging.DEBUG
    WTF_CSRF_ENABLED = False

    def __init__(self):
        super(TestConfig, self).__init__()
        self.update_db_uri()
        # Log to the terminal
        print(" * Environment: test", file=sys.stderr)
        print(" * Database type: {}".format(self.SQLALCHEMY_DBMS), file=sys.stderr)
        print(
            " * Database path: {}".format(self.SQLALCHEMY_DATABASE_URI_SAN),
            file=sys.stderr,
        )
