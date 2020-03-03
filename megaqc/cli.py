#!/usr/bin/env python

""" MegaQC: a web application that collects results from multiple runs of MultiQC and allows bulk visualisation.
"""

import os

import pkg_resources

import click
from flask.cli import FlaskGroup


def create_megaqc_app(info):
    import os
    from megaqc.app import create_app
    from megaqc.settings import TestConfig, DevConfig, ProdConfig

    if os.environ.get("FLASK_DEBUG", False):
        CONFIG = DevConfig()
    elif os.environ.get("MEGAQC_PRODUCTION", False):
        CONFIG = ProdConfig()
    else:
        CONFIG = TestConfig()
    return create_app(CONFIG)


@click.group(cls=FlaskGroup, create_app=create_megaqc_app)
def cli():
    """
    Welcome to the MegaQC command line interface!\n MegaQC is built using the
    Flask Python web framework.

    See below for the available commands - for example,
    to start the MegaQC server, use the command: megaqc run
    """


def main():
    version = pkg_resources.get_distribution("megaqc").version
    print("This is MegaQC v{}\n".format(version))
    if os.environ.get("FLASK_DEBUG", False):
        print(" * Environment variable FLASK_DEBUG is true - running in dev mode")
        os.environ["FLASK_ENV"] = "dev"
    elif not os.environ.get("MEGAQC_PRODUCTION", False):
        os.environ["FLASK_ENV"] = "test"
    cli()


if __name__ == "__main__":
    main()
