import calendar
from operator import sub
import time
import uuid
from http import HTTPStatus
import datetime
from google.cloud.storage import retry

from sqlalchemy import func
from sqlalchemy.sql.functions import current_date, current_time
from werkzeug.exceptions import BadRequest
from app.main.models.brands import Brand
from sqlalchemy import or_
from app.main import config
from app.main import db
from app.main.models.user import User
from app.main.models.token import Token
from app.main.services import get_time
from app.main.models.ssl_cert_model import ssl_cert_generation
import random
import subprocess
import string
import os
from urllib.parse import urlparse
import dns.resolver
from flask import current_app as cur_app
from app.main.services import get_time
from app.main.services.ssl_generation_services import create_ssl, create_ssl_by_cron_job
from app.main.config import ssl_logger


def ssl_cron_job():
    print("ssl cron job hit ")
    try:
        from manage import app
        with app.app_context():
            current_time = get_time()
            ssl_row = ssl_cert_generation.query.filter(ssl_cert_generation.ssl_in_use == True).filter(or_(
                current_time >= ssl_cert_generation.fqdn_expiry_at, ssl_cert_generation.ssl_status == False)).order_by(func.random()).first()
            print(f"query output {ssl_row}")

            if ssl_row:
                fqdn = f"https://{ssl_row.fqdn}/"
                domain_name = {"site_url": fqdn}
                ssl_logger.critical(f"scron job new started : {fqdn}")
                print(f"cron job start for {fqdn}")
                create_ssl_by_cron_job(data=domain_name)
            # from manage import app
            # with app.app_context():
            #     for i in ssl_row:
            #         time.sleep(10)
            #         fqdn = f"https://{i.fqdn}/"
            #         domain_name = {"site_url": fqdn}
            #         ssl_logger.exception(f"scron job new started : {fqdn}")
            #         create_ssl(data=domain_name)

            # ssl_generation_pages = ssl_cert_generation.query.filter(True == ssl_cert_generation.ssl_status).filter(or_(ssl_cert_generation.new_location_migration == False, ssl_cert_generation.old_location_migration == False)).all()
            # for item in ssl_generation_pages:
            #     gcp_bucket_page_delete_move_handeler(item.fqdn)

            print(ssl_row)
    except Exception as e:
        print(f"exeption in the job{e}")

    return {"message": 'success cron job'}
