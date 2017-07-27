# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from megaqc.extensions import db
from megaqc.user.models import User

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')


@blueprint.route('/')
@login_required
def members():
    """List members."""
    return render_template('users/members.html')

@blueprint.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        abort(403) 
    else:
        users_data = db.session.query(User).all()
        return render_template('users/admin.html', users_data=users_data)
