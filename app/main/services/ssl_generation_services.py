import calendar
from operator import sub
import time
import uuid 
from http import HTTPStatus
import datetime
from google.cloud.storage import retry
import requests
from sqlalchemy import func
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import null
from werkzeug.exceptions import BadRequest
from app.main.models.brands import Brand
from sqlalchemy import or_
from app.main import config
from app.main import db
from app.main.models.user import User
from app.main.models.token import Token
from app.main.services import get_time
from app.main.models.ssl_cert_model import ssl_cert_generation
from app.main.gcp_clients.bucket import  copy_pages_to_new_location, delete_old_location_page, chage_link_to_default
import random
import subprocess
import string
import os
from urllib.parse import urlparse
import dns.resolver
from flask import current_app as cur_app
from app.main.services import get_time
from app.main.config import ssl_logger
import threading


import logging
cron_logger = logging.getLogger(__name__)
cron_logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(message)s')

file_handler = logging.FileHandler('log/scrape.log')
file_handler.setFormatter(formatter)

cron_logger.addHandler(file_handler)


def ssl_enrty_generater(brand_id, fqdn, success, info):
    ssl_row = ssl_cert_generation.query.filter(
        ssl_cert_generation.fqdn == fqdn).first()
    current_time = get_time()

    fqdn_expiry_time = current_time
    fqdn_created_time = current_time
    retry_count_num = 1
    if success:
        # https://www.kite.com/python/answers/how-to-create-a-unix-timestamp-in-the-future-in-python
        current_datetime = datetime.datetime.utcnow()
        future_datetime = current_datetime + datetime.timedelta(days=80)
        future_timetuple = future_datetime.timetuple()
        future_timestamp = calendar.timegm(future_timetuple)
        fqdn_expiry_time = future_timestamp
        retry_count_num = 0
    if not ssl_row:

        try:
            create = ssl_cert_generation(
                id=uuid.uuid4(),
                brand_id=brand_id,
                fqdn_expiry_at=fqdn_expiry_time,
                fqdn_created_at=fqdn_created_time,
                fqdn=fqdn,
                ssl_status=success,
                failure_reason=info,
                ssl_in_use=True,
                retry_count=retry_count_num,
                created_at=current_time,
                updated_at=current_time
            )
            db.session.add(create)
            db.session.commit()

        except Exception as e:
            ssl_logger.exception(
                f"Error in adding entry in ssl_cert_generation : {fqdn}")
            raise BadRequest(
                f"Error in adding entry in ssl_cert_generation :  {e}")
    else:
        if success:
            retryCount = 0
        else:
            retryCount = ssl_row.retry_count + 1
        try:
            ssl_row.fqdn_expiry_at = fqdn_expiry_time
            ssl_row.fqdn_created_at = fqdn_created_time
            ssl_row.ssl_status = success
            ssl_row.brand_id = brand_id
            ssl_row.ssl_in_use = True
            ssl_row.retry_count = retryCount
            ssl_row.updated_at = current_time
            ssl_row.failure_reason = info
            db.session.commit()
        except Exception as e:
            ssl_logger.exception(
                f"Error in updating entry in ssl_cert_generation : {fqdn}")
            raise BadRequest(
                f"Error in updating entry in ssl_cert_generation :  {e}")


