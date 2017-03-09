# -*- coding: utf-8 -*-
""" MultiQC_DB: A web-based tool to collect and visualise data from multiple MultiQC reports.
This file contains the app module, with the app factory function."""

from __future__ import print_function
from flask import Flask, render_template
from flask.helpers import get_debug_flag

from multiqc_db import commands, public, user, version
from multiqc_db.assets import assets
from multiqc_db.extensions import bcrypt, cache, csrf_protect, db, debug_toolbar, login_manager, migrate
from multiqc_db.settings import DevConfig, ProdConfig

from multiqc import __version__

def create_app(config_object=ProdConfig):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    assets.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)

    @app.context_processor
    def inject_debug():
        """ Make the debug variable available to templates """
        return dict(debug=app.debug, version=version)

    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code
    for errcode in [401, 404, 500]:
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

# Run the app!
CONFIG = DevConfig if get_debug_flag() else ProdConfig
app = create_app(CONFIG)

# Live reload
if get_debug_flag():
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    from livereload import Server
    server = Server(app.wsgi_app)
    server.serve()
