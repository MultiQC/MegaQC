"""
Location of a rewritten API in a RESTful style, with appropriate resources
Following the JSON API standard where relevant: https://jsonapi.org/format/
"""
from flask import request, Blueprint, jsonify
from flask_restful import Resource, Api, marshal_with
from sqlalchemy.sql.functions import count
from sqlalchemy.orm import joinedload
from flask.globals import current_app
import os
from flask_login import login_required, login_user, logout_user, current_user, login_manager
from uuid import uuid4
import json
from numpy import mean, std, repeat, concatenate, flip

from megaqc.api.views import check_user, check_admin
from megaqc.model import models, schemas
import megaqc.user.models as user_models
from megaqc.extensions import db, restful
from megaqc import model
from megaqc.api.filters import build_filter_query

api_bp = Blueprint('rest_api', __name__, url_prefix='/rest_api/v1')


def get_upload_dir():
    upload_dir = current_app.config['UPLOAD_FOLDER']
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)

    return upload_dir


def get_unique_filename():
    dir = get_upload_dir()
    while True:
        proposed = os.path.join(dir, str(uuid4()))
        if not os.path.exists(proposed):
            return proposed


class ReportList(Resource):
    def get(self):
        """
        Get a list of reports
        """
        report_meta = db.session.query(
            models.Report,
            # count(models.Sample.sample_id)
        ).all()

        return schemas.ReportSchema(many=True, exclude=['report_meta']).dump(report_meta)

    @check_user
    def post(self, user):
        """
        Upload a new report
        """
        file_name = get_unique_filename()
        request.files['report'].save(file_name)
        upload_row = models.Upload.create(
            status="NOT TREATED",
            path=file_name,
            message="File has been created, loading in MegaQC is queued.",
            user_id=user.user_id
        )

        return schemas.UploadSchema(exclude=['path']).dump(upload_row)


class Report(Resource):
    def get(self, report_id):
        """
        Get data about this report
        """
        report_meta = db.session.query(
            models.Report,
        ).options(
            joinedload(models.Report.meta)
        ).filter(
            models.Report.report_id == report_id
        ).first()

        return schemas.ReportSchema(many=False).dump(report_meta)

    def put(self, report_id):
        """
        Update this report
        """
        raise NotImplementedError()

    @check_admin
    def delete(self, report_id, user):
        """
        Delete this report
        """
        db.session.query(models.Report).filter(models.Report.report_id == report_id).delete()
        db.session.commit()
        return {}


class SamplesList(Resource):
    def get(self, report_id=None):
        """
        Get all samples for this report
        """

        # Only apply the report filter if we had a report ID
        filters = []
        if report_id is not None:
            filters.append([models.Sample.report_id == report_id])

        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        samples = db.session.query(
            models.Sample
        ).options(
            joinedload(models.Sample.data).joinedload(models.SampleData.data_type)
        ).filter(
            *filters
        ).all()

        return schemas.SampleSchema(many=True, exclude=['report']).dump(samples)

    def post(self, report_id):
        # Currently we only support uploading samples via a report
        raise NotImplementedError()


class Sample(Resource):
    def get(self, sample_id, report_id=None):
        """
        Get a single sample within a report
        """
        samples = db.session.query(
            models.Sample
        ).options(
            joinedload(models.Sample.data).joinedload(models.SampleData.data_type)
        ).filter(
            models.Sample.sample_id == sample_id
        ).first()

        return schemas.SampleSchema(many=False, exclude=['report']).dump(samples)

    def put(self, report_id, sample_id):
        """
        Update an existing sample
        """
        raise NotImplementedError()

    @check_admin
    def delete(self, sample_id, user, report_id=None):
        """
        Delete a single sample
        """
        db.session.query(
            models.Sample
        ).options(
            joinedload(models.Sample.data).joinedload(models.SampleData.data_type)
        ).filter(
            models.Sample.sample_id == sample_id
        ).delete()

        db.session.commit()

        return {}


class UserList(Resource):
    @check_admin
    def get(self):
        """
        Get a list of users
        """
        users = db.session.query(
            user_models.User
        ).options(
            joinedload(user_models.User.roles)
        ).all()

        return schemas.UserSchema(many=True, exclude=['reports', 'password', 'salt', 'api_token']).dump(users)

    def post(self):
        """
        Create a new user
        """
        data = schemas.UserSchema(exclude=['reports', 'salt', 'api_token']).load(request.json, session=db.session)
        new_user = User(**data)
        new_user.set_password(data.password)
        new_user.active = True
        new_user.save()


