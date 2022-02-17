from os import replace
import uuid
from bs4 import BeautifulSoup
import lxml.html
from flask_restplus._http import HTTPStatus
from werkzeug.exceptions import BadRequest
from app.main import db, config
from app.main.gcp_clients.bucket import upload_html_blob, upload_html_blob_special_page
from app.main.models.brand_log import BrandLog
from app.main.models.branding_pages import BrandPages
from app.main.models.brands import Brand
from app.main.models.page_data import PageData
from flask import current_app as cur_app
from google.cloud import storage
from app.main.models.page_editors import PageEditors
from app.main.models.page_seo import PageSeo
from app.main.models.template_creation import Template
from app.main.models.story_template import StoryTemplate
from app.main.models.user import User
from app.main.models.widgets import Widget
from app.main.services import get_active_user, get_time
from app.main.services.image_upload_services import upload_image_by_raw, upload_images_api
from app.main.services.parser_service import parser
from sqlalchemy import or_
from app.main.config import driver
from itsdangerous import URLSafeTimedSerializer
from datetime import date
auth_s = URLSafeTimedSerializer(config.Config.SECRET_KEY, "auth")

storage_client = storage.Client()


def save_page_data(page_data: dict):
    try:
        _p_data = PageData()
        for key, value in page_data.items():
            if hasattr(_p_data, key):
                setattr(_p_data, key, value)
        db.session.add(_p_data)
        db.session.commit()
    except Exception as e:
        config.logging.error(f"Can't save your page : {page_data}")
        raise BadRequest(f"Can't save your page : {page_data}")


def raplace_text_in_template(template_html, replace_data):
    try:
        for key, value in replace_data.items():
            if key in template_html:
                template_html = template_html.replace(key, value)
        return template_html
    except Exception as e:
        config.logging.critical(f"Failed to replace text in template:{e}")
        raise BadRequest(f"Failed to replace text in templates {e}")


def fetch_seo_data_from_widget(data, number_of_widgets):

    seo_description = ""
    seo_title = ""
    images = ""
    for i in range(number_of_widgets):
        if "page_data" in data:
            soup = BeautifulSoup(data["page_data"][i]["widget_page"], "lxml")
        elif "story_data" in data:
            soup = BeautifulSoup(data["story_data"][i]["widget_page"], "lxml")
        title = soup.find_all("div", {"class": "ql-editor"})
        image = soup.find_all("img", {"name": "image-tag"})
        if len(title) >= 2 and len(image) >= 1:
            seo_title = title[0].get_text()
            seo_description = title[1].get_text()
            images = image[0].get('src')
        break

    return {"seo_title": seo_title, "seo_description": seo_description, "seo_banner_image": images}


def parse_header_and_footer(brand_id, issued_template):
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest(
            "Brand not found in database. Please create brand or check brand id.")
    try:
        navbar_data = {
            "brand_white_logo": brand.white_theme_logo if brand.white_theme_logo else "#",
            "home_page_link": f"https://{brand.fqdn}"
        }
        footer_data = {
            "brand_black_logo": brand.black_theme_logo if brand.black_theme_logo else "#",
            "facebook_link": brand.facebook_url if brand.facebook_url else "#",
            "insta_link": brand.instagram_url if brand.instagram_url else "#",
            "twitter_link": brand.twitter_url if brand.twitter_url else "#"
        }
        soup = BeautifulSoup(issued_template, "lxml")
        if soup.find(id='navbarDiv'):
            if brand.navbar_html:
                __dom = lxml.html.fromstring(
                    issued_template)
                mydiv = __dom.get_element_by_id('navbarDiv')
                mango = parser(brand.navbar_html, navbar_data)
                myhtml = lxml.html.fromstring(
                    mango)
                mydiv.insert(0, myhtml)
                issued_template = lxml.html.tostring(__dom)
            else:
                raise BadRequest("Error in adding navbar to data")

        if soup.find(id='footerDiv'):
            if brand.footer_html:
                __dom = lxml.html.fromstring(
                    issued_template)
                mydiv = __dom.get_element_by_id('footerDiv')
                mango = parser(brand.footer_html, footer_data)
                myhtml = lxml.html.fromstring(
                    mango)
                mydiv.insert(0, myhtml)
                issued_template = lxml.html.tostring(__dom)
            else:
                raise BadRequest("Error in adding footerDiv to data")
        return issued_template
    except Exception as e:
        config.logging.warning(
            f"api: Error in parsing footer or header in template. {e}")
        raise BadRequest(f" Error in parsing footer or header in template.")


