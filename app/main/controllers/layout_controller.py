from flask_restplus import Resource
from app.main.utils.layout_dto import layoutDto
from app.main.services.layout_services import get_layout_names

api = layoutDto.api


@api.route("iapi/v1.0/layouts/<country>")
class Layouts(Resource):
    def get(self, country):
        return get_layout_names(country)
