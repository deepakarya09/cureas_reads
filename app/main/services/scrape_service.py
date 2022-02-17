import requests
from http import HTTPStatus
from bs4 import BeautifulSoup
from werkzeug.exceptions import BadRequest
from app.main import config
from flask import current_app as cur_app
import logging
from app.main.config import driver
scrape_logger = logging.getLogger(__name__)
scrape_logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(message)s')

file_handler = logging.FileHandler('log/scrape.log')
file_handler.setFormatter(formatter)

scrape_logger.addHandler(file_handler)


def replace_xml_key(key):
    return key.replace("&#39;", "'").replace("&quot;", '"').replace('&gt;', '>').replace('&amp;', '&').replace('&lt;',
                                                                                                               '<')


def get_data(page):
    try:
        req = requests.get(page['site_link'], headers={
                           'User-Agent': 'Mozilla/5.0'}, timeout=20)
    except requests.exceptions.Timeout:
        raise BadRequest(f"This site is not supported by platform")
    except Exception as e:
        config.logging.info(f"Exception:{e}:article is not reachable.")
        raise BadRequest(f"article is not reachable.")
    # domain = (page['site_link']).split('/')
    # basename = '/'.join(domain[:3])
    try:
        soup = BeautifulSoup(req.content, "lxml")
    except Exception as e:
        raise BadRequest("Webpage XML parsing Failed.")

    title = soup.find("meta", property="og:title")
    description = soup.find("meta", property="og:description")
    canonical_link = soup.find("meta", property="og:url")
    image_link = soup.find("meta", property="og:image")
    content_type = soup.find("meta", property="og:type")
    site_name = soup.find("meta", property="og:site_name")
    favicon_icon_link = soup.find("link", rel="shortcut icon")
    if favicon_icon_link is None:
        favicon_icon_link = soup.find("link", rel="icon")
    if favicon_icon_link is None:
        favicon_icon_link = soup.find("link", rel="Shortcut Icon")
    valid = False
    try:
        icon = requests.get(favicon_icon_link, headers={
                            'User-Agent': 'Mozilla/5.0'}, timeout=28)
        if icon:
            valid = True
    except:
        pass

    return {
        "title": replace_xml_key(title['content']) if title else "",
        "description": replace_xml_key(description['content']) if description else "",
        "canonical_link": canonical_link["content"] if canonical_link else "",
        "image_link": image_link["content"] if image_link else "",
        "type": replace_xml_key(content_type["content"]) if content_type else "",
        "site_name": replace_xml_key(site_name["content"]) if site_name else "",
        "favicon_icon_link": favicon_icon_link["href"] if valid == True else cur_app.config["DEFAULT_WIDGET_BLANK_IMAGE"]
    }, HTTPStatus.OK.value


def generate_screnshot_of_element(data):

    try:
        window_width = "1440"
        window_height = "1080"
        try:
            req = requests.get(data['site_link'], headers={
                'User-Agent': 'Mozilla/5.0'}, timeout=20)
        except requests.exceptions.Timeout:
            raise BadRequest(f"This site is not supported by platform")
        except Exception as e:
            config.logging.info(f"Exception:{e}:article is not reachable.")
            raise BadRequest(f"article is not reachable.")
        driver.implicitly_wait(4)
        driver.get(
            str(data['site_link']))
        driver.implicitly_wait(10)
        if data['device'] == "MOBILE":
            window_width = "370"
            window_height = "640"
        if data['device'] == "TABLET":
            window_width = "600"
            window_height = "1024"
        if data['device'] == "DESKTOP":
            window_width = "1440"
            window_height = "1080"
        driver.set_window_size(window_width, window_height)
        CSS_TAG = data.get("css_id", "html")
        if CSS_TAG == 'html' or CSS_TAG == 'body':
            selected_div = driver.find_element_by_tag_name(CSS_TAG)
        else:
            selected_div = driver.find_element_by_id(CSS_TAG)
        image_string = ""
        if data.get("scroll_screenshot", False):

            height = int(selected_div.size['height'] if data.get(
                "scroll_Screenshot ", False) else window_height)
            driver.set_window_size(window_width, str(height + 300))
            return {"data": selected_div.screenshot_as_base64}
        else:
            driver.set_window_size(window_width, window_height)
            return {"data": driver.get_screenshot_as_base64()}

    except Exception as e:
        raise BadRequest("Failed to get Screenshot ")
