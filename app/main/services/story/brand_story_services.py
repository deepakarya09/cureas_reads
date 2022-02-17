from app.main.gcp_clients.bucket import upload_html_blob_story
from app.main.models.brand_log import BrandLog
from app.main.models.story_app import BrandStory
from app.main.models.story_data import StoryData
from app.main.models.story_editors import StoryEditors
from app.main.models.story_seo import StorySeo
from app.main.models.story_template import StoryTemplate
import uuid
from flask_restplus._http import HTTPStatus
from werkzeug.exceptions import BadRequest
from app.main import config, db
from app.main.services import get_active_user, get_time
from flask import current_app as cur_app
from app.main.services.pages.brand_pages_service import fetch_seo_data_from_widget, raplace_text_in_template, raw_html_template, raw_html_Storye_template
from app.main.services.image_upload_services import upload_image_by_raw, upload_images_api
from app.main.services.parser_service import parser
from app.main.models.widgets import Widget
from app.main.models.brands import Brand
from app.main.config import driver
from app.main.models.user import User
from sqlalchemy import or_
from datetime import date
from itsdangerous import URLSafeTimedSerializer
auth_s = URLSafeTimedSerializer(config.Config.SECRET_KEY, "auth")


def save_story_data(story_data: dict):
    try:
        _p_data = StoryData()
        for key, value in story_data.items():
            if hasattr(_p_data, key):
                setattr(_p_data, key, value)
        db.session.add(_p_data)
        db.session.commit()
    except Exception as e:
        config.logging.error(f"Can't save your story : {story_data}")
        raise BadRequest(f"Can't save your story : {story_data}")


def issue_story_template_before_save(template_id):
    try:
        uuid.UUID(template_id)
    except Exception as e:
        config.logging.warning(
            f"api: Get template by id : Invalid Submission Id. {e}")
        raise BadRequest(f"Template id is not valid.")
    issue_template = StoryTemplate.query.filter_by(id=template_id).first()
    if not issue_template:
        raise BadRequest("Template not found please check template id.")
    replace_data = {"changecss": str(issue_template.draft_css), "seotitle": "Story", "seodescription": "This is demo issue template description",
                    "seopagetype": "story", "seofacebbokid": "#", "seocreatedat": str(get_time()), "seobannerimage": cur_app.config["DEFAULT_WIDGET_BLANK_IMAGE"], "seotwitterid": "demo", "seogtag": str(cur_app.config["GTAG"])}
    issued_template = raplace_text_in_template(
        issue_template.raw_html, replace_data)
    if not issued_template:
        config.logging.warning(
            f"api: issue template brand story: Error in replacing css and logo url")
        raise BadRequest(
            "Template not found. Please check brand logo or css file!")
    number_of_widgets = issue_template.block_count
    if not number_of_widgets:
        config.logging.warning(
            f"api: issue template brand story: Error not getting block count of issued template")
        raise BadRequest("Number of widgets is not available!")
    structure = issue_template.block_structure
    if not structure:
        config.logging.warning(
            f"api: Issue template brand story: Error not getting block structure of issued template")
        raise BadRequest(
            "Error not getting block structure of issued template!")
    if number_of_widgets != len(structure):
        raise BadRequest(
            "Block count is not equal to block structure of issued template.")
    try:
        story_data = [
            Widget.query.filter_by(name=structure[i]).first() for i in range(len(structure))]

        parsed_data = [
            {'block_no': i, 'widget_name': story_data[i].name, 'widget_type': story_data[i].type,
             'widget_page': parser(story_data[i].raw_html, story_data[i].default_data),
             'updated': False} for i in range(number_of_widgets)]
        template = StoryTemplate.query.filter_by(id=template_id).first()

        return {"story_name": "Story", "raw_template": template.raw_html, "template_html": issued_template if isinstance(issued_template, str) else issued_template.decode(),
                "story_data": parsed_data}, HTTPStatus.CREATED
    except Exception as e:
        config.logging.warning(
            f"api: brand story services:  Default Template can not render due to parsing error")
        raise BadRequest(
            f" Default template can not render due to parsing error")


