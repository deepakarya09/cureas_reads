import distutils
from distutils import util
from flask_restplus import Resource
from flask import request
from app.main.services.generator_service import get_all_contents
from app.main.utils.generator_dto import generator

api = generator.api
res_all = generator.res_all_content


@api.route("iapi/v1.0/contents")
class Generator(Resource):
    @api.marshal_with(res_all)
    def get(self):
        used = request.args.get('used')
        return get_all_contents(bool(distutils.util.strtobool(used)))
