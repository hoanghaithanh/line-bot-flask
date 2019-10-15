# coding: utf-8

from application import application
from app.extentions import db

db.init_app(application)
db.create_all()
application.run()
