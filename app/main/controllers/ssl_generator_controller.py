from app.main.tokenvalidation.token_check import token_required
from app.main.services.ssl_generation_services import create_ssl, add_brand, ssl_domain_validator, get_active_domain,generate_ssl_cert
from app.main.utils.ssl_generation_dto import SslGeneration
from flask_restplus import Resource
from flask import request
from app.main.config import ssl_logger
import threading
from urllib.parse import urlparse
import dns.resolver
from werkzeug.exceptions import BadRequest
from flask import current_app as cur_app
from app.main.models.brands import Brand

api = SslGeneration.api


_req_for_ssl = SslGeneration.ssl_request


@api.route("api/v1.0/brand/ssl/create")
class CreateSSL(Resource):
    @api.expect(_req_for_ssl)
    def post(self):
        data = request.json
        return ssl_domain_validator(data=data)


@api.route("api/v1.0/brand/<brand_id>/activedomain")
class GeteDomain(Resource):
    @api.expect(_req_for_ssl)
    def get(self, brand_id):
        return get_active_domain(id=brand_id)
    

@api.route("api/v1.0/brand/<brand_id>/generatessl")
class CreateSsl(Resource):
    @api.expect(_req_for_ssl)
    def get(self, brand_id):
        return generate_ssl_cert(id=brand_id)


@api.route("api/v1.0/brand/adddefaultbrnad")
class migrate(Resource):
    @api.expect(_req_for_ssl)
    def get(self):
        return add_brand()
