# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, abort, json, Request
from flask_login import login_required, login_user, logout_user, current_user

from collections import OrderedDict

from megaqc.extensions import login_manager, db
from megaqc.public.forms import LoginForm
from megaqc.user.forms import RegisterForm
from megaqc.user.models import User
from megaqc.model.models import Report, PlotConfig, PlotData, PlotCategory
from megaqc.api.utils import get_samples, get_report_metadata_fields, get_sample_metadata_fields, get_report_plot_types
from megaqc.utils import settings, flash_errors

from sqlalchemy.sql import func, distinct
from urllib import unquote_plus

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.query.get(int(user_id))

@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    return render_template('public/home.html', num_samples=get_samples(count=True))

@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    """Log in."""
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash('Welcome {}! You are now logged in.'.format(current_user.first_name), 'success')
            redirect_url = request.args.get('next') or url_for('public.home')
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template('public/login.html', form=form)

@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        user_id = (db.session.query(func.max(User.user_id)).scalar() or 0)+1
        User.create(
            user_id=user_id,
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            active=True
        )
        flash("Thanks for registering! You're now logged in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route('/about/')
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template('public/about.html', form=form)

@blueprint.route('/plot_type/')
def choose_plot_type():
    """Choose plot type."""
    return render_template('public/plot_type.html', num_samples=get_samples(count=True))

@blueprint.route('/report_plot/')
@login_required
def report_plot_select_samples():
    reports = db.session.query(Report).all()

    # Get the sample metadata fields
    sample_md_fields = { k['key']: {'section':k['section']} for k in get_sample_metadata_fields() }
    for md in sample_md_fields:
        if md in settings.sample_metadata_fields:
            if settings.sample_metadata_fields[md].get('hidden', False):
                continue
            sample_md_fields[md].update(settings.sample_metadata_fields[md])
        if 'priority' not in sample_md_fields[md]:
            sample_md_fields[md]['priority'] = 1
        if 'nicename' not in sample_md_fields[md]:
            sample_md_fields[md]['nicename'] = "{0}: {1}".format(sample_md_fields[md]['section'].replace('_', ' '),md.replace('_', ' '))
    sample_md_sorted = OrderedDict(sorted(sample_md_fields.items(), key=lambda x: x[1]['priority'], reverse=True))

    # Render the template
    return render_template(
        'public/report_plot_select_samples.html',
        db=db,
        User=User,
        reports=reports,
        user_token=current_user.api_token,
        num_samples=get_samples(count=True),
        report_fields=get_report_metadata_fields(),
        report_plot_types=get_report_plot_types(),
        sample_md=sample_md_sorted
        )


@blueprint.route('/report_plot/plot/')
@login_required
def report_plot():
    return render_template(
        'public/report_plot.html',
        db=db,
        User=User,
        filters = request.values
        )

