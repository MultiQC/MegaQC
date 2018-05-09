# -*- coding: utf-8 -*-
"""Click commands."""
from __future__ import print_function
from builtins import next, str

import os
from glob import glob
from subprocess import call

import click
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from werkzeug.exceptions import MethodNotAllowed, NotFound

from megaqc.extensions import db

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """ Run the tests """
    import pytest
    rv = pytest.main([TEST_PATH, '--verbose'])
    exit(rv)


@click.command()
@click.option('-f', '--fix-imports', default=False, is_flag=True,
              help='Fix imports using isort, before linting')
def lint(fix_imports):
    """ Lint and check code style """
    skip = ['requirements']
    root_files = glob('*.py')
    root_directories = [
        name for name in next(os.walk('.'))[1] if not name.startswith('.')]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo('{}: {}'.format(description, ' '.join(command_line)))
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    if fix_imports:
        execute_tool('Fixing import order', 'isort', '-rc')
    execute_tool('Checking code style', 'flake8')


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively """
    # Borrowed from Flask-Script, converted to use Click.
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dirpath, filename)
                click.echo('Removing {}'.format(full_pathname))
                os.remove(full_pathname)


@click.command()
@click.option('--url', default=None,
              help='Url to test (ex. /static/image.png)')
@click.option('--order', default='rule',
              help='Property on Rule to order by (default: rule)')
@with_appcontext
def urls(url, order):
    """ Display all url routes """
    # Borrowed from Flask-Script, converted to use Click.
    rows = []
    column_length = 0
    column_headers = ('Rule', 'Endpoint', 'Arguments')

    if url:
        try:
            rule, arguments = (
                current_app.url_map
                           .bind('localhost')
                           .match(url, return_rule=True))
            rows.append((rule.rule, rule.endpoint, arguments))
            column_length = 3
        except (NotFound, MethodNotAllowed) as e:
            rows.append(('<{}>'.format(e), None, None))
            column_length = 1
    else:
        rules = sorted(
            current_app.url_map.iter_rules(),
            key=lambda rule: getattr(rule, order))
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, None))
        column_length = 2

    str_template = ''
    table_width = 0

    if column_length >= 1:
        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4
        str_template += '{:' + str(max_rule_length) + '}'
        table_width += max_rule_length

    if column_length >= 2:
        max_endpoint_length = max(len(str(r[1])) for r in rows)
        # max_endpoint_length = max(rows, key=len)
        max_endpoint_length = (
            max_endpoint_length if max_endpoint_length > 8 else 8)
        str_template += '  {:' + str(max_endpoint_length) + '}'
        table_width += 2 + max_endpoint_length

    if column_length >= 3:
        max_arguments_length = max(len(str(r[2])) for r in rows)
        max_arguments_length = (
            max_arguments_length if max_arguments_length > 9 else 9)
        str_template += '  {:' + str(max_arguments_length) + '}'
        table_width += 2 + max_arguments_length

    click.echo(str_template.format(*column_headers[:column_length]))
    click.echo('-' * table_width)

    for row in rows:
        click.echo(str_template.format(*row[:column_length]))

@click.command()
@with_appcontext
def initdb():
    """ Initialise a new database """
    if "postgresql" in current_app.config['SQLALCHEMY_DATABASE_URI']:
        try:
            create_engine(current_app.config['SQLALCHEMY_DATABASE_URI']).connect().close()
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


    """Initializes the database."""
    db.metadata.bind=db.engine
    db.metadata.create_all()
    print('Initialized the database.')


@click.command( context_settings=dict( help_option_names = ['-h', '--help'] ) )
@click.argument('json_files', type=click.Path(exists=True), nargs=-1, required=True, metavar="<multiqc_data.json>" )
def upload(json_files):
    """
    Manually upload MultiQC JSON files to MegaQC

    This function allows you to submit one or more MultiQC JSON data files
    to MegaQC. These files are generated by MultiQC v1.3 and above, and are
    typically found in `multiqc_data/multiqc_data.json`.

    Note that this functionality is designed to be run from a totally separate
    location to the main MegaQC installation. It imports and uses MultiQC code,
    so it should be run in the same environment where you usually use MultiQC.

    It should probably be part of MultiQC, but it's difficult to add
    separate subcommand functionality there.
    """

    try:
        from multiqc.utils import config as multiqc_config
        from multiqc.utils import log as multiqc_log
        from multiqc.utils import megaqc as multiqc_megaqc
    except ImportError:
        print('Error - This function requires MultiQC to be installed.')
    else:
        import json
        import gzip
        multiqc_log.init_log(multiqc_config.logger, loglevel="INFO")
        multiqc_config.mqc_load_userconfig()
        if not multiqc_config.megaqc_url:
            print('Error - MultiQC megaqc_url not set.')
        else:
            # Loop through supplied JSON files
            for fn in json_files:
                multiqc_config.logger.info("Uploading file '{}'".format(fn))
                if fn.endswith('.gz'):
                    with gzip.open(fn, 'rb') as fh:
                        multiqc_json_dump = json.load(fh)
                else:
                    with open(fn, 'r') as fh:
                        multiqc_json_dump = json.load(fh)
                multiqc_megaqc.multiqc_api_post(multiqc_json_dump)
