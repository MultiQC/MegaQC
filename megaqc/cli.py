#!/usr/bin/env python

""" MegaQC: a web application that collects results from multiple runs of MultiQC and allows bulk visualisation.
"""

import os

import click
import pkg_resources
from environs import Env
from flask.cli import FlaskGroup


def create_megaqc_app(info):
    import os

    from megaqc.app import create_app
    from megaqc.settings import DevConfig, ProdConfig, TestConfig

    env = Env()
    env.read_env()

    if env.bool("FLASK_DEBUG", False):
        CONFIG = DevConfig()
    elif env.bool("MEGAQC_PRODUCTION", False):
        CONFIG = ProdConfig()
    else:
        CONFIG = TestConfig()
    return create_app(CONFIG)


@click.group(cls=FlaskGroup, create_app=create_megaqc_app)
def cli():
    """
    Welcome to the MegaQC command line interface.

    \nSee below for the available commands - for example,
    to start the MegaQC server, use the command: megaqc run
    """


def main():
    version = pkg_resources.get_distribution("megaqc").version
    print("This is MegaQC v{}\n".format(version))

    env = Env()
    env.read_env()

    if env.bool("FLASK_DEBUG", False):
        print(" * Environment variable FLASK_DEBUG is true - running in dev mode")
        os.environ["FLASK_ENV"] = "dev"
    elif env.bool("MEGAQC_PRODUCTION", False):
        os.environ["FLASK_ENV"] = "test"
    cli()


if __name__ == "__main__":
    main()
