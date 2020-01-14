# -*- coding: utf-8 -*-
""" MegaQC: A web-based tool to collect and visualise data from multiple MultiQC reports.
This file contains the app module, with the app factory function."""

from __future__ import print_function
from builtins import str
from future import standard_library
standard_library.install_aliases()

import jinja2
import logging
import markdown

from flask import Flask, jsonify, render_template, request
from megaqc import commands, public, user, version, api
from megaqc.extensions import cache, csrf_protect, db, debug_toolbar, login_manager
from megaqc.scheduler import init_scheduler
from megaqc.settings import ProdConfig, TestConfig

def create_app(config_object):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    # get appropriate log level from config and set it
    log_level = getattr(config_object, 'LOG_LEVEL', logging.INFO)
    app.logger.setLevel(log_level)
    app.config.from_object(config_object)
    if app.config['SERVER_NAME'] is not None:
        print(" * Server name: {}".format(app.config['SERVER_NAME']))
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    init_scheduler(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)

    @app.context_processor
    def inject_debug():
        """ Make the debug variable available to templates """
        return dict(debug=app.debug, version=version)

    @app.template_filter()
    def safe_markdown(text):
        return jinja2.Markup(markdown.markdown(text))

    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    csrf_protect.exempt(api.views.api_blueprint)
    app.register_blueprint(api.views.api_blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        err_msg = str(error)
        # Return JSON if an API call
        if request.path.startswith('/api/'):
            response = jsonify({
                'success': False,
                'message': err_msg,
                'error': {
                    'code': error_code,
                    'message': err_msg
                }
            })
            response.status_code = error_code
            return response
        # Return HTML error if not an API call
        if error_code in [401, 404, 500]:
            return render_template('{0}.html'.format(error_code)), error_code
        else:
            return render_template('error.html', error=error), error_code
    for errcode in [400, 401, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 428, 429, 431, 500, 501, 502, 503, 504, 505]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)
    app.cli.add_command(commands.initdb)
    app.cli.add_command(commands.upload)
