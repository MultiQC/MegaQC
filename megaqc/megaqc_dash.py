import dash
from flask import render_template


class MegaQcDash(dash.Dash):
    """
    Subclass of Dash, which renders a jinja template rather than using the default HTML template
    """
    def interpolate_index(self, **kwargs):
        t = render_template('dash.html', **kwargs)
        return t