def issue_template_before_save(template_id, brand_id):
    try:
        uuid.UUID(template_id)
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"api: Get template by id : Invalid Submission Id. {e}")
        raise BadRequest(f"Template id or brand id is not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest(
            "Brand not found in database. Please create brand or check brand id.")
    issue_template = Template.query.filter_by(id=template_id).first()
    if not issue_template:
        raise BadRequest("Template not found please check template id.")
    replace_data = {"logo_url": str(brand.white_theme_logo), "footer_logo": str(brand.black_theme_logo), "changecss": str(issue_template.draft_css), "seoiconlink": str(brand.white_theme_logo), "seotitle": "Untitled", "seodescription": "This is demo issue template description",
                    "seopagelink": str(brand.fqdn), "seopagetype": "article", "seofacebbokid": "#", "seocreatedat": str(get_time()), "seobannerimage": cur_app.config["DEFAULT_WIDGET_BLANK_IMAGE"], "seotwitterid": "demo", "seogtag": str(cur_app.config["GTAG"]), "api_key": brand.email_api_key if brand.email_api_key else "#"}
    issued_template = raplace_text_in_template(
        issue_template.raw_html, replace_data)
    if not issued_template:
        config.logging.warning(
            f"api: issue template brand page: Error in replacing css and logo url")
        raise BadRequest(
            "Template not found. Please check brand logo or css file!")
    number_of_widgets = issue_template.block_count
    if not number_of_widgets:
        config.logging.warning(
            f"api: issue template brand page: Error not getting block count of issued template")
        raise BadRequest("Number of widgets is not available!")
    structure = issue_template.block_structure
    if not structure:
        config.logging.warning(
            f"api: Issue template brand page: Error not getting block structure of issued template")
        raise BadRequest(
            "Error not getting block structure of issued template!")
    if number_of_widgets != len(structure):
        raise BadRequest(
            "Block count is not equal to block structure of issued template.")

    issued_template = parse_header_and_footer(brand_id, issued_template)
    issued_template = issued_template if isinstance(
        issued_template, str) else issued_template.decode()
    try:
        page_data = [
            Widget.query.filter_by(name=structure[i]).first() for i in range(len(structure))]

        parsed_data = [
            {'block_no': i, 'widget_name': page_data[i].name, 'widget_type': page_data[i].type,
             'widget_page': parser(page_data[i].raw_html, page_data[i].default_data),
             'updated': False} for i in range(number_of_widgets)]
        template = Template.query.filter_by(id=template_id).first()

        return {"page_name": "Untitled", "raw_template": template.raw_html, "template_html": issued_template if isinstance(issued_template, str) else issued_template.decode(),
                "page_data": parsed_data}, HTTPStatus.CREATED
    except Exception as e:
        config.logging.warning(
            f"api: brand page services:  Default Template can not render due to parsing error")
        raise BadRequest(
            f" Default template can not render due to parsing error")


