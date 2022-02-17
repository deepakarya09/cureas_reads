from http import HTTPStatus

from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import abort

from flask import current_app as cur_app

from app.main.controllers import error_m
from app.main.field_valiadators.aapi.worker_validator import workerPUTValidate
from app.main.services.aapi_crowd_sourcing_services import get_all_submissions, get_submission_by_id, \
    get_extension_submitted, update_worker

from app.main.utils.aapi_crowd_sourcing_dto import CrowdSourcingDto
from app.main.tokenvalidation.token_check import token_required

api = CrowdSourcingDto.api
_return_article = CrowdSourcingDto.return_article
_return_articles_by_id = CrowdSourcingDto.return_articles_by_id
_browser_extension = CrowdSourcingDto.extension_return_articles_by_id

put_validate = workerPUTValidate()


@api.route("aapi/v1.0/crowdsource/submission/<id>")
class CSubmissionId(Resource):
    @api.marshal_with(_return_article)
    @token_required
    def get(self, id):
        return get_submission_by_id(id)


@api.route("aapi/v1.0/crowdsource/submission")
class CSubmission(Resource):
    @api.marshal_with(_return_articles_by_id)
    @token_required
    def get(self):
        # URL?page=1&limit=2&searchKey=b8843kONRkxb9rvcvUhPHaF3
        args = request.args
        page = int(args.get('page', cur_app.config["PAGE"]))
        limit = int(args.get('limit', cur_app.config["LIMIT"]))
        searchKey = args.get('searchKey')
        return get_all_submissions(page, limit, searchKey)


@api.route("aapi/v1.0/crowdsource/<submission_id>")
class PutWorkerId(Resource):
    @api.marshal_with(_return_article)
    @token_required
    def put(self, submission_id):
        data = request.json
        error = put_validate.validate(data)
        if error:
            abort(HTTPStatus.BAD_REQUEST.value, error_m(error))
        return update_worker(data, submission_id)


@api.route("aapi/v1.0/article")
class browser_submission(Resource):
    @api.marshal_with(_browser_extension)
    def get(self):
        args = request.args
        page = int(args.get('page', cur_app.config["PAGE"]))
        limit = int(args.get('limit', cur_app.config["LIMIT"]))
        searchKey = args.get('searchKey', '')
        return get_extension_submitted(page, limit, searchKey)
