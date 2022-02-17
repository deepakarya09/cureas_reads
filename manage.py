import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app.main.models import user, user_credentials, user_session, source, contents, content_types, content_tags, tags, \
    page_counts, meta_static_pages, submissions, submitted_articles, config_variables, brands, widgets, branding_pages, brand_articles, template_creation, page_data, token, rolebranduser, membership, email_subscribers, pricing_model, ssl_cert_model, faq_model, page_seo, page_editors, page_component, template_css_styles, css_styles, story_app, story_data, story_editors, story_seo, story_template, brand_social_accounts, social_access, story_share, brand_log, social_stats, page_stats, story_stats

from app import blueprint
from app.main import create_app, db
from flask_cors import CORS
from pytz import utc
from app.main.services.analytics.analytics_content import kafka_consumer

from app.main.services.story.story_sharing_services import schedule_share
from app.main.services.ssl_cron_services import ssl_cron_job
from app.main.services.social_stats_services import call_scheduler_for_social_logs

app = create_app('dev')
CORS(app, resources={r"/": {"origins": "*"}})


app.register_blueprint(blueprint)
app.app_context().push()

schedule = BackgroundScheduler(timezone=utc, deamon=True)
schedule.add_job(ssl_cron_job, 'interval', minutes=10)

manager = Manager(app)
migrate = Migrate(app, db, compare_type=True)

manager.add_command('db', MigrateCommand)


def share():
    schedule_share(app)


def social_stat():
    call_scheduler_for_social_logs(app)


def consumer():
    kafka_consumer(app)


schedule.add_job(share, trigger="interval", minutes=3)
schedule.add_job(social_stat, trigger="interval", minutes=10)
schedule.add_job(consumer)
schedule.start()


@manager.command
def run():
    db.create_all()
    app.run(port=81)


if __name__ == '__main__':
    manager.run()