def save_publish_and_draft(brand_id, data):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"api: get brand id : Invalid submission brand Id. {brand_id}")
        raise BadRequest(f"This brand id not valid.")
    check = Brand.query.filter_by(id=brand_id).first()
    if not check:
        config.logging.warning(
            f"api: save publish and draft: brand not exists:{brand_id}")
        raise BadRequest(
            "Brand not availabe in database. Please check brand id!")
    number_of_widgets = len(data['page_data'])
    issue_template = Template.query.filter_by(id=data['template_id']).first()
    if not issue_template:
        raise BadRequest(
            "Template not available in database. Please check template id.")
    block_count = issue_template.block_count
    if not block_count:
        config.logging.warning(
            f"api: issue template brand page: Error not getting block count of issued template")
        raise BadRequest("Error not getting block count of issued template!")
    count = 0
    # count updated
    for i in data['page_data']:
        if i["updated"] == True:
            count = count+1
    if 'category' in data:
        if not (data['category'] == "General" or data['category'] == "Privacy" or data['category'] == "Terms" or data['category'] == "Home" or data['category'] == "System"):
            config.logging.warning(
                f"api: get all widgit: please enter valid status!")
            raise BadRequest(
                "please enter valid key, General , Privacy , Terms or Home!")
    else:
        raise BadRequest(
            "Please add category of page, General, Terms, Privacy or Home .")
    pageStatus = data['status']
    page_name = data['page_name'] if data['page_name'] else 'Untitled'

    if "seo_data" in data:
        seo = data["seo_data"]
        banner_link = ""
        if "banner_image" in seo:
            post = {"image": seo["banner_image"]}
            banner = upload_images_api(brand_id, post)
            banner_link = banner['image_link']
    else:
        seo = fetch_seo_data_from_widget(data, number_of_widgets)
        banner_link = seo['seo_banner_image']

    if pageStatus == 'PUBLISHED':
        if count != block_count:
            config.logging.warning(
                f"api: user try to publish without fill all block")
            raise BadRequest("You can’t publish with empty blocks")
    if "page_id" in data:
        raise BadRequest(
            "Please call update API page id available in given data")
    else:
        try:
            new_page_create = BrandPages(id=uuid.uuid4(), brand_id=brand_id, page_name=page_name,
                                         template_id=data['template_id'], template_raw_html=data['raw_template'] if "raw_template" in data else issue_template.raw_html, total_block_count=block_count, filled_block_count=count, status=data['status'], created_at=get_time(), updated_at=get_time(), category=data['category'], active=False)
            db.session.add(new_page_create)
            db.session.commit()

            parsed_data = [
                {'id': str(uuid.uuid4()), 'page_id': str(new_page_create.id), 'block_no': i, 'widget_name': data['page_data'][i]['widget_name'], 'widget_type': data['page_data'][i]['widget_type'], 'widget_page': data['page_data'][i]['widget_page'], 'updated': data['page_data'][i]['updated']} for i in range(block_count)]

            for d in parsed_data:
                save_page_data(d)
            page = BrandPages.query.filter_by(id=new_page_create.id).first()
            if not page:
                raise BadRequest(
                    "Page not found in databse. Please check page id.")
            try:
                add_editors = PageEditors(
                    page_id=page.id, user_id=get_active_user())
                db.session.add(add_editors)
                db.session.commit()
            except Exception as e:
                raise BadRequest(f"Error in adding editors {e}")
            try:
                page_seo = PageSeo(id=uuid.uuid4(), page_id=page.id, icon=check.white_theme_logo, title=seo["seo_title"],
                                   description=seo["seo_description"], page_link="https://" + str(check.fqdn), page_type=seo["page_type"] if "page_type" in seo else "Article", banner_image=banner_link if banner_link != '' else '#', twitter_id=seo["twitter_id"] if "twitter_id" in seo else "#", facebook_publisher=seo["facebook_publisher"] if "facebook_publisher" in data else "#")
                db.session.add(page_seo)
                log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=brand_id,
                               message="has created new issue", created_at=get_time(), date=date.today())
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                raise BadRequest(f"Error in saving seo for page {e}")

            data_item = PageData.query.filter_by(
                page_id=new_page_create.id).order_by(PageData.block_no).all()
            if not data_item:
                raise BadRequest(
                    "Data of page is not found in databse. Please create new page.")
            template_before = Template.query.filter_by(
                id=new_page_create.template_id).first()
            template_html = data['raw_template'] if "raw_template" in data else template_before.raw_html
            encoded_id = auth_s.dumps({"content_id": str(page.id)})
            replace_data = {"content_id": str(encoded_id), "logo_url": str(check.white_theme_logo), "footer_logo": str(check.black_theme_logo), "changecss": str(template_before.draft_css), "seoiconlink": str(page_seo.icon), "seotitle": str(page_seo.title), "seodescription": str(page_seo.description),
                            "seopagelink": str(page_seo.page_link), "seopagetype": str(page_seo.page_type), "seofacebbokid": str(page_seo.facebook_publisher), "seocreatedat": str(page_seo.created_at), "seobannerimage": str(page_seo.banner_image), "seotwitterid": str(page_seo.twitter_id), "seogtag": str(cur_app.config["GTAG"]), "api_key": str(check.email_api_key) if check.email_api_key else "#"}
            template_with_logo = raplace_text_in_template(
                template_html, replace_data)
            template_with_logo = parse_header_and_footer(
                brand_id, template_with_logo)
            template_with_logo = template_with_logo if isinstance(
                template_with_logo, str) else template_with_logo.decode()
            if data['status'] == "PUBLISHED":
                try:
                    if page.cdn_html_page_link == None:
                        raw = data['raw_template'] if "raw_template" in data else template_before.raw_html
                        encoded_id = auth_s.dumps({"content_id": str(page.id)})
                        replace_data = {"content_id": str(encoded_id), "logo_url": str(check.white_theme_logo), "footer_logo": str(check.black_theme_logo), "changecss": str(template_before.publish_css), "seoiconlink": str(page_seo.icon), "seotitle": str(page_seo.title), "seodescription": str(page_seo.description),
                                        "seopagelink": str(page_seo.page_link), "seoupdatedat": str(page_seo.updated_at), "seopagetype": str(page_seo.page_type), "seofacebbokid": str(page_seo.facebook_publisher), "seocreatedat": str(page_seo.created_at), "seobannerimage": str(page_seo.banner_image), "seotwitterid": str(page_seo.twitter_id), "seogtag": str(cur_app.config["GTAG"]), "api_key": str(check.email_api_key) if check.email_api_key else "#"}
                        raw_html = raplace_text_in_template(raw, replace_data)
                        raw_html = parse_header_and_footer(
                            brand_id, raw_html)
                        raw_html = raw_html if isinstance(
                            raw_html, str) else raw_html.decode()

                        parsed_html = parser(raw_html,
                                             {"temp": [items.widget_page for items in data_item]})

                        if page.page_name:
                            webname = (page.page_name.replace(" ", "")).lower()
                        else:
                            raise BadRequest(
                                "page name not found in selected page")
                        if check.name:
                            brand_fqdn = (check.fqdn.replace(" ", "")).lower()
                        else:
                            raise BadRequest(
                                "brand name not found of active brand")
                        if data['category'] == "General" or data['category'] == "System":
                            page.active = True
                            link = upload_html_blob(bucket_name=cur_app.config["BUCKET_NAME"],
                                                    destination_blob_name=str(
                                                    webname) + ".html",
                                                    string_data=parsed_html, date=page.created_at, brand_obj=check)
                        elif data['category'] == "Terms":
                            checking_page = BrandPages.query.filter(
                                BrandPages.category == "Terms", BrandPages.active == True).first()
                            if checking_page:
                                checking_page.active = False
                            page.active = True
                            link = upload_html_blob_special_page(
                                bucket_name=cur_app.config["BUCKET_NAME"], destination_blob_name="terms.html", string_data=parsed_html, brand_obj=check)

                        elif data['category'] == "Privacy":
                            checking_page = BrandPages.query.filter(
                                BrandPages.category == "Privacy", BrandPages.active == True).first()
                            if checking_page:
                                checking_page.active = False
                            page.active = True
                            link = upload_html_blob_special_page(
                                bucket_name=cur_app.config["BUCKET_NAME"], destination_blob_name="privacy.html", string_data=parsed_html, brand_obj=check)
                        elif data['category'] == "Home":
                            checking_page = BrandPages.query.filter(
                                BrandPages.category == "Home", BrandPages.active == True).first()
                            if checking_page:
                                checking_page.active = False
                            page.active = True
                            link = upload_html_blob_special_page(
                                bucket_name=cur_app.config["BUCKET_NAME"], destination_blob_name="index.html", string_data=parsed_html, brand_obj=check)

                        setattr(page, "cdn_html_page_link", link)

                        try:
                            driver.get(str(link+"?ignoreCache=1"))
                            driver.set_window_size('1440', '1080')
                            screenshot = driver.get_screenshot_as_base64()
                            raw_image = f"data:image/png;base64,{screenshot}"
                            image_link = upload_image_by_raw(
                                raw_image, brand_id)
                            setattr(page, "thumbnail_image", image_link)
                        except Exception as e:
                            config.logging.error(
                                f"Error in taking screen short. {e}")
                            print(f"Error in taking screen short. {e}")
                            raise BadRequest(
                                f"Error in taking screen short. {e}")

                    l = page.cdn_html_page_link
                    baseurl = cur_app.config["BUCKET_BASE_URL"]
                    l = l.replace(
                        f'{baseurl}{(check.fqdn).lower()}', f'https://{check.fqdn}')
                    setattr(page_seo, "page_link", l)
                    db.session.commit()
                    return {'id': str(page.id), 'link': l, 'thumbnail_image': page.thumbnail_image, 'page_name': page.page_name, "template_html": template_with_logo, "raw_template": page.template_raw_html, 'template_id': str(page.template_id), 'page_data': data_item, "status": page.status, "category": page.category, "active": page.active}, HTTPStatus.CREATED
                except Exception as e:
                    config.logging.warning(
                        f"api: brand page services:  Not able to generate page link {e}")
                    raise BadRequest(f" Not able to generate page link {e}")

            return {'id': str(page.id), 'page_name': page.page_name, "template_html": template_with_logo, "raw_template": page.template_raw_html, 'template_id': str(page.template_id), 'page_data': data_item, "status": page.status, "category": page.category, "active": page.active}, HTTPStatus.CREATED
        except Exception as e:
            config.logging.error(
                f"api: save and publish : Not able to create new page. {e}")
            raise BadRequest(f"Not able to create new page.{e}")