class User(Resource):
    @check_admin
    def get(self, user_id, user):
        """
        Get a specific user
        """
        users = db.session.query(
            user_models.User
        ).options(
            joinedload(user_models.User.roles)
        ).filter(
            user_models.User.user_id == user_id
        ).first()

        return schemas.UserSchema(many=False).dump(users)

    def put(self, user_id):
        """
        Update a user
        """
        raise NotImplementedError()

    @check_admin
    def delete(self, user_id):
        """
        Delete a user
        """
        db.session.query(
            user_models.User
        ).filter(
            user_models.User.user_id == user_id
        ).delete()
        db.session.commit()

        return {}


class DashboardList(Resource):
    def get(self, user_id):
        pass

    def post(self, user_id):
        pass


class Dashboard(Resource):
    def get(self, user_id, dashboard_id):
        pass

    def put(self, user_id, dashboard_id):
        pass

    def delete(self, user_id, dashboard_id):
        pass


class FavouriteList(Resource):
    def get(self, user_id):
        pass

    def post(self, user_id):
        pass


class Favourite(Resource):
    def get(self, user_id, favourite_id):
        pass

    def put(self, user_id, favourite_id):
        pass

    def delete(self, user_id, favourite_id):
        pass


class FilterList(Resource):
    def get(self):
        pass

    def post(self):
        pass


class Filter(Resource):
    def get(self, filter_id):
        pass

    def put(self, filter_id):
        pass

    def delete(self, filter_id):
        pass


class TrendSeries(Resource):
    def get(self):
        filter = json.loads(request.args.get('filter', '[]'))
        fields = json.loads(request.args['fields'])

        query = build_filter_query(filter)
        plots = []
        for field in fields:

            # Choose the columns to select, and further filter it down to samples with the column we want to plot
            query = query.with_entities(
                models.Report.created_at,
                models.SampleData.value
            ).filter(
                models.SampleDataType.data_key == field
            ).order_by(
                models.Report.created_at.asc(),
            )
            data = query.all()

            # If the query returned nothing, skip this field
            if len(data) == 0:
                break

            x, y = zip(*data)
            y = [float(num) for num in y]

            # Add the raw data
            plots.append(dict(
                type='scatter',
                x=x,
                y=y,
                line=dict(color='rgb(0,100,80)'),
                mode='markers',
                name=field,
            ))

            # Add the mean
            y2 = repeat(mean(y), len(x))
            plots.append(dict(
                type='scatter',
                x=x,
                y=y2.tolist(),
                line=dict(color='rgb(0,100,80)'),
                mode='lines',
                showlegend=False,
            ))

            # Add the stdev
            x3 = concatenate((x, flip(x, axis=0)))
            stdev = repeat(std(y), len(x))
            upper = y2 + stdev
            lower = y2 - stdev
            y3 = concatenate((lower, upper))
            plots.append(dict(
                type='scatter',
                x=x3.tolist(),
                y=y3.tolist(),
                fill='tozerox',
                fillcolor='rgba(0,100,80,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
            ))

        return jsonify(plots)


restful.add_resource(ReportList, '/reports')
restful.add_resource(Report, '/reports/<int:report_id>')
restful.add_resource(SamplesList, '/reports/<int:report_id>/samples', '/samples')
restful.add_resource(Sample, '/reports/<int:report_id>/samples/<int:sample_id>', '/samples/<int:sample_id>')

restful.add_resource(UserList, '/users')
restful.add_resource(User, '/users/<int:user_id>')
# restful.add_resource(DashboardList, '/users/<int:user_id>/dashboards')
# restful.add_resource(Dashboard, '/users/<int:user_id>/dashboards/<int:dashboard_id>')
# restful.add_resource(FavouriteList, '/users/<int:user_id>/favourites')
# restful.add_resource(Favourite, '/users/<int:user_id>/favourites/<int:favourite_id>')
restful.add_resource(TrendSeries, '/plots/trends/series', endpoint='trend_data')

restful.add_resource(FilterList, '/filters')
restful.add_resource(Filter, '/filters/<int:filter_id>')

restful.init_app(api_bp)
