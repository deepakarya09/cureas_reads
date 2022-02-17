from google.cloud import storage
from sqlalchemy.sql.base import Executable
from sqlalchemy.sql.expression import true
from flask import current_app as cur_app
from app.main.config import ssl_logger
from google.api_core.exceptions import NotFound
from app.main import db

storage_client = storage.Client()


def upload_bucket(bytes_im, remote_path):
    bucket = storage_client.get_bucket(cur_app.config["BUCKET_NAME"])
    thumbnail_blob = bucket.blob(remote_path)
    thumbnail_blob.upload_from_string(bytes_im, content_type="image/png")


def upload_html_blob(bucket_name, destination_blob_name, date, string_data, brand_obj):
    bucket = storage_client.bucket(bucket_name)

    default_fqdn = (brand_obj.default_fqdn.replace(" ", "")).lower()
    brand_domain = (brand_obj.fqdn.replace(" ", "")).lower()

    blob = bucket.blob(
        f"{brand_domain}/{cur_app.config['HTML_GCP_REMOTE_FOLDER']}/{date}/" + destination_blob_name)
    blob.upload_from_string(string_data, content_type="text/html")

    blob1 = bucket.blob(
        f"{default_fqdn}/{cur_app.config['HTML_GCP_REMOTE_FOLDER']}/{date}/" + destination_blob_name)
    blob1.upload_from_string(string_data, content_type="text/html")
    return blob.public_url


def upload_html_blob_story(bucket_name, destination_blob_name, date, string_data, brand_obj):
    bucket = storage_client.bucket(bucket_name)

    default_fqdn = (brand_obj.default_fqdn.replace(" ", "")).lower()
    brand_domain = (brand_obj.fqdn.replace(" ", "")).lower()

    blob = bucket.blob(
        f"{brand_domain}/story/{date}/" + destination_blob_name)
    blob.upload_from_string(string_data, content_type="text/html")

    blob1 = bucket.blob(
        f"{default_fqdn}/story/{date}/" + destination_blob_name)
    blob1.upload_from_string(string_data, content_type="text/html")
    return blob.public_url


def upload_html_blob_special_page(bucket_name, destination_blob_name, string_data, brand_obj):
    bucket = storage_client.bucket(bucket_name)
    default_fqdn = (brand_obj.default_fqdn.replace(" ", "")).lower()
    brand_domain = (brand_obj.fqdn.replace(" ", "")).lower()

    blob = bucket.blob(f"{brand_domain}/" + destination_blob_name)
    blob.upload_from_string(string_data, content_type="text/html")

    blob1 = bucket.blob(f"{default_fqdn}/" + destination_blob_name)
    blob1.upload_from_string(string_data, content_type="text/html")
    return blob.public_url


def chage_link_to_default(old_fqdn, brand_obj):
    for page in brand_obj.branding_page:
        try:
            new_url_location = page.cdn_html_page_link.replace(
                f'{(old_fqdn).lower()}',  f'{(brand_obj.default_fqdn).lower()}')
            page.cdn_html_page_link = new_url_location
            db.session.commit()

        except NotFound as e:
            # https://stackoverflow.com/questions/58925651/how-to-pip-install-google-cloud-exceptions
            ssl_logger.exception(f'rename  ')

        except Exception as e:

            ssl_logger.exception(f'rename ')


def copy_pages_to_new_location(bucket_name, brand_obj):
    bucket = storage_client.bucket(bucket_name)
    # default_fqdn =  (brand_obj.default_fqdn.replace(" ", "")).lower()
    # rand_domain = (brand_obj.fqdn.replace(" ", "")).lower()
    # newLocation = rand_domain +"/page/1634714783/untitled.html"
    # blob = bucket.blob(f"mkdkdkd.nmedia2.com/page/1634714783/untitoled.html")

    # all_migration = True

    # try:
    #     blob_copy = bucket.copy_blob(
    #         blob, bucket, newLocation
    #     )

    # except NotFound as e:

    #     print("not founttnn")
    # except Exception as e:
    #     print(e)
    #     ssl_logger.exception(f'jjjjjjjjjjj  ')
    count = 0
    for page in brand_obj.branding_page:
        try:
            baseurl = cur_app.config["BUCKET_BASE_URL"]
            old_url_location = page.cdn_html_page_link.replace(
                f'{baseurl}', '')
            sub_string = old_url_location.split('/', 1)[1]
            old_url = f'{brand_obj.default_fqdn}/'+sub_string
            blob = bucket.blob(old_url)
            new_location_url = old_url.replace(
                f'{(brand_obj.default_fqdn).lower()}', f'{(brand_obj.fqdn).lower()}')
            blob_copy = bucket.copy_blob(blob, bucket, new_location_url)
            page.cdn_html_page_link = blob_copy.public_url
            db.session.commit()

        except NotFound as e:
            # https://stackoverflow.com/questions/58925651/how-to-pip-install-google-cloud-exceptions
            ssl_logger.exception(
                f'Not fount while transfaring page from {old_url}  to {new_location_url} ')

        except Exception as e:
            count += 1
            ssl_logger.exception(
                f'Error while transfaring page from {old_url}  to {new_location_url} ')

    if count == 0:
        return True
    else:
        return False


def delete_old_location_page(bucket_name, oldfqdn):

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    try:

        blobs = bucket.list_blobs(prefix=f'{oldfqdn}/')

        for blob in blobs:
            try:
                ssl_logger.info(f'page deleted from old location{oldfqdn}')
                blob.delete()
            except Exception as e:
                ssl_logger.exception(
                    f'exeption while deleting pages in folder{oldfqdn}')

    except Exception as e:
        ssl_logger.exception(
            f'exeption while deleting pages in folder{oldfqdn}')
