
from app.main.services.ssl_cron_services import ssl_cron_job
from app.main.utils.ssl_generation_dto import SslGeneration
from flask_restplus import Resource
from flask import request


api = SslGeneration.api

_req_for_ssl = SslGeneration.ssl_request


@api.route("api/v1.0/ssl/cronjob")
class SslCronJob(Resource):
    def get(self):
        return ssl_cron_job()




