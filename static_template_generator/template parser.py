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

template_env = Environment(cache_size=1000)


def template_writer():
    template = template_env.from_string("<html>{{ image }}</html>")
    gen = template.render({"image": "hello"})
    print(gen)


template_writer()