def get_story(story_id):
    try:
        uuid.UUID(story_id)
    except Exception as e:
        config.logging.warning(
            f"api: get story by id : Invalid Submission Id. {e}")
        raise BadRequest("This story id not valid.")
    story = BrandStory.query.filter_by(id=story_id).first()
    if not story:
        raise BadRequest("This story id not valid.")
    data_item = StoryData.query.filter_by(
        story_id=story_id).order_by(StoryData.block_no).all()
    if not data_item:
        raise BadRequest("Data item not found for this story.")

    try:
        brand = story.brand_story
        template_before = story.bs.raw_html if story.template_raw_html == None else story.template_raw_html
        template_with_logo = ''
        if ("changecss" in template_before):
            try:
                template_with_logo = template_before.replace(
                    "changecss", str(story.bs.draft_css))
            except Exception as e:
                config.logging.error(f"not able to replace. {e}")
                raise BadRequest(
                    f"This template id or brand id not valid. {e}")
        else:
            template_with_logo = story.bs.raw_html

        editors = User.query.join(StoryEditors).order_by(
            StoryEditors.updated_at.desc()).filter(StoryEditors.story_id == story.id).all()
        return {
            "story_name": str(story.story_name) if story.story_name else "",
            "template_id": str(story.template_id),
            "template_html": template_with_logo,
            "raw_template": story.bs.raw_html if story.template_raw_html == None else story.template_raw_html,
            "story_data": data_item,
            "thumbnail_image": story.thumbnail_image,
            "active": story.active,
            "category": str(story.category),
            "editors": editors
        }
    except Exception as e:
        config.logging.warning(
            f"api: get Story by id : Not Able to return Data.. {e}")
        raise BadRequest(f"Not Able to return Data.{e}")