def create_ssl(data):
    site_url = data['site_url']
    domain = urlparse(f'{site_url}')
    if domain.scheme != 'https':
        raise BadRequest("Please add domain url with https://")

    coreDomain = domain.netloc
    # https://www.geeksforgeeks.org/network-programming-in-python-dns-look-up/
    result = dns.resolver.query(coreDomain, 'A')

    from manage import app
    with app.app_context():
        for val in result:
            if cur_app.config['SERVER_IP'] != val.to_text():
                raise BadRequest(
                    f"your domain's --{coreDomain}  DNS records don't map to {cur_app.config['SERVER_IP']}")

        if data.get('brand_id'):
            brand_id = data.get('brand_id')
            try:
                uuid.UUID(brand_id)
            except Exception as e:
                ssl_logger.exception(
                    f" create_ssl - brand Id not valid: {brand_id}.")
                raise BadRequest(f"This {brand_id} - Brand id is not valid.")
            try:
                brand_details = Brand.query.filter(
                    or_(Brand.fqdn == coreDomain, Brand.default_fqdn == coreDomain)).first()
            except Exception as e:
                ssl_logger.exception(
                    f"create_ssl - Error while getting brand details by {coreDomain} : {brand_id}.")
                raise BadRequest(
                    f" create_ssl -Error while getting brand details by {coreDomain} : {brand_id}.")
            if brand_details:
                if str(brand_details.id) == brand_id:
                    pass
                else:
                    raise BadRequest(
                        f"{coreDomain} already in use,please select another domain")

            ssl_row = ssl_cert_generation.query.filter(
                ssl_cert_generation.fqdn == coreDomain).first()

            if ssl_row:
                if ssl_row.ssl_in_use:
                    if ssl_row.brand_id == brand_details.id:
                        if brand_details.default_fqdn == coreDomain:

                            old_fqdn = ssl_cert_generation.query.filter(
                                ssl_cert_generation.fqdn == brand_details.fqdn).first()
                            if old_fqdn:
                                if brand_details.fqdn == coreDomain:
                                    if check_ssl_status(coreDomain):
                                        raise BadRequest(
                                            f"{coreDomain} is already active")
                                    else:
                                        generate_ssl(coreDomain)
                                        raise BadRequest(
                                            f"{coreDomain} ssl will we generated")

                                else:
                                    old_fqdn.ssl_in_use = False
                                    old_fqdn.fqdn_expiry_at = None
                                    old_fqdn.ssl_status = False
                                    old_fqdn.brand_id = None

                                    brand_details.fqdn = coreDomain
                                    db.session.commit()
                                    delete_old_location_page(
                                        bucket_name=cur_app.config["BUCKET_NAME"], oldfqdn=old_fqdn.fqdn)
                                    chage_link_to_default(
                                        old_fqdn.fqdn, brand_details)
                                    if check_ssl_status(coreDomain):
                                        raise BadRequest(
                                            f"{coreDomain} is activated")
                                    else:
                                        generate_ssl(coreDomain)
                                        raise BadRequest(
                                            f"{coreDomain} ssl will we generated")
                        else:
                            if brand_details.fqdn == coreDomain:
                                if check_ssl_status(coreDomain):
                                    raise BadRequest(
                                        f"{coreDomain} is already active")
                                else:
                                    generate_ssl(coreDomain)
                                    raise BadRequest(
                                        f"{coreDomain} ssl will we generated")

                    else:
                        raise BadRequest(
                            f"{coreDomain} already in use,please select another domain")

                else:
                    brand = Brand.query.filter_by(id=brand_id).first()
                    old_fqdn = ssl_cert_generation.query.filter(
                        ssl_cert_generation.fqdn == brand.fqdn).first()
                    if brand.fqdn != brand.default_fqdn:
                        old_fqdn.ssl_in_use = False
                        old_fqdn.fqdn_expiry_at = None
                        old_fqdn.brand_id = None
                        old_fqdn.ssl_status = False

                        delete_old_location_page(
                            bucket_name=cur_app.config["BUCKET_NAME"], oldfqdn=old_fqdn.fqdn)

                    brand.fqdn = coreDomain
                    db.session.commit()
                    copy_pages_to_new_location(
                        bucket_name=cur_app.config["BUCKET_NAME"], brand_obj=brand)

                    generate_ssl(coreDomain)

            else:
                brand = Brand.query.filter_by(id=brand_id).first()
                if not brand:
                    raise BadRequest(
                        "Brand not available in database. Please check brand id.")
                try:
                    if brand.fqdn != brand.default_fqdn:
                        delete_old_location_page(
                            bucket_name=cur_app.config["BUCKET_NAME"], oldfqdn=brand.fqdn)
                    if brand.fqdn != brand.default_fqdn:
                        old_fqdn = ssl_cert_generation.query.filter(
                            ssl_cert_generation.fqdn == brand.fqdn).first()
                        old_fqdn.ssl_in_use = False
                        old_fqdn.fqdn_expiry_at = None
                        old_fqdn.brand_id = None
                        old_fqdn.ssl_status = False
                        db.session.commit()
                    current_time = get_time()
                    create = ssl_cert_generation(
                        id=uuid.uuid4(),
                        brand_id=brand_id,
                        fqdn=coreDomain,
                        ssl_in_use=True,
                        ssl_status=False,
                        failure_reason="",
                        retry_count=0,
                        created_at=current_time,
                        updated_at=current_time
                    )

                    db.session.add(create)
                    brand.fqdn = coreDomain
                    db.session.commit()

                    copy_pages_to_new_location(
                        bucket_name=cur_app.config["BUCKET_NAME"], brand_obj=brand)
                    generate_ssl(coreDomain)

                except Exception as e:
                    ssl_logger.exception(
                        f"Error in adding entry in ssl_cert_generation : {coreDomain}")
                    raise BadRequest(
                        f"Error in adding entry in ssl_cert_generation :  {e}")

        else:
            generate_ssl(coreDomain)


