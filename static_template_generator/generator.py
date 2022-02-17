import os
import sys
import schedule
import time
import conf_var

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + os.sep + '..')

from generator_service.generator_service import generator

try:
    if not os.path.exists(conf_var.local_html_page_directory):
        os.makedirs(conf_var.local_html_page_directory)
except:
    pass

schedule.every(conf_var.generator_time_span).seconds.do(generator)
while True:
    schedule.run_pending()
    time.sleep(1)
