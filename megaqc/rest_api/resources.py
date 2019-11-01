import abc
from hashlib import sha1
from http import HTTPStatus

from flask import request, jsonify, make_response
from flask_login import current_user
from flask_restful import Resource
from marshmallow.utils import INCLUDE
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Load

import megaqc.user.models as user_models
from megaqc.api.views import check_user
from megaqc.extensions import db
from megaqc.model import models
from megaqc.rest_api import schemas, utils, plot
from megaqc.rest_api.webarg_parser import use_kwargs


class JsonApiResource(Resource):
    """
    A REST API resource that uses JSON API schemas to define the input and output representations
    """

    # Relationships to include in the output
    included = []

    # def __init__(self, schema, model, included=None):
    #     self.model = model
    #     self.schema = schema
    #     self.included = included if included is not None else []

    method_decorators = [utils.check_perms]

    @classmethod
    def _get_exclude(cls, **kwargs):
        """
        Returns a list of keys to dynamically exclude from the output
        """
        return []

    @classmethod
    def _id_column(cls):
        """
        The column tuple for the primary key of the model
        """
        return cls.model.primary

    @classmethod
    def _id_name(cls):
        """
        The string name of the single primary key column of the associated model
        """
        return cls._id_column[0].name


class ResourceDetail(JsonApiResource):
    """
    Represents the URL for a single resource, e.g. /reports/1
    """

    @classmethod
    def _get_by_id(cls, **kwargs):
        """
        Returns a query that fetches a single resource
        """
        return (
            db.session.query(cls.model)
                .options(Load(cls.model).joinedload("*"))
                .get(kwargs[cls._id_name])
        )

    def get(self, **kwargs):
        """
        Get detail for a single resource
        """
        data = self._get_by_id(**kwargs)

        if data:
            return self.schema(many=False, exclude=self._get_exclude(**kwargs)).dump(data)
        else:
            return {}, HTTPStatus.NOT_FOUND

    def delete(self, **kwargs):
        """
        Delete a single resource
        """
        model = self._get_by_id(**kwargs)

        if model:
            db.session.delete(model)
            db.session.commit()
            return {}, HTTPStatus.NO_CONTENT
        else:
            return {}, HTTPStatus.NOT_FOUND

    def patch(self, **kwargs):
        """
        Update a single resource
        """
        req_data = self.schema(many=False).load(request.json)
        model = self._get_by_id(**kwargs)

        if model:
            model.update(req_data)
            db.session.commit()
            return (
                self.schema(many=False).dump(
                    model, exclude=self._get_exclude(**kwargs)
                ),
                HTTPStatus.OK,
            )
        else:
            return {}, HTTPStatus.NOT_FOUND


class ResourceList(JsonApiResource):
    """
    Represents the URL for a list of resources, e.g. /reports
    """

    @classmethod
    def _list_query(cls, **kwargs):
        """
        Returns a query that will fetch the list of resources
        """
        query = db.session.query(cls.model).options(Load(cls.model).joinedload("*"))

        # If we have any view args, use them to filter the data. For example for /reports/1/samples, we should
        # filter to only samples that belong to report 1
        for key, value in request.view_args.items():
            query = query.filter(getattr(cls.model, key) == value)

        return query

    @classmethod
    def _create_model(cls, data, **kwargs):
        """
        Creates a model instance from the request data
        """
        return cls.model.create(**data)

    def get(self, **kwargs):
        """
        Get all resources in this collection
        """
        query = self._list_query(**kwargs)
        return self.schema(many=True, exclude=self._get_exclude(**kwargs)).dump(query.all()), HTTPStatus.OK

    def post(self, **kwargs):
        """
        Get detail for a single resource
        """
        record = self.schema(many=False, exclude=self._get_exclude(**kwargs)).load(request.json)
        db.session.add(record)
        db.session.commit()
        return self.schema(many=False, exclude=self._get_exclude(**kwargs)).dump(record), HTTPStatus.CREATED
