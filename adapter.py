# coding: utf-8
import sys
import logging
from logging.handlers import RotatingFileHandler

sys.path.insert(0, '/var/www/line-bot-flask')
from application import application

if __name__ == '__main__':
	application.run()