def update_page_by_id(brand_id, page_id, data):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"api: get brand id : Invalid submission brand Id. {brand_id}")
        raise BadRequest(f"This brand id not valid.")
    check = Brand.query.filter_by(id=brand_id).first()
    if not check:
        config.logging.warning(
            f"api: save publish and draft: brand not exists:{brand_id}")
        raise BadRequest(
            "Brand not availabe in database. Please check brand id!")
    page = BrandPages.query.filter_by(id=page_id).first()
    if not page:
        raise BadRequest("Page not found with this page id")
    page_seo = PageSeo.query.filter_by(page_id=page_id).first()
    if not page_seo:
        raise BadRequest("Page Seo not found with this page id")
    number_of_widgets = len(data['page_data'])
    issue_template = Template.query.filter_by(id=data['template_id']).first()
    if not issue_template:
        raise BadRequest(
            "Template not available in database. Please check template id.")
    block_count = issue_template.block_count
    if not block_count:
        config.logging.warning(
            f"api: issue template brand page: Error not getting block count of issued template")
        raise BadRequest("Error not getting block count of issued template!")
    count = 0
    # count updated
    for i in data['page_data']:
        if i["updated"] == True:
            count = count+1
    if 'category' in data:
        if not (data['category'] == "General" or data['category'] == "Privacy" or data['category'] == "Terms" or data['category'] == "Home" or data['category'] == "System"):
            config.logging.warning(
                f"api: get all widgit: please enter valid status!")
            raise BadRequest(
                "please enter valid key, General , Privacy , Terms or Home!")
    else:
        raise BadRequest(
            "Please add category of page, General, Terms, Privacy or Home .")
    pageStatus = data['status']
    page_name = data['page_name'] if data['page_name'] else 'Untitled'

    if pageStatus == 'PUBLISHED':
        if count != block_count:
            config.logging.warning(
                f"api: user try to publish without fill all block")
            raise BadRequest("You can’t publish with empty blocks")
    if page:
        try:
            check_editors = PageEditors.query.filter(
                PageEditors.page_id == page_id, PageEditors.user_id == get_active_user()).first()
            if check_editors:
                check_editors.updated_at = get_time()
                db.session.commit()
            else:
                add_editors = PageEditors(
                    user_id=get_active_user(), page_id=page_id)
                db.session.add(add_editors)
                db.session.commit()
        except Exception as e:
            raise BadRequest("Error in adding editors of page.")
        try:
            page.page_name = page_name
            page.status = pageStatus
            page.category = data['category']
            page.filled_block_count = count
            page.active = False
            page.template_raw_html = data['raw_template']
            page.updated_at = get_time()

            data_item = PageData.query.filter_by(
                page_id=page_id).order_by(PageData.block_no).all()
            log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=brand_id,
                           message="has update old issue", created_at=get_time(), date=date.today())
            db.session.add(log)

            db.session.add(page)
            for i in range(len(data_item)):
                data_item[i].widget_name = data['page_data'][i]['widget_name']
                data_item[i].widget_page = data['page_data'][i]['widget_page']
                data_item[i].updated = data['page_data'][i]['updated']

                db.session.add(data_item[i])
                db.session.commit()
        except Exception as e:
            config.logging.error(
                f"api: save and publish : Not able to update data due to. {e}")
            raise BadRequest(f"No able to update data due to.{e}")
    template_before = data['raw_template'] if "raw_template" in data else issue_template.raw_html
    draftcss = page.bp.draft_css
    encoded_id = auth_s.dumps({"content_id": str(page.id)})
    replace_data = {"content_id": str(encoded_id), "logo_url": str(check.white_theme_logo), "footer_logo": str(check.black_theme_logo), "changecss": str(draftcss), "seoiconlink": str(page_seo.icon), "seotitle": str(page_seo.title), "seodescription": str(page_seo.description),
                    "seopagelink": str(page_seo.page_link), "seoupdatedat": str(page_seo.created_at), "seopagetype": str(page_seo.page_type), "seofacebbokid": str(page_seo.facebook_publisher), "seocreatedat": str(page_seo.created_at), "seobannerimage": str(page_seo.banner_image), "seotwitterid": str(page_seo.twitter_id), "seogtag": str(cur_app.config["GTAG"]), "api_key": str(check.email_api_key) if check.email_api_key else "#"}
    template_with_logo = raplace_text_in_template(
        template_before, replace_data)
    template_with_logo = parse_header_and_footer(
        brand_id, template_with_logo)
    template_with_logo = template_with_logo if isinstance(
        template_with_logo, str) else template_with_logo.decode()
    try:
        if count == number_of_widgets:
            if data['status'] == "PUBLISHED":
                setattr(page, 'published_at', get_time())
                try:
                    raw = data['raw_template'] if "raw_template" in data else issue_template.raw_html
                    publishcss = page.bp.publish_css
                    encoded_id = auth_s.dumps({"content_id": str(page.id)})
                    replace_data = {"content_id": str(encoded_id), "logo_url": str(check.white_theme_logo), "footer_logo": str(check.black_theme_logo), "changecss": str(publishcss), "seoiconlink": str(page_seo.icon), "seotitle": str(page_seo.title), "seodescription": str(page_seo.description),
                                    "seopagelink": str(page_seo.page_link), "seoupdatedat": str(page_seo.created_at), "seopagetype": str(page_seo.page_type), "seofacebbokid": str(page_seo.facebook_publisher), "seocreatedat": str(page_seo.created_at), "seobannerimage": page_seo.banner_image, "seotwitterid": page_seo.twitter_id, "seogtag": str(cur_app.config["GTAG"]), "api_key": str(check.email_api_key) if check.email_api_key else "#"}
                    raw_html = raplace_text_in_template(raw, replace_data)
                    raw_html = parse_header_and_footer(
                        brand_id, raw_html)

                    raw_html = raw_html if isinstance(
                        raw_html, str) else raw_html.decode()
                    parsed_html = parser(raw_html,
                                         {"temp": [items.widget_page for items in data_item]})

                    if page.page_name:
                        webname = (page.page_name.replace(" ", "")).lower()
                    else:
                        raise BadRequest(
                            "page name not found in selected page")
                    if check.name:
                        brand_fqdn = (check.fqdn.replace(" ", "")).lower()
                    else:
                        raise BadRequest(
                            "brand name not found of active brand")
                    if data['category'] == "General" or data['category'] == "System":
                        page.active = True
                        link = upload_html_blob(bucket_name=cur_app.config["BUCKET_NAME"], destination_blob_name=str(webname) + ".html",
                                                string_data=parsed_html, date=page.created_at, brand_obj=check)
                    elif data['category'] == "Terms":
                        checking_page = BrandPages.query.filter(
                            BrandPages.category == "Terms", BrandPages.active == True).first()
                        if checking_page:
                            checking_page.active = False
                        page.active = True
                        link = upload_html_blob_special_page(
                            bucket_name=cur_app.config["BUCKET_NAME"], destination_blob_name="terms.html", string_data=parsed_html, brand_obj=check)

                    elif data['category'] == "Privacy":
                        checking_page = BrandPages.query.filter(
                            BrandPages.category == "Privacy", BrandPages.active == True).first()
                        if checking_page:
                            checking_page.active = False
                        page.active = True
                        link = upload_html_blob_special_page(
                            bucket_name=cur_app.config["BUCKET_NAME"], destination_blob_name="privacy.html", string_data=parsed_html, brand_obj=check)
                    elif data['category'] == "Home":
                        checking_page = BrandPages.query.filter(
                            BrandPages.category == "Home", BrandPages.active == True).first()
                        if checking_page:
                            checking_page.active = False
                        page.active = True
                        link = upload_html_blob_special_page(
                            bucket_name=cur_app.config["BUCKET_NAME"], destination_blob_name="index.html", string_data=parsed_html, brand_obj=check)

                    setattr(page, "cdn_html_page_link", link)

                    try:
                        driver.get(str(link+"?ignoreCache=1"))
                        driver.set_window_size('1440', '1080')
                        screenshot = driver.get_screenshot_as_base64()
                        raw_image = f"data:image/png;base64,{screenshot}"
                        image_link = upload_image_by_raw(raw_image, brand_id)
                        setattr(page, "thumbnail_image", image_link)
                    except Exception as e:
                        config.logging.error(
                            f"Error in taking screen short. {e}")
                        print(f"Error in taking screen short. {e}")
                        raise BadRequest(
                            f"Error in taking screen short. {e}")

                    l = page.cdn_html_page_link
                    baseurl = cur_app.config["BUCKET_BASE_URL"]
                    l = l.replace(f'{baseurl}{(check.fqdn).lower()}',
                                  f'https://{check.fqdn}')
                    setattr(page_seo, "page_link", l)
                    db.session.commit()

                    return {'id': str(page.id), 'link': l, 'page_name': page.page_name, "thumbnail_image": page.thumbnail_image, "template_html": template_with_logo, "raw_template": page.template_raw_html, 'template_id': str(page.template_id), 'page_data': data_item, "status": page.status, "category": page.category, "active": page.active}, HTTPStatus.CREATED
                except Exception as e:
                    config.logging.warning(
                        f"api: brand page services:  Not able to generate page link {e}")
                    raise BadRequest(" Not able to generate page link ")
    except Exception as e:
        config.logging.warning(
            f"api: brand page services:  data not able to publish without page id code")
        raise BadRequest(f"  data not able to publish with page id code{e}")
    try:
        return {'id': str(page.id), 'page_name': page.page_name, "template_html": template_with_logo, "raw_template": page.template_raw_html, 'template_id': str(page.template_id), 'page_data': data_item, "status": page.status, "category": page.category, "active": page.active}, HTTPStatus.CREATED
    except:
        config.logging.warning(
            f"api: brand page services:  data not able to save in draft without page id code")
        raise BadRequest(
            " data not able to save in draft without page id code")


