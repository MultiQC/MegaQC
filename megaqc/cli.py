#!/usr/bin/env python

""" MegaQC: a web application that collects results from multiple runs of MultiQC and allows bulk visualisation.
"""

import os
import sys

import click
import pkg_resources
import sqlalchemy
from environs import Env
from flask.cli import FlaskGroup

from megaqc import settings

env = Env()


def create_megaqc_app():
    from megaqc.app import create_app
    from megaqc.settings import DevConfig, ProdConfig, TestConfig

    if env.bool("FLASK_DEBUG", False):
        CONFIG = DevConfig()
    elif env.bool("MEGAQC_PRODUCTION", False):
        CONFIG = ProdConfig()
    else:
        CONFIG = TestConfig()

    if settings.run_db_check:
        # Attempt to connect to the database exists to check that it exists
        try:
            dbengine = sqlalchemy.create_engine(CONFIG.SQLALCHEMY_DATABASE_URI).connect()
            metadata = sqlalchemy.MetaData(dbengine, reflect=True)
            assert 'sample_data' in metadata.tables
        except:
            print("\n##### ERROR! Could not find table 'sample_data' in database!")
            print("Has the database been initialised? If not, please run 'megaqc initdb' first")
            print("Exiting...\n")
            sys.exit(1)
        else:
            dbengine.close()

    return create_app(CONFIG)


@click.group(cls=FlaskGroup, create_app=create_megaqc_app)
@click.pass_context
def cli(ctx):
    """
    Welcome to the MegaQC command line interface.

    \nSee below for the available commands - for example,
    to start the MegaQC server, use the command: megaqc run
    """
    # Attempt to connect to the database exists to check that it exists
    if ctx.invoked_subcommand != 'initdb':
        settings.run_db_check = True


def main():
    version = pkg_resources.get_distribution("megaqc").version
    print("This is MegaQC v{}\n".format(version))

    if env.bool("FLASK_DEBUG", False):
        print(" * Environment variable FLASK_DEBUG is true - running in dev mode")
        os.environ["FLASK_ENV"] = "dev"
    elif not env.bool("MEGAQC_PRODUCTION", False):
        os.environ["FLASK_ENV"] = "test"
    cli()


if __name__ == "__main__":
    main()
