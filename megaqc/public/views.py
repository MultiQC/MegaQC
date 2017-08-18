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
from megaqc.api.utils import get_samples, get_report_metadata_fields
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
    return render_template('public/plot_type.html', num_samples=get_samples(count=True))

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

@blueprint.route('/new_plot/')
@login_required
def new_plot():
    reports = db.session.query(Report).all()
    plot_types = [x[0] for x in db.session.query(distinct(PlotConfig.section)).filter(PlotConfig.name == 'bar_graph').all()]
    plot_types.extend(['{} -- {}'.format(x[0], x[1]) for x in db.session.query(distinct(PlotConfig.section), PlotCategory.category_name).join(PlotCategory).filter(PlotConfig.name == 'xy_line').all()])
    plot_types.sort()
    return render_template('public/plot_choice.html', db=db,User=User, reports=reports, user_token=current_user.api_token, plot_types=plot_types)

@blueprint.route('/report_plot/')
@login_required
def report_plot_select_samples():
    reports = db.session.query(Report).all()

    # Get the report metadata fields
    report_fields = { k: {} for k in get_report_metadata_fields() }
    report_md = {}
    for md in report_fields:
        if md in settings.report_metadata_fields:
            if settings.report_metadata_fields[md].get('hidden', False):
                continue
            report_md[md] = settings.report_metadata_fields[md]
        else:
            report_md[md] = {}
        if 'priority' not in report_md[md]:
            report_md[md]['priority'] = 1
        if 'nicename' not in report_md[md]:
            report_md[md]['nicename'] = md.replace('_', ' ')
    report_md_sorted = OrderedDict(sorted(report_md.items(), key=lambda x: x[1]['priority'], reverse=True))

    total_num_samples=get_samples(count=True)

    # Render the template
    return render_template(
        'public/report_plot_select_samples.html',
        db=db,
        User=User,
        reports=reports,
        user_token=current_user.api_token,
        total_num_samples=total_num_samples,
        filtered_num_samples=total_num_samples,
        report_md=report_md_sorted
        )


@blueprint.route('/report_plot/plot/')
@login_required
def report_plot():
    reports = db.session.query(Report).all()
    # Get the filters JSON from the URL
    urldata = json.loads(unquote_plus(request.query_string.partition('&')[0]))
    filters = urldata['filters']
    return render_template(
        'public/report_plot.html',
        db=db,
        User=User,
        total_num_samples=get_samples(count=True),
        filtered_num_samples=get_samples(filters, count=True),
        filters = filters
        )