def get_page(page_id):
    try:
        uuid.UUID(page_id)
    except Exception as e:
        config.logging.warning(
            f"api: get templatebyid : Invalid Submission Id. {e}")
        raise BadRequest("This page id not valid.")
    page = BrandPages.query.filter_by(id=page_id).first()
    if not page:
        raise BadRequest("This page id not valid.")
    data_item = PageData.query.filter_by(
        page_id=page_id).order_by(PageData.block_no).all()
    if not data_item:
        raise BadRequest("Data item not found for this page.")

    try:
        brand = page.brand_page
        template_before = page.bp.raw_html if page.template_raw_html == None else page.template_raw_html
        navbar_data = {
            "brand_white_logo": brand.white_theme_logo if brand.white_theme_logo else "#",
            "home_page_link": f"https://{brand.fqdn}"
        }
        footer_data = {
            "brand_black_logo": brand.black_theme_logo if brand.black_theme_logo else "#",
            "facebook_link": brand.facebook_url if brand.facebook_url else "#",
            "insta_link": brand.instagram_url if brand.instagram_url else "#",
            "twitter_link": brand.twitter_url if brand.twitter_url else "#"
        }
        template_with_logo = ''
        encoded_id = auth_s.dumps({"content_id": str(page.id)})
        if ("content_id" in template_before) or ("logo_url" in template_before) or ("footer_logo" in template_before) or ("changecss" in template_before):
            try:
                template_with_logo = template_before.replace("logo_url", str(brand.white_theme_logo)).replace(
                    "footer_logo", str(brand.black_theme_logo)).replace("changecss", str(page.bp.draft_css)).replace("content_id", str(encoded_id)).replace("api_key", str(brand.email_api_key))
            except Exception as e:
                config.logging.error(f"not able to replace. {e}")
                raise BadRequest(
                    f"This template id or brand id not valid. {e}")
        soup = BeautifulSoup(template_with_logo, "lxml")
        if soup.find(id='navbarDiv'):
            if brand.navbar_html:
                __dom = lxml.html.fromstring(
                    template_with_logo)
                mydiv = __dom.get_element_by_id('navbarDiv')
                mango = parser(brand.navbar_html, navbar_data)
                myhtml = lxml.html.fromstring(
                    mango)
                mydiv.insert(0, myhtml)
                template_with_logo = lxml.html.tostring(__dom)
                template_with_logo = template_with_logo.decode()
                print(type(template_with_logo))
                # template_with_logo = template_with_logo.replace(
                #     "navbarTop", parser(brand.navbar_html, navbar_data))
            else:
                raise BadRequest("Brand don't have saved navbar html")
        soup = BeautifulSoup(template_with_logo, "lxml")
        if soup.find(id='footerDiv'):

            if brand.footer_html:
                __dom = lxml.html.fromstring(
                    template_with_logo)
                mydiv = __dom.get_element_by_id('footerDiv')
                mango = parser(brand.footer_html, footer_data)
                myhtml = lxml.html.fromstring(
                    mango)
                mydiv.insert(0, myhtml)
                template_with_logo = lxml.html.tostring(__dom)
                template_with_logo = template_with_logo.decode()
                print(type(template_with_logo))
                # template_with_logo = template_with_logo.replace(
                #     "footerBottom", parser(brand.footer_html, footer_data))
            else:
                raise BadRequest("Brand don't have saved footer html")
        else:
            template_with_logo = page.bp.raw_html

        editors = User.query.join(PageEditors).order_by(
            PageEditors.updated_at.desc()).filter(PageEditors.page_id == page.id).all()
        return {
            "page_name": str(page.page_name) if page.page_name else "",
            "template_id": str(page.template_id),
            "template_html": template_with_logo,
            "raw_template": page.bp.raw_html if page.template_raw_html == None else page.template_raw_html,
            "page_data": data_item,
            "thumbnail_image": page.thumbnail_image,
            "active": page.active,
            "category": str(page.category),
            "editors": editors
        }
    except Exception as e:
        config.logging.warning(
            f"api: get page by id : Not Able to return Data.. {e}")
        raise BadRequest(f"Not Able to return Data.{e}")


