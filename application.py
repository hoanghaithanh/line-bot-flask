from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy, event

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (ImageMessage, MessageEvent, TextMessage,
                            TextSendMessage, FollowEvent)
from app.text_command_utils import *
import sys
import os
import wikipedia
import logging

from logging.handlers import RotatingFileHandler
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger.setLevel(logging.DEBUG)
log_handler = RotatingFileHandler('linebot.log', maxBytes=1024, backupCount=5)
log_handler.setFormatter(formatter)


application = Flask(__name__)
application.config.from_object(os.environ['APP_SETTINGS'])
application.logger.addHandler(log_handler)
db = SQLAlchemy(application)
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

#Load model
from models import *


@event.listens_for(ImageCommand.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    db.session.add(ImageCommand(command='detect text'))
    db.session.add(ImageCommand(command='translate text'))
    db.session.add(ImageCommand(command='describe objects'))
    db.session.commit()


@application.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(line_event):
    error_mess = 'Wrong syntax, try "Summary: [keyword]"!'
    if line_event.message.text:
        message = line_event.message.text
        try:
            application.logger.info(message)
            command, content = message.split(':')
            message = handle_command(db, line_event, command, content)
            line_bot_api.reply_message(
                line_event.reply_token,
                TextSendMessage(text=message))
        except Exception as e:
            application.logger.error(e)
            application.logger.info(sys.exc_info())
            line_bot_api.reply_message(
                line_event.reply_token,
                TextSendMessage(text=error_mess))


@application.route("/hello", methods=['GET'])
def hello():
    return ' '.join(k.symbol for k in Language.query.all())


@application.route("/log", methods=['GET'])
def log():
    f = open('linebot.log')
    log_text = f.readline()
    f.close()
    return log_text


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(line_event):
    pass


def reply_message(line_event, messages):
    line_bot_api.reply_message(
        line_event.reply_token,
        messages=messages,
    )


if __name__ == "__main__":
    wikipedia.set_rate_limiting(True)
    db.create_all()
    application.run()