def post_story_publish_and_draft(brand_id, data):
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
    number_of_widgets = len(data['story_data'])
    issue_template = StoryTemplate.query.filter_by(
        id=data['template_id']).first()
    if not issue_template:
        raise BadRequest(
            "Template not available in database. Please check template id.")
    block_count = issue_template.block_count
    if not block_count:
        config.logging.warning(
            f"api: issue template brand story: Error not getting block count of issued template")
        raise BadRequest("Error not getting block count of issued template!")
    count = 0
    for i in data['story_data']:
        if i["updated"] == True:
            count = count+1
    StoryStatus = data['status']
    story_name = data['story_name'] if data['story_name'] else 'Story'

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

    if StoryStatus == 'PUBLISHED':
        if count != block_count:
            config.logging.warning(
                f"api: user try to publish without fill all block")
            raise BadRequest("You cant publish with empty blocks")
    if "story_id" in data:
        raise BadRequest(
            "Please call update API story id available in given data")
    else:
        try:
            new_story_create = BrandStory(id=uuid.uuid4(), brand_id=brand_id, story_name=story_name,
                                          template_id=data['template_id'], template_raw_html=data['raw_template'] if "raw_template" in data else issue_template.raw_html, total_block_count=block_count, filled_block_count=count, status=data['status'], created_at=get_time(), updated_at=get_time(), category=data['category'], active=True)
            db.session.add(new_story_create)
            db.session.commit()

            parsed_data = [
                {'id': str(uuid.uuid4()), 'story_id': str(new_story_create.id), 'block_no': i, 'widget_name': data['story_data'][i]['widget_name'], 'widget_type': data['story_data'][i]['widget_type'], 'widget_page': data['story_data'][i]['widget_page'], 'updated': data['story_data'][i]['updated']} for i in range(block_count)]

            for d in parsed_data:
                save_story_data(d)
            story = BrandStory.query.filter_by(id=new_story_create.id).first()
            if not story:
                raise BadRequest(
                    "story not found in databse. Please check story id.")
            try:
                add_editors = StoryEditors(
                    story_id=story.id, user_id=get_active_user())
                db.session.add(add_editors)
                db.session.commit()
            except Exception as e:
                raise BadRequest(f"Error in adding editors {e}")
            try:
                story_seo = StorySeo(id=uuid.uuid4(), story_id=story.id, icon=check.white_theme_logo, title=seo["seo_title"],
                                     description=seo["seo_description"], story_link="https://" + str(check.fqdn), story_type=seo["story_type"] if "story_type" in seo else "Story", banner_image=banner_link if banner_link != '' else '#', twitter_id=seo["twitter_id"] if "twitter_id" in seo else "#", facebook_publisher=seo["facebook_publisher"] if "facebook_publisher" in data else "#")
                db.session.add(story_seo)
                log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=brand_id,
                               message="has created new story", created_at=get_time(), date=date.today())
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                raise BadRequest(f"Error in saving seo for story {e}")

            data_item = StoryData.query.filter_by(
                story_id=new_story_create.id).order_by(StoryData.block_no).all()
            if not data_item:
                raise BadRequest(
                    "Data of story is not found in databse. Please create new story.")
            template_before = StoryTemplate.query.filter_by(
                id=new_story_create.template_id).first()
            template_html = data['raw_template'] if "raw_template" in data else template_before.raw_html
            encoded_id = auth_s.dumps({"content_id": str(story.id)})
            replace_data = {"content_id": str(encoded_id), "changecss": str(template_before.draft_css), "seoiconlink": str(story_seo.icon), "seotitle": str(story_seo.title), "seodescription": str(story_seo.description),
                            "seopagelink": str(story_seo.story_link), "seopagetype": str(story_seo.story_type), "seofacebbokid": str(story_seo.facebook_publisher), "seocreatedat": str(story_seo.created_at), "seobannerimage": str(story_seo.banner_image), "seotwitterid": str(story_seo.twitter_id), "seogtag": str(cur_app.config["GTAG"])}
            template_with_logo = raplace_text_in_template(
                template_html, replace_data)
            if data['status'] == "PUBLISHED":
                try:
                    if story.story_link == None:
                        raw = data['raw_template'] if "raw_template" in data else template_before.raw_html
                        encoded_id = auth_s.dumps(
                            {"content_id": str(story.id)})
                        replace_data = {"content_id": str(encoded_id), "changecss": str(template_before.publish_css), "seoiconlink": str(story_seo.icon), "seotitle": str(story_seo.title), "seodescription": str(story_seo.description),
                                        "seopagelink": str(story_seo.story_link), "seoupdatedat": str(story_seo.updated_at), "seopagetype": str(story_seo.story_type), "seofacebbokid": str(story_seo.facebook_publisher), "seocreatedat": str(story_seo.created_at), "seobannerimage": str(story_seo.banner_image), "seotwitterid": str(story_seo.twitter_id), "seogtag": str(cur_app.config["GTAG"])}
                        raw_html = raplace_text_in_template(raw, replace_data)

                        parsed_html = parser(raw_html,
                                             {"temp": [items.widget_page for items in data_item]})

                        if story.story_name:
                            webname = (
                                story.story_name.replace(" ", "")).lower()
                        else:
                            raise BadRequest(
                                "story name not found in selected story")
                        if check.name:
                            brand_fqdn = (check.fqdn.replace(" ", "")).lower()
                        else:
                            raise BadRequest(
                                "brand name not found of active brand")
                        link = upload_html_blob_story(bucket_name=cur_app.config["BUCKET_NAME"],
                                                      destination_blob_name=str(
                            webname) + ".html",
                            string_data=parsed_html, date=story.created_at, brand_obj=check)

                        setattr(story, "story_link", link)

                        try:
                            driver.get(str(link+"?ignoreCache=1"))
                            driver.set_window_size('1440', '1080')
                            screenshot = driver.get_screenshot_as_base64()
                            raw_image = f"data:image/png;base64,{screenshot}"
                            image_link = upload_image_by_raw(
                                raw_image, brand_id)
                            setattr(story, "thumbnail_image", image_link)
                        except Exception as e:
                            config.logging.error(
                                f"Error in taking screen short. {e}")
                            print(f"Error in taking screen short. {e}")
                            raise BadRequest(
                                f"Error in taking screen short. {e}")

                    l = story.story_link
                    baseurl = cur_app.config["BUCKET_BASE_URL"]
                    l = l.replace(
                        f'{baseurl}{(check.fqdn).lower()}', f'https://{check.fqdn}')
                    setattr(story_seo, "story_link", l)
                    db.session.commit()
                    return {'id': str(story.id), 'link': l, 'thumbnail_image': story.thumbnail_image, 'story_name': story.story_name, "template_html": template_with_logo, "raw_template": story.template_raw_html, 'template_id': str(story.template_id), 'story_data': data_item, "status": story.status, "category": story.category, "active": story.active}, HTTPStatus.CREATED
                except Exception as e:
                    config.logging.warning(
                        f"api: brand story services:  Not able to generate story link {e}")
                    raise BadRequest(f" Not able to generate story link {e}")

            return {'id': str(story.id), 'story_name': story.story_name, "template_html": template_with_logo, "raw_template": story.template_raw_html, 'template_id': str(story.template_id), 'story_data': data_item, "status": story.status, "category": story.category, "active": story.active}, HTTPStatus.CREATED
        except Exception as e:
            config.logging.error(
                f"api: save and publish : Not able to create new story. {e}")
            raise BadRequest(f"Not able to create new story.{e}")