def delete_block(page_id, block_no):
    try:
        uuid.UUID(page_id)
    except Exception as e:
        config.logging.warning(f"api: delete : pageid not valid. {e}")
        raise BadRequest("This page id not valid.")
    try:
        block = PageData.query.filter_by(
            page_id=page_id, block_no=block_no).first()
        if not block:
            raise BadRequest("Block not found to delete")
        db.session.delete(block)
        db.session.commit()
        return block, HTTPStatus.OK
    except:
        config.logging.warning(f"api: brand page services: not able to delete")
        raise BadRequest(" data not able to delete")


def delete_page(page_id):
    try:
        uuid.UUID(page_id)
    except Exception as e:
        config.logging.warning(
            f"api: delete page id : Invalid Submission Id. {e}")
        raise BadRequest("This page id not valid.")
    page = BrandPages.query.filter_by(id=page_id).first()
    if not page:
        raise BadRequest("Page not found!")
    for block in page.page_data:
        delete_block(page_id=page_id, block_no=block.block_no)
    db.session.delete(page)
    log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=page.brand_id,
                   message="has deleted one issue", created_at=get_time(), date=date.today())
    db.session.add(log)
    db.session.commit()
    return {"message": "Page delete successfully"}, HTTPStatus.OK


def raw_html_template(template_id):
    template = Template.query.filter_by(id=template_id).first()
    if not template:
        raise BadRequest("template not found with given id")
    raw_html = template.raw_html
    return raw_html


def raw_html_Storye_template(template_id):
    template = StoryTemplate.query.filter_by(id=template_id).first()
    if not template:
        raise BadRequest("template not found with given id")
    raw_html = template.raw_html
    return raw_html


