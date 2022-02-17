
import requests
import logging
import os
url = 'https://api.projectwhite.space/'

if not os.path.exists("log/"):
    os.makedirs("log")


scron_logger = logging.getLogger(__name__)
scron_logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(message)s')

file_handler = logging.FileHandler('log/scron_job.log')
file_handler.setFormatter(formatter)

scron_logger.addHandler(file_handler)

try:
    req = requests.get(f'{url}/api/v1.0/ssl/cronjob')
    scron_logger.critical(f" {req.text} -- cron log")
    print(req.text)
except Exception as e:
    scron_logger.exception(f" {req.text} -- cron log")
    