def generate_ssl(coreDomain):
    from manage import app
    with app.app_context():
        brand = Brand.query.filter(
            or_(Brand.fqdn == coreDomain, Brand.default_fqdn == coreDomain)).first()
        if not brand:
            raise BadRequest(
                "Brand not available in database. Please check again.")
        data = {'fqdn':coreDomain}

        r = requests.post(url =f'{cur_app.config["SSL_SERVER_URL"]}/sslcreate/create/ssl',json=data)
 
        # check status code for response received
        # success code - 200
        print(r)
        print(r.json())
        reponce = r.json()
        status = reponce.get('status')
        if not status:
            info=f"ssl failed due to ssl server scripts {coreDomain}"
            ssl_enrty_generater(brand.id, coreDomain, False, info)
            print(f"ssl failed due to ssl server scripts{coreDomain}")
            raise BadRequest(
                f"ssl failed due to ssl server scripts{coreDomain}")
        else:
            info="ssl generated successfully"
            ssl_enrty_generater(brand.id, coreDomain, True, info)
            print(status)
        
    
def create_ssl_by_cron_job(data):
    site_url = data['site_url']
    domain = urlparse(f'{site_url}')
    if domain.scheme != 'https':
        print("fqdn not with https://")
        cron_logger.critical(f" site url not with https {site_url}.")
        raise BadRequest("Please add domain url with https://")
    coreDomain = domain.netloc
    print(f"core domain in ssl cronjon is {coreDomain}")
    # https://www.geeksforgeeks.org/network-programming-in-python-dns-look-up/
    result = dns.resolver.query(coreDomain, 'A')
    for val in result:
        if cur_app.config['SERVER_IP'] != val.to_text():
            info = f"domain {coreDomain} DNS not map with  {cur_app.config['SERVER_IP']}"
            print(info)
            cron_logger.critical(f" {info}")
            ssl_table = ssl_cert_generation.query.filter(ssl_cert_generation.fqdn == coreDomain).first()
            if ssl_table:
                ssl_table.ssl_in_use = False
                ssl_table.updated_at = get_time()
                ssl_table.failure_reason = info
                db.session.commit()
            raise BadRequest(
                f"your domain's --{coreDomain}  DNS records don't map to {cur_app.config['SERVER_IP']}")
            
    

    brand = Brand.query.filter(
            or_(Brand.fqdn == coreDomain, Brand.default_fqdn == coreDomain)).first()
    if not brand:
        info = f"domain {coreDomain} -- Brand not available in database. Please check again"
        print(info)
        cron_logger.critical(f" {info}")
        ssl_table = ssl_cert_generation.query.filter(ssl_cert_generation.fqdn == coreDomain).first()
        if ssl_table:
            ssl_table.ssl_in_use = False
            ssl_table.updated_at = get_time()
            ssl_table.failure_reason = info
            db.session.commit()
        raise BadRequest("Brand not available in database. Please check again.")
    dataa = {'fqdn':coreDomain}
    r = requests.post(url =f'{cur_app.config["SSL_SERVER_URL"]}/sslcreate/create/ssl',json=dataa)
 
        # check status code for response received
        # success code - 200
    print(r)
    print(r.json())
    reponce = r.json()
    status = reponce.get('status')
    if not status:
        info=f"ssl failed due to ssl server scripts{coreDomain}"
        cron_logger.critical(f" {info}")
        ssl_enrty_generater(brand.id, coreDomain, False, info)
        print(f"ssl failed due to ssl server scripts {coreDomain}")
        raise BadRequest(
            f"ssl failed due to ssl server scripts {coreDomain}")
    else:
        info=f"{coreDomain}ssl generated successfully"
        cron_logger.critical(f" {info}")
        ssl_enrty_generater(brand.id, coreDomain, True, info)
        print(status)
        

