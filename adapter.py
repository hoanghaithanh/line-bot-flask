# coding: utf-8
import sys
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger.setLevel(logging.DEBUG)

log_handler = RotatingFileHandler('/home/ubuntu/logs/linebot.log', maxBytes=1024, backupCount=5)
log_handler.setFormatter(formatter)
sys.path.insert(0, '/var/www/line-bot-flask')

try:
	from application import application
except Exception as e:
	logger.exception(e)
	logger.info(sys.version)