def get_all_draft_or_published_pages(brand_id, status, search, category, page, limit):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get brand id not valid. {e}")
        raise BadRequest("get brand id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand page services: Brand not available!")
        raise BadRequest("Brand not available!")
    if status:
        if not (status == "DRAFT" or status == "PUBLISHED" or status == "SHEDULED"):
            config.logging.warning(
                f"api: brand page services: please enter valid status!")
            raise BadRequest("Please enter valid status!")

    if category:
        if not (category == "General" or category == "Home" or category == "Terms" or category == "Privacy" or category == "System"):
            config.logging.warning(
                f"api: brand page services: please enter valid category!")
            raise BadRequest(
                "please enter valid category, General , Home , Privacy or Terms!")

    searchKey = "%{}%".format(search)
    mm = BrandPages.query.filter(BrandPages.brand_id == brand_id)
    if (status == "DRAFT" or status == "PUBLISHED" or status == "SHEDULED"):
        mm = mm.filter(BrandPages.status == status)
    if (category == "General" or category == "Home" or category == "Terms" or category == "Privacy" or category == "System"):
        mm = mm.filter(BrandPages.category == category)
    mm = mm.filter(or_(BrandPages.page_name.ilike(searchKey)))
    item = mm.order_by(BrandPages.updated_at.desc())

    paginated_data = item.paginate(page=page, per_page=limit)
    total_page = [page for page in paginated_data.iter_pages()]
    if not item:
        return {"items": []}, HTTPStatus.OK.value
    try:
        return {"items": [{"id": str(paginated_data.items[i].id), "category":paginated_data.items[i].category, "active":paginated_data.items[i].active, "brand_id":str(paginated_data.items[i].brand_id), "updated_at":str(paginated_data.items[i].updated_at), "page_name":str(paginated_data.items[i].page_name), "template_id":str(paginated_data.items[i].template_id), "total_block_count":paginated_data.items[i].total_block_count, "html": parser(raw_html_template(str(paginated_data.items[i].template_id)),
                                                                                                                                                                                                                                                                                                                                                                                                                                                          {"temp": [items.widget_page for items in getattr(paginated_data.items[i], 'page_data')]}),

                           "link":str(item[i].cdn_html_page_link).replace(f"{cur_app.config['BUCKET_BASE_URL']}{brand.fqdn}", f'https://{brand.fqdn}'), "filled_block_count":item[i].filled_block_count, "status":item[i].status, "editors": User.query.join(PageEditors).order_by(PageEditors.updated_at.desc()).filter(PageEditors.page_id == paginated_data.items[i].id).all(), "thumbnail_image":paginated_data.items[i].thumbnail_image} for i in

                          range(len(paginated_data.items))],
                "total_pages": total_page if total_page else [],
                "pages": paginated_data.pages,
                "has_next": paginated_data.has_next,
                "has_prev": paginated_data.has_prev,
                "page": paginated_data.page,
                "per_page": paginated_data.per_page,
                "total": paginated_data.total,
                }, HTTPStatus.OK
    except Exception as e:
        config.logging.error(
            f"api: get get all draft and published : not able to return ecouse at some point of database template Id not found please remove old pages . {e}")
        raise BadRequest(
            f"Not able to return becouse at some point of database template Id not found please remove old pages. {e}")


def get_all_system_pages(category, page, limit):
    if category:
        if not (category == "General" or category == "Home" or category == "Terms" or category == "Privacy" or category == "System"):
            config.logging.warning(
                f"api: brand page services: please enter valid category!")
            raise BadRequest(
                "please enter valid category, General , Home , Privacy or Terms!")

    pages = BrandPages.query.filter(
        BrandPages.status == "PUBLISHED", BrandPages.active == True)
    if category:
        pages = pages.filter(BrandPages.category == category, BrandPages.active == True).order_by(
            BrandPages.created_at.desc())
    paginated_data = pages.paginate(page=page, per_page=limit)
    total_page = [story for story in paginated_data.iter_pages()]
    if not pages:
        return {"items": []}, HTTPStatus.OK.value
    return {"items": paginated_data.items,
            "total_pages": total_page if total_page else [],
            "pages": paginated_data.pages,
            "has_next": paginated_data.has_next,
            "has_prev": paginated_data.has_prev,
            "page": paginated_data.page,
            "per_page": paginated_data.per_page,
            "total": paginated_data.total,
            }, HTTPStatus.OK


def preview_page(page_id):
    try:
        uuid.UUID(page_id)
    except Exception as e:
        config.logging.warning(
            f"api: get templatebyid : Invalid Submission Id. {e}")
        raise BadRequest("This page id not valid.")
    page = BrandPages.query.filter_by(id=page_id).first()
    if not page:
        config.logging.warning(
            f"api: brand page services: page is not available!")
        raise BadRequest("page not available!")
    brand = page.brand_page
    if not brand:
        config.logging.warning(
            f"api: brand page services: brand is not available!")
        raise BadRequest("brand not available!")
    temp = page.bp.raw_html
    if not temp:
        config.logging.warning(
            f"api: brand page services: template is not available!")
        raise BadRequest("template not available!")
    publishcss = page.bp.publish_css
    encoded_id = auth_s.dumps({"content_id": str(page.id)})
    if ("content_id" in temp) or ("logo_url" in temp) or ("footer_logo" in temp) or ("changecss" in temp):
        try:
            template_with_logo = temp.replace("logo_url", str(brand.white_theme_logo)).replace(
                "footer_logo", str(brand.black_theme_logo)).replace("changecss", str(publishcss)).replace("content_id", str(encoded_id)).replace("api_key", str(brand.email_api_key))
        except Exception as e:
            config.logging.error(f"not able to replace. {e}")
            raise BadRequest(f"This template id or brand id not valid. {e}")
    else:
        template_with_logo = page.bp.raw_html
    if not template_with_logo:
        config.logging.warning(
            f"api: brand page services: Template not available!")
        raise BadRequest("Template not available!")
    data_item = PageData.query.filter_by(
        page_id=page_id).order_by(PageData.block_no).all()
    if not data_item:
        raise BadRequest("Data Item not found in preview page api!")
    try:
        return{"page_id": page_id, "category": page.category, "active": page.active, "parsed_html_page": parser(template_with_logo, {"temp": [items.widget_page for items in data_item]})}
    except:
        config.logging.warning(
            f"api: brand page services: Not able to generate preview page!")
        raise BadRequest("Not able to generate preview page!")


