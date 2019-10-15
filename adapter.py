# coding: utf-8

from app.extentions import db
from application import application

if __name__ == '__main__':
	db.init_app(application)
	#Tell sqlalchemy which app is the current app
	with application.app_context():
		db.create_all()
	application.run()