def generate_ssl(coreDomain):
    from manage import app
    with app.app_context():
        brand = Brand.query.filter(
            or_(Brand.fqdn == coreDomain, Brand.default_fqdn == coreDomain)).first()
        if not brand:
            raise BadRequest(
                "Brand not available in database. Please check again.")
        data = {'fqdn':coreDomain}

        r = requests.post(url =f'{cur_app.config["SSL_SERVER_URL"]}/sslcreate/create/ssl',json=data)
 
        # check status code for response received
        # success code - 200
        print(r)
        print(r.json())
        reponce = r.json()
        status = reponce.get('status')
        if not status:
            info=f"ssl failed due to ssl server scripts {coreDomain}"
            ssl_enrty_generater(brand.id, coreDomain, False, info)
            print(f"ssl failed due to ssl server scripts {coreDomain}")
            cron_logger.critical(f" site url not with https {coreDomain}.")
            raise BadRequest(f"ssl failed due to ssl server scripts {coreDomain}")
        else:
            info="ssl generated successfully"
            cron_logger.critical(f" site url not with https {coreDomain}.")
            ssl_enrty_generater(brand.id, coreDomain, True, info)
            print(status)


       
            


def check_ssl_status(fqdn):
    ssl_active = True
    try:
        req = requests.get(f'https://{fqdn}/')
    except requests.exceptions.SSLError as e:
        ssl_active = False
        ssl_logger.exception(f"ssl is not active for this fqdn -- {fqdn}")
    except Exception as e:
        ssl_logger.exception(
            f"exception while check ssl status i function-- {fqdn}")

    return ssl_active


def add_brand():
    brand = Brand.query.all()
    for item in brand:
        print(item.fqdn)
        item.default_fqdn = item.fqdn

    db.session.commit()



def ssl_domain_validator(data):
    site_url = data['site_url']
    site_url = data.get('site_url', None)
    if not site_url:
        raise BadRequest("Please add domain url")

    site_url = data.get('site_url', None)

    brand_id = data.get('brand_id', None)
    if not brand_id:
        raise BadRequest("Please add brand id ")
    
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        ssl_logger.exception(
                f" create_ssl - brand Id not valid: {brand_id}.")
        raise BadRequest(f"This {brand_id} - Brand id is not valid.")

    domain = urlparse(f'{site_url}')

    if domain.scheme != 'https':
        raise BadRequest("Please add domain url with https://")

    coreDomain = domain.netloc
    # https://www.geeksforgeeks.org/network-programming-in-python-dns-look-up/

    result = dns.resolver.query(coreDomain, 'A')
    for val in result:
        if cur_app.config['SERVER_IP'] != val.to_text():
            raise BadRequest(
                f"your domain -- {coreDomain}  DNS records don't map to {cur_app.config['SERVER_IP']}")

    brand = Brand.query.filter_by(id=brand_id).first()
    if brand:
        if brand.fqdn == coreDomain:
            if check_ssl_status(coreDomain):
                raise BadRequest(f"{site_url} domain is active.")
            else:
                pass

    try:
        brand_details = Brand.query.filter(
            or_(Brand.fqdn == coreDomain, Brand.default_fqdn == coreDomain)).first()
    except Exception as e:
        ssl_logger.exception(
            f"Error while getting brand details by {coreDomain} : {brand_id}.")
        raise BadRequest(
            f"Error while getting brand details by {coreDomain} : {brand_id}.")
    if brand_details:
        if str(brand_details.id) == brand_id:
            pass
        else:
            raise BadRequest(
                f"{coreDomain} already in use,please select another domain")

    from manage import app
    with app.app_context():
        threading.Thread(target=create_ssl, args=(data,)).start()
    return {"message": "Your request is placed successfully and is under process"}


def get_active_domain(id):
    try:
        uuid.UUID(id)
    except Exception as e:
        ssl_logger.exception(f"brand Id not valid: {id}.")
        raise BadRequest(f"This {id} - Brand id is not valid.")

    brand = Brand.query.filter_by(id=id).first()
    if brand:
        return {"fqdn": brand.fqdn}
    else:
        BadRequest(f"brand not avalable")


def generate_ssl_cert(id):
    try:
        uuid.UUID(id)
    except Exception as e:
        ssl_logger.exception(f"brand Id not valid: {id}.")
        raise BadRequest(f"This {id} - Brand id is not valid.")

    brand = Brand.query.filter_by(id=id).first()
    if brand:
        fqdn = f"https://{brand.fqdn}/"
        domain_name = {"site_url": fqdn, "brand_id": id}
        create_ssl(data=domain_name)
    else:
        return {"message": f"brand not found with id {id}"}