def open_documnet(link):
    try:
        bucket = storage_client.get_bucket(cur_app.config["BUCKET_NAME"])
        data = bucket.blob(link).download_as_string()
        html = data.decode("utf-8")
        return {"data": html}
    except Exception as e:
        config.logging.warning(
            f"api: brand page services: page link not valid! {e}")
        raise BadRequest(f"page link is not valid {e}")


def get_all_contents(subdomain, page, limit, category):
    brand = Brand.query.filter_by(fqdn=subdomain).first()
    if not brand:
        raise BadRequest("Brand Not availabe by this subdomain!")
    # if searchKey:
    #     search = "%{}%".format(searchKey)
    #     paginated_data = BrandPages.query.order_by(
    #         BrandPages.created_at.desc()).filter(
    #         BrandPages.brand_id == brand.id,BrandPages.status=="PUBLISHED").filter(or_(BrandPages.page_name.ilike(search))).paginate(page=page, per_page=limit)
    #     objects = paginated_data.items
    # else:
    if category:
        if not (category == "General" or category == "Home" or category == "Terms" or category == "Privacy" or category == "System"):
            config.logging.warning(
                f"api: brand page services: please enter valid key!")
            raise BadRequest(
                "please enter valid key, General , Home , Privacy or Terms!")
        data = BrandPages.query.filter(
            BrandPages.brand_id == brand.id).filter(BrandPages.status == "PUBLISHED").filter(BrandPages.category == category).filter(BrandPages.active == True).order_by(BrandPages.created_at.desc())
    else:
        data = BrandPages.query.filter(
            BrandPages.brand_id == brand.id, BrandPages.status == "PUBLISHED", BrandPages.active == True).order_by(BrandPages.created_at.desc())
    if not data:
        raise BadRequest(f"Data not found with given sub domain")
    paginated_data = data.paginate(page=page, per_page=limit)
    obj = []
    for i in paginated_data.items:
        link = (i.cdn_html_page_link).replace(
            cur_app.config["BUCKET_BASE_URL"], "") if data else None
        html = open_documnet(link)
        obj.append(html)

    white_theme_logo = brand.white_theme_logo
    black_theme_logo = brand.black_theme_logo

    total_page = [page for page in paginated_data.iter_pages()]

    return {"items": obj,
            "total_pages": total_page if total_page else [],
            "white_theme_logo": white_theme_logo if white_theme_logo else None,
            "black_theme_logo": black_theme_logo if black_theme_logo else None,
            "has_next": paginated_data.has_next,
            "has_prev": paginated_data.has_prev,
            "page": paginated_data.page,
            "per_page": paginated_data.per_page,
            "total": paginated_data.total,
            }, HTTPStatus.OK.value


def duplicate_page(brand_id, page_id):
    try:
        uuid.UUID(page_id)
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"api: Get template by id : Invalid Submission Id. {e}")
        raise BadRequest(f"page id or brand id is not valid.")

    page = BrandPages.query.filter_by(id=page_id).first()
    if not page:
        config.logging.warning(
            f"api: brand page services: please enter valid page id!")
        raise BadRequest("please enter valid page id.. page not found!")

    page_seo = PageSeo.query.filter_by(page_id=page_id).first()
    if not page_seo:
        raise BadRequest("Page Seo not found with this page id")

    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand page services: please enter valid brand id or create brand!")
        raise BadRequest("please enter valid brand id.. brand not found!")

    l = []
    for i in page.page_data:
        block = {
            "block_no": i.block_no,
            "widget_name": i.widget_name,
            "widget_page": i.widget_page,
            "widget_type": i.widget_type,
            "updated": i.updated,
        }
        l.append(block)
    try:
        template_before = page.bp.raw_html if page.template_raw_html == None else page.template_raw_html
        draftcss = page.bp.draft_css
        replace_data = {"logo_url": str(brand.white_theme_logo), "footer_logo": str(brand.black_theme_logo), "changecss": str(draftcss), "seoiconlink": str(page_seo.icon), "seotitle": str(page_seo.title), "seodescription": str(page_seo.description),
                        "seopagelink": str(page_seo.page_link), "seoupdatedat": str(page_seo.created_at), "seopagetype": str(page_seo.page_type), "seofacebbokid": str(page_seo.facebook_publisher), "seocreatedat": str(page_seo.created_at), "seobannerimage": str(page_seo.banner_image), "seotwitterid": str(page_seo.twitter_id), "seogtag": str(cur_app.config["GTAG"]),"api_key":str(brand.email_api_key)}
        template_with_logo = raplace_text_in_template(
            template_before, replace_data)
        template_with_logo = parse_header_and_footer(
            brand_id, template_with_logo)
        template_with_logo = template_with_logo if isinstance(
            template_with_logo, str) else template_with_logo.decode()
    except Exception as e:
        config.logging.warning(f"Error in replacing seo. {e}")
        raise BadRequest(f"Error in Seo content replacement.")
    try:
        return {
            "template_id": str(page.template_id),
            "template_html": template_with_logo,
            "page_name": f"New {str(page.page_name)}",
            "page_data": l,
            "raw_template": page.bp.raw_html if page.template_raw_html == None else page.template_raw_html
        }
    except Exception as e:
        config.logging.warning(
            f"api: brand page services: Duplicate page not working due to {e}!")
        raise BadRequest("Error in Duplicating page!")