def update_story_by_id(brand_id, story_id, data):
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
    story = BrandStory.query.filter_by(id=story_id).first()
    if not story:
        raise BadRequest("Story not found with this story id")
    story_seo = StorySeo.query.filter_by(story_id=story_id).first()
    if not story_seo:
        raise BadRequest("Story Seo not found with this story id")
    number_of_widgets = len(data['story_data'])
    issue_template = StoryTemplate.query.filter_by(
        id=data['template_id']).first()
    if not issue_template:
        raise BadRequest(
            "Template not available in database. Please check template id.")
    block_count = issue_template.block_count
    if not block_count:
        config.logging.warning(
            f"api: issue template brand story: Error not getting block count of issued template")
        raise BadRequest("Error not getting block count of issued template!")
    count = 0
    for i in data['story_data']:
        if i["updated"] == True:
            count = count+1
    StoryStatus = data['status']
    story_name = data['story_name'] if data['story_name'] else 'Story'

    if StoryStatus == 'PUBLISHED':
        if count != block_count:
            config.logging.warning(
                f"api: user try to publish without fill all block")
            raise BadRequest("You cant publish with empty blocks")
    if story:
        try:
            check_editors = StoryEditors.query.filter(
                StoryEditors.story_id == story_id, StoryEditors.user_id == get_active_user()).first()
            log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=brand_id,
                           message="has updated story", created_at=get_time(), date=date.today())
            db.session.add(log)
            if check_editors:
                check_editors.updated_at = get_time()
            else:
                add_editors = StoryEditors(
                    user_id=get_active_user(), story_id=story_id)
                db.session.add(add_editors)
            db.session.commit()
        except Exception as e:
            raise BadRequest("Error in adding editors of story.")
        try:
            story.story_name = story_name
            story.status = StoryStatus
            story.category = data['category']
            story.filled_block_count = count
            story.active = True
            story.template_raw_html = data['raw_template']
            story.updated_at = get_time()

            data_item = StoryData.query.filter_by(
                story_id=story_id).order_by(StoryData.block_no).all()

            db.session.add(story)
            for i in range(len(data_item)):
                data_item[i].widget_name = data['story_data'][i]['widget_name']
                data_item[i].widget_page = data['story_data'][i]['widget_page']
                data_item[i].updated = data['story_data'][i]['updated']

                db.session.add(data_item[i])
                db.session.commit()
        except Exception as e:
            config.logging.error(
                f"api: save and publish : Not able to update data due to. {e}")
            raise BadRequest(f"No able to update data due to.{e}")
    template_before = data['raw_template'] if "raw_template" in data else issue_template.raw_html
    draftcss = story.bs.draft_css
    encoded_id = auth_s.dumps({"content_id": str(story.id)})
    replace_data = {"content_id": str(encoded_id), "changecss": str(draftcss), "seoiconlink": str(story_seo.icon), "seotitle": str(story_seo.title), "seodescription": str(story_seo.description),
                    "seopagelink": str(story_seo.story_link), "seoupdatedat": str(story_seo.created_at), "seopagetype": str(story_seo.story_type), "seofacebbokid": str(story_seo.facebook_publisher), "seocreatedat": str(story_seo.created_at), "seobannerimage": str(story_seo.banner_image), "seotwitterid": str(story_seo.twitter_id), "seogtag": str(cur_app.config["GTAG"])}
    template_with_logo = raplace_text_in_template(
        template_before, replace_data)
    try:
        if count == number_of_widgets:
            if data['status'] == "PUBLISHED":
                setattr(story, 'published_at', get_time())
                try:
                    raw = data['raw_template'] if "raw_template" in data else issue_template.raw_html
                    publishcss = story.bs.publish_css
                    encoded_id = auth_s.dumps({"content_id": str(story.id)})
                    replace_data = {"content_id": str(encoded_id), "changecss": str(publishcss), "seoiconlink": str(story_seo.icon), "seotitle": str(story_seo.title), "seodescription": str(story_seo.description),
                                    "seopagelink": str(story_seo.story_link), "seoupdatedat": str(story_seo.created_at), "seopagetype": str(story_seo.story_type), "seofacebbokid": str(story_seo.facebook_publisher), "seocreatedat": str(story_seo.created_at), "seobannerimage": story_seo.banner_image, "seotwitterid": story_seo.twitter_id, "seogtag": str(cur_app.config["GTAG"])}
                    raw_html = raplace_text_in_template(raw, replace_data)
                    parsed_html = parser(raw_html,
                                         {"temp": [items.widget_page for items in data_item]})

                    if story.story_name:
                        webname = (story.story_name.replace(" ", "")).lower()
                    else:
                        raise BadRequest(
                            "story name not found in selected story")
                    if check.name:
                        brand_fqdn = (check.fqdn.replace(" ", "")).lower()
                    else:
                        raise BadRequest(
                            "brand name not found of active brand")
                    link = upload_html_blob_story(bucket_name=cur_app.config["BUCKET_NAME"], destination_blob_name=str(webname) + ".html",
                                                  string_data=parsed_html, date=story.created_at, brand_obj=check)

                    setattr(story, "story_link", link)

                    try:
                        driver.get(str(link+"?ignoreCache=1"))
                        driver.set_window_size('1440', '1080')
                        screenshot = driver.get_screenshot_as_base64()
                        raw_image = f"data:image/png;base64,{screenshot}"
                        image_link = upload_image_by_raw(raw_image, brand_id)
                        setattr(story, "thumbnail_image", image_link)
                    except Exception as e:
                        config.logging.error(
                            f"Error in taking screen short. {e}")
                        print(f"Error in taking screen short. {e}")
                        raise BadRequest(
                            f"Error in taking screen short. {e}")

                    l = story.story_link
                    baseurl = cur_app.config["BUCKET_BASE_URL"]
                    l = l.replace(f'{baseurl}{(check.fqdn).lower()}',
                                  f'https://{check.fqdn}')
                    setattr(story_seo, "story_link", l)
                    db.session.commit()

                    return {'id': str(story.id), 'link': l, 'story_name': story.story_name, "thumbnail_image": story.thumbnail_image, "template_html": template_with_logo, "raw_template": story.template_raw_html, 'template_id': str(story.template_id), 'story_data': data_item, "status": story.status, "category": story.category, "active": story.active}, HTTPStatus.CREATED
                except Exception as e:
                    config.logging.warning(
                        f"api: brand story services:  Not able to generate story link {e}")
                    raise BadRequest(" Not able to generate story link ")
    except Exception as e:
        config.logging.warning(
            f"api: brand story services:  data not able to publish without story id code")
        raise BadRequest(f"  data not able to publish with story id code{e}")
    try:
        return {'id': str(story.id), 'story_name': story.story_name, "template_html": template_with_logo, "raw_template": story.template_raw_html, 'template_id': str(story.template_id), 'story_data': data_item, "status": story.status, "category": story.category, "active": story.active}, HTTPStatus.CREATED
    except:
        config.logging.warning(
            f"api: brand story services:  data not able to save in draft without story id code")
        raise BadRequest(
            "data not able to save in draft without story id code")


