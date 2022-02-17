from flask_restplus import Api
from flask import Blueprint

from app.main.controllers.source_controller import api as user_ns
from app.main.controllers.user_controller import api as source_ns
from app.main.controllers.tags_controller import api as tag_ns
from app.main.controllers.sapi_content_controller import api as con_ns
from app.main.controllers.api_content_controller import api as con_api
from app.main.controllers.scrape_controller import api as scrap_ns
from app.main.controllers.generator_controller import api as gen_api
from app.main.controllers.iapi_system_controllers import api as config_api
from app.main.controllers.layout_controller import api as layout_api
from app.main.controllers.brand_controller import api as brand_api
from app.main.controllers.widget_controller import api as widget_api
from app.main.controllers.aapi_crowd_sourcing_controller import api as submission_api
from app.main.controllers.api_crowd_source_controller import api as crowd_api
from app.main.controllers.parser_controller import api as parser_api
from app.main.controllers.template_controller import api as template_api
from app.main.controllers.brandpage_controller import api as brand_page_api
from app.main.controllers.brand_articles_controller import api as brand_articles_api
from app.main.controllers.api_multiuser import api as multiuser_api
from app.main.controllers.referral_controller import api as referral_api
from app.main.controllers.user_role_brand import api as role_api
from app.main.controllers.api_email_subscribers import api as subscriber_api
from app.main.controllers.image_controller import api as image_api
from app.main.controllers.ssl_generator_controller import api as ssl_ns
from app.main.controllers.ssl_cron_job_controller import api as ssl_cron_ns
from app.main.controllers.api_page_component import api as page_component_ns
from app.main.controllers.api_css_style_controller import api as css_style_api
from app.main.controllers.api_template_css_style_controller import api as template_css_style_api
from app.main.controllers.api_brand_page_seo_controller import api as brand_page_seo
from app.main.controllers.api_story_controller import api as brand_story_api
from app.main.controllers.api_story_templates import api as story_template_api
from app.main.controllers.api_brand_social_account_controller import api as social_account_api
from app.main.controllers.api_story_sharing import api as story_sharing_api
from app.main.controllers.api_brand_log import api as brand_log_api
from app.main.controllers.api_analytics_social import api as social_analytics_api
from app.main.controllers.api_analytics_content import api as content_analytics_api

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='CuriousReads',
          version='1.0',
          description=''
          )

api.add_namespace(user_ns, path='/')
api.add_namespace(source_ns, path='/')
api.add_namespace(tag_ns, path='/')
api.add_namespace(con_ns, path="/")
api.add_namespace(con_api, path='/')
api.add_namespace(scrap_ns, path='/')
api.add_namespace(gen_api, path='/')
api.add_namespace(config_api, path='/')
api.add_namespace(layout_api, path='/')
api.add_namespace(crowd_api, path='/')
api.add_namespace(submission_api, path='/')
api.add_namespace(widget_api, path="/")
api.add_namespace(brand_api, path="/")
api.add_namespace(parser_api, path="/")
api.add_namespace(template_api, path="/")
api.add_namespace(brand_page_api, path="/")
api.add_namespace(brand_articles_api, path='/')
api.add_namespace(multiuser_api, path='/')
api.add_namespace(referral_api, path='/')
api.add_namespace(role_api, path='/')
api.add_namespace(subscriber_api, path='/')
api.add_namespace(image_api, path='/')
api.add_namespace(ssl_ns, path='/')
api.add_namespace(ssl_cron_ns, path='/')
api.add_namespace(page_component_ns, path='/')
api.add_namespace(css_style_api, path='/')
api.add_namespace(template_css_style_api, path='/')
api.add_namespace(brand_page_seo, path='/')
api.add_namespace(brand_story_api, path='/')
api.add_namespace(story_template_api, path='/')
api.add_namespace(social_account_api, path='/')
api.add_namespace(story_sharing_api, path='/')
api.add_namespace(brand_log_api, path='/')
api.add_namespace(social_analytics_api, path='/')
api.add_namespace(content_analytics_api, path='/')
