from http import HTTPStatus
from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import abort

from app.main.controllers import error_m
from app.main.field_valiadators.api.api_crowd_source_field_validator import CrowdSourcePost, WorkerSubmission, \
    article_validator
from app.main.services.crowd_source_submission_service import crowd_source_save_worker, crowd_source_add_article, \
    extension_submission
from app.main.utils.api_crowd_sourcing_dto import CrowdSource

api = CrowdSource.api

_worker_req = CrowdSource.worker_request
_add_article = CrowdSource.article_submission
_return_article = CrowdSource.return_article

_validator = CrowdSourcePost()
_worker_validator = WorkerSubmission()
_extension_validation = article_validator()


@api.route("api/v1.0/crowdsource/submission")
class CrowdSubmission(Resource):
    @api.expect(_worker_req)
    @api.marshal_with(_return_article)
    def post(self):
        data = request.json
        error = _worker_validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return crowd_source_save_worker(data)


@api.route("api/v1.0/crowdsource/submission/<submission_id>/add")
class CrowdSubmissionAdd(Resource):
    @api.expect(_add_article)
    @api.marshal_with(_return_article)
    def post(self, submission_id):
        data = request.json
        error = _validator.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return crowd_source_add_article(submission_id, data)


@api.route("api/v1.0/article")
class ExtensionSubmission(Resource):
    def post(self):
        data = request.json
        error = _extension_validation.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return extension_submission(data)