def get_all_draft_or_published_story(brand_id, status, active, search, category, page, limit):
    try:
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(f"api: get brand id not valid. {e}")
        raise BadRequest("get brand id not valid.")
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand story services: Brand not available!")
        raise BadRequest("Brand not available!")
    if status:
        if not (status == "DRAFT" or status == "PUBLISHED" or status == "SHEDULED"):
            config.logging.warning(
                f"api: brand story services: please enter valid status!")
            raise BadRequest("Please enter valid status!")

    searchKey = "%{}%".format(search)
    mm = BrandStory.query.filter(BrandStory.brand_id == brand_id)
    if (status == "DRAFT" or status == "PUBLISHED" or status == "SHEDULED"):
        mm = mm.filter(BrandStory.status == status)
    if category:
        mm = mm.filter(BrandStory.category == category)
    if active:
        mm = mm.filter(BrandStory.active == active)
    mm = mm.filter(or_(BrandStory.story_name.ilike(searchKey)))
    item = mm.order_by(BrandStory.updated_at.desc())

    paginated_data = item.paginate(page=page, per_page=limit)
    total_page = [story for story in paginated_data.iter_pages()]
    if not item:
        return {"items": []}, HTTPStatus.OK.value
    try:
        return {"items": [{"id": str(paginated_data.items[i].id), "category":paginated_data.items[i].category, "active":paginated_data.items[i].active, "brand_id":str(paginated_data.items[i].brand_id), "updated_at":str(paginated_data.items[i].updated_at), "story_name":str(paginated_data.items[i].story_name), "template_id":str(paginated_data.items[i].template_id), "total_block_count":paginated_data.items[i].total_block_count, "html": parser(raw_html_Storye_template(str(paginated_data.items[i].template_id)),
                                                                                                                                                                                                                                                                                                                                                                                                                                                            {"temp": [items.widget_page for items in getattr(paginated_data.items[i], 'story_data')]}),

                           "link":str(item[i].story_link).replace(f"{cur_app.config['BUCKET_BASE_URL']}{brand.fqdn}", f'https://{brand.fqdn}'), "filled_block_count":item[i].filled_block_count, "status":item[i].status, "editors": User.query.join(StoryEditors).order_by(StoryEditors.updated_at.desc()).filter(StoryEditors.story_id == paginated_data.items[i].id).all(), "thumbnail_image":paginated_data.items[i].thumbnail_image} for i in

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
            f"api: get get all draft and published : not able to return ecouse at some point of database template Id not found please remove old story . {e}")
        raise BadRequest(
            f"Not able to return becouse at some point of database template Id not found please remove old story. {e}")


def remove_story_from_search(story_id):
    try:
        uuid.UUID(story_id)
    except Exception as e:
        config.logging.warning(f"api: get story id not valid. {e}")
        raise BadRequest("get story id not valid.")

    story = BrandStory.query.filter_by(id=story_id).first()

    if not story:
        config.logging.warning(
            f"api: brand story services: story not available!")
        raise BadRequest("story not available!")
    story.active = False
    log = BrandLog(id=uuid.uuid4(), user_id=get_active_user(), brand_id=story.brand_id,
                   message="has removed one story", created_at=get_time(), date=date.today())
    db.session.add(log)
    db.session.commit()
    return {"message": "story removed successfully from search results you can still backup."}


def duplicate_story(brand_id, story_id):
    try:
        uuid.UUID(story_id)
        uuid.UUID(brand_id)
    except Exception as e:
        config.logging.warning(
            f"api: deplicate story : Invalid Submission Id. {e}")
        raise BadRequest(f"story id or brand id is not valid.")

    story = BrandStory.query.filter_by(id=story_id).first()
    if not story:
        config.logging.warning(
            f"api: brand story services: please enter valid story id!")
        raise BadRequest("please enter valid story id.. story not found!")

    story_seo = StorySeo.query.filter_by(story_id=story_id).first()
    if not story_seo:
        raise BadRequest("Story Seo not found with this story id")

    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        config.logging.warning(
            f"api: brand story services: please enter valid brand id or create brand!")
        raise BadRequest("please enter valid brand id.. brand not found!")

    l = []
    for i in story.story_data:
        block = {
            "block_no": i.block_no,
            "widget_name": i.widget_name,
            "widget_page": i.widget_page,
            "widget_type": i.widget_type,
            "updated": i.updated,
        }
        l.append(block)
    try:
        template_before = story.bs.raw_html if story.template_raw_html == None else story.template_raw_html
        draftcss = story.bs.draft_css
        replace_data = {"changecss": str(draftcss), "seoiconlink": str(story_seo.icon), "seotitle": str(story_seo.title), "seodescription": str(story_seo.description),
                        "seopagelink": str(story_seo.story_link), "seoupdatedat": str(story_seo.created_at), "seopagetype": str(story_seo.story_type), "seofacebbokid": str(story_seo.facebook_publisher), "seocreatedat": str(story_seo.created_at), "seobannerimage": str(story_seo.banner_image), "seotwitterid": str(story_seo.twitter_id), "seogtag": str(cur_app.config["GTAG"])}
        template_with_logo = raplace_text_in_template(
            template_before, replace_data)
    except Exception as e:
        config.logging.warning(f"Error in replacing seo story. {e}")
        raise BadRequest(f"Error in Seo content replacement story duplicate.")
    try:
        return {
            "template_id": str(story.template_id),
            "template_html": template_with_logo,
            "story_name": f"New {str(story.story_name)}",
            "story_data": l,
            "raw_template": story.bs.raw_html if story.template_raw_html == None else story.template_raw_html
        }
    except Exception as e:
        config.logging.warning(
            f"api: brand story services: Duplicate story not working due to {e}!")
        raise BadRequest("Error in Duplicating story!")


def get_all_system_story(category, page, limit):
    if category:
        if not (category == "General" or category == "Home" or category == "Terms" or category == "Privacy" or category == "System"):
            config.logging.warning(
                f"api: brand page services: please enter valid category!")
            raise BadRequest(
                "please enter valid category, General , Home , Privacy or Terms!")

    pages = BrandStory.query.filter(
        BrandStory.status == "PUBLISHED", BrandStory.active == True)
    if category:
        pages = pages.filter(BrandStory.category == category).order_by(
            BrandStory.created_at.desc())
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
