# coding: utf-8

from app.extentions import db
from application import application

if __name__ == '__main__':
	db.init_app(application)
	db.create_all()
	application.run()
