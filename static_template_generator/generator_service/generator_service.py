import calendar
import os
import random
import time
import uuid

import requests
from jinja2 import Environment, FileSystemLoader

from app.main import config
from app.main import db
from app.main.models.contents import Content
from app.main.models.meta_static_pages import GeneratedPages
from app.main.models.page_counts import PageCount
from app.manage import app
from static_template_generator import conf_var
from static_template_generator.gcp_storage.gcp_storage import upload_from_directory

template_env = Environment(loader=FileSystemLoader(searchpath="./"))

min_page = conf_var.min_page
max_page = conf_var.max_page


def template_writer(file_name, data, template):
    template = template_env.get_template(template)
    with open(f"{conf_var.local_html_page_directory}/{file_name}", "w", encoding='utf-8') as output_file:
        output_file.write(
            template.render(
                items=data
            )
        )


def fill_meta_generated_table(page_name, layout_name, storage_location, country):
    with app.app_context():
        page = GeneratedPages(id=uuid.uuid4(), page_name=page_name, layout_name=layout_name,
                              created_at=calendar.timegm(time.gmtime()),
                              expires_at=86400 + calendar.timegm(time.gmtime()),
                              storage_location=storage_location, country=country, published_at=None)
        db.session.add(page)
        db.session.commit()
    return True


def generator():
    try:
        response = requests.get("https://api.projectwhite.space/iapi/v1.0/contents?used=False", verify=False)
        data = response.json()
    except Exception as e:
        config.logging.warning("Generator request to API", e)
        return

    page_count = 0

    with app.app_context():
        count = PageCount.query.first()
        if count:
            page_count = count.page_count

    lengths_of_contents_region = {}
    layout_templates = os.listdir(conf_var.template_dir)
    items = data['items']

    for item in range(len(items)):
        lengths_of_contents_region[item] = len(items[item])

    index = 0
    number_of_country = list(range(0, len(lengths_of_contents_region)))
    page_count_indexer = [-1] * len(number_of_country)

    while len(number_of_country) != 1 and len(number_of_country) > 0:
        index1 = index
        first = number_of_country[index1]
        index2 = index + 1

        if index2 == len(number_of_country):
            index2 = 0
        second = number_of_country[index2]
        flag1 = True
        flag2 = True

        try:
            if lengths_of_contents_region[second] < min_page:
                flag2 = False
                number_of_country.remove(number_of_country[index2])
            if lengths_of_contents_region[first] < max_page:
                flag1 = False
                number_of_country.remove(number_of_country[index1])
        except Exception as e:
            config.logging.warning("Generator request to length condition", e)

        try:
            if flag1 and flag2:
                if lengths_of_contents_region[first] >= max_page and lengths_of_contents_region[second] >= min_page:
                    layout_batch = items[first][page_count_indexer[first]:page_count_indexer[first] - max_page:-1] + \
                                   items[
                                       second][
                                   page_count_indexer[
                                       second]:(
                                           page_count_indexer[
                                               second] - min_page):-1]

                    random.shuffle(layout_batch)

                    template_writer(file_name=layout_templates[page_count % max_page] + "_" + str(page_count) + ".html",
                                    template=f'{conf_var.template_dir}/{layout_templates[page_count % max_page]}',
                                    data=layout_batch)

                    fill_meta_generated_table(
                        page_name=layout_templates[page_count % max_page] + "_" + str(page_count) + ".html",
                        layout_name=layout_templates[page_count % max_page],
                        storage_location="gcp",
                        country=items[first][0]['country'] if items[first][0]['country'] else 'US')

                    page_count += 1
                    page_count_indexer[first] -= max_page
                    page_count_indexer[second] -= min_page
                    lengths_of_contents_region[first] -= max_page
                    lengths_of_contents_region[second] -= min_page
            if index == len(number_of_country) - 1:
                index = 0
            elif index >= len(number_of_country):
                index = 0
            else:
                index += 1
        except Exception as e:
            config.logging.warning("Generator", e)

    upload_from_directory(conf_var.local_html_page_directory,
                          conf_var.html_bucket_name,
                          conf_var.remote_html_page_directory)

    with app.app_context():
        counter = PageCount.query.first()
        if not counter:
            save_page_number = PageCount(id=uuid.uuid4(), page_count=page_count)
            db.session.add(save_page_number)
            db.session.commit()
        else:
            counter.page_count = page_count
            db.session.commit()

    try:
        for key, value in lengths_of_contents_region.items():
            if value != 0:
                for con in range(value):
                    with app.app_context():
                        content = Content.query.filter_by(id=uuid.UUID(items[key][con]['id'])).first()
                        content.used = False
                        db.session.commit()
    except Exception as e:
        config.logging.warning("Marking False remaining", e)
