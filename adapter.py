# coding: utf-8

from application import application
from app.extentions import db

if __name__ == '__main__':
	db.init_app(application)
	db.create_all()
	application.run()
