from http import HTTPStatus
import uuid
from werkzeug.exceptions import BadRequest
from app.main.models.brands import Brand
from app.main.models.page_component import PageComponent
from app.main import config, db
from app.main.services import get_time
from app.main.services.parser_service import parser


def get_all_page_component(brand_id, category):
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand not found id database. Please check brand id")
    if not category:
        raise BadRequest("Please add category to get parsed results")
    default_html = PageComponent.query.order_by(
        PageComponent.updated_at.desc()).filter(PageComponent.category == category).all()
    if category == "navbar":
        if brand.navbar_html:
            default_html_active = brand.navbar_html
            active_id = brand.navbar_id
        else:
            raise BadRequest("Please add navbar html to the brand")
        json_data = {
            "brand_white_logo": brand.white_theme_logo if brand.white_theme_logo else "#",
            "home_page_link": f"https://{brand.fqdn}"
        }
    if category == "footer":
        if brand.footer_html:
            default_html_active = brand.footer_html
            active_id = brand.footer_id
        else:
            raise BadRequest("Please add footer html to the brand")
        json_data = {
            "brand_black_logo": brand.black_theme_logo if brand.black_theme_logo else "#",
            "facebook_link": brand.facebook_url if brand.facebook_url else "#",
            "insta_link": brand.instagram_url if brand.instagram_url else "#",
            "twitter_link": brand.twitter_url if brand.twitter_url else "#"
        }
    cssLink = PageComponent.query.filter(
        PageComponent.category == "cssLink").first()
    active = PageComponent.query.filter(PageComponent.id == active_id).first()
    if not active:
        raise BadRequest(
            "Active brand navbar and footer id dosen't match with component id")
    items = []
    active_data = {
        "id": active.id,
        "default_html": default_html_active,
        "parsed_html": parser(default_html_active, json_data),
        "name": active.name,
        "active": True
    }
    items.append(active_data)
    if default_html:
        for i in range(len(default_html)):
            data = {
                "id": default_html[i].id,
                "default_html": default_html[i].data,
                "parsed_html": parser(default_html[i].data, json_data),
                "name": default_html[i].name,
                "active": False
            }
            items.append(data)
    return {"items": items, "cssLink": cssLink.data}, HTTPStatus.OK


def put_brand_page_component(brand_id, category, data):
    brand = Brand.query.filter_by(id=brand_id).first()
    if not brand:
        raise BadRequest("Brand not found id database. Please check brand id")
    if not (category == "navbar" or category == "footer"):
        raise BadRequest("Please add category navbar or footer")
    if "edited_html" not in data:
        raise BadRequest("Please add edited_html in data")
    if "id" not in data:
        raise BadRequest("Please add id data")
    try:
        if category == "navbar":
            brand.navbar_html = data['edited_html']
            brand.navbar_id = data['id']
        if category == "footer":
            brand.footer_html = data["edited_html"]
            brand.footer_id = data['id']
        db.session.commit()
        return {"message": "Data updated successfully"}, HTTPStatus.OK
    except Exception as e:
        config.logging.error(f"error in adding component to brand .{e}")
        raise BadRequest(f"error in adding component to brand.")


def post_page_component(data):
    if "data" not in data and "category" not in data and "name" not in data:
        raise BadRequest("Please add all required data to add in database")
    if 'active' in data:
        if data['active'] == True:
            check = PageComponent.query.filter(PageComponent.category == data['category']).filter(
                PageComponent.active == True).first()
            if check:
                check.active = False
                db.session.commit()
    try:
        add_page_component = PageComponent(
            id=uuid.uuid4(),
            name=data['name'],
            category=data['category'],
            data=data['data'],
            active=data['active'] if 'active' in data else False
        )
        db.session.add(add_page_component)
        db.session.commit()
        return add_page_component, HTTPStatus.CREATED
    except Exception as e:
        config.logging.error(f"error in adding component to brand .{e}")
        raise BadRequest(f"error in adding component to brand.")


def update_page_component(component_id, data):
    component = PageComponent.query.filter_by(id=component_id).first()
    if not component:
        raise BadRequest(
            "Error please check page component Id, Page Component not found in data:")
    try:
        for key, value in data.items():
            if getattr(component, key) != value:
                setattr(component, key, value)
        setattr(component, "updated_at", get_time())
    except Exception as e:
        config.logging.critical(f"Failed to updated page component:{e}")
        raise BadRequest("Update Failed")
    db.session.commit()
    return component, HTTPStatus.OK.value


def get_page_component(component_id):
    component = PageComponent.query.filter_by(id=component_id).first()
    if not component:
        raise BadRequest(
            "Page Component not found id database. Please check page component id")
    return component, HTTPStatus.OK


def delete_page_component(component_id):
    component = PageComponent.query.filter_by(id=component_id).first()
    if not component:
        raise BadRequest(
            "Page Component not found id database. Please check page component id")
    try:
        db.session.delete(component)
        db.session.commit()
        return {"message": "Successfully deleted"}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(f"Failed to updated page component:{e}")
        raise BadRequest("Update Failed")


def component_to_all_brand():
    navbar = PageComponent.query.filter(PageComponent.category == "navbar").filter(
        PageComponent.active == True).first()
    if not navbar:
        raise BadRequest("not have any active navbar in componnent")
    footer = PageComponent.query.filter(PageComponent.category == "footer").filter(
        PageComponent.active == True).first()
    if not footer:
        raise BadRequest("not have any active footer in componnent")
    try:
        Brand.query.update({Brand.navbar_html: navbar.data})
        Brand.query.update({Brand.navbar_id: navbar.id})
        Brand.query.update({Brand.footer_html: footer.data})
        Brand.query.update({Brand.footer_id: footer.id})
        db.session.commit()
        return {"message": "Successfully addedd"}, HTTPStatus.OK
    except Exception as e:
        config.logging.critical(f"Failed to add html to all brand script:{e}")
        raise BadRequest(f"Error in updating all brand navbar and footer {e}")
