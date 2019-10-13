from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (ImageMessage, MessageEvent, TextMessage,
                            TextSendMessage, FollowEvent)

import sys
import os
import wikipedia
import logging

from logging.handlers import RotatingFileHandler
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger.setLevel(logging.DEBUG)

log_handler = RotatingFileHandler('/home/ubuntu/logs/application.log', maxBytes=1024, backupCount=5)
log_handler.setFormatter(formatter)


application = Flask(__name__)
application.config.from_object(os.environ['APP_SETTINGS'])
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SQLALCHEMY_ECHO'] = True
application.logger.addHandler(log_handler)
db = SQLAlchemy(application)
#Load model
from models import *
db.create_all()
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])


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
def handle_message(event):
    error_mess = 'Wrong syntax, try "Summary: [keyword]"!'
    if event.message.text:
        message = event.message.text
        try:
            application.logger.info(message)
            command, content = message.split(':')
            message = handle_command(event, command, content)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=message))
        except Exception as e:
            application.logger.error(e)
            application.logger.info(sys.exc_info())
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_mess))


def handle_command(event, command, content):
    lang_keyword = ['language', 'lang', 'ngon ngu', 'ngôn ngữ', '言語']
    support_lang = [k.symbol for k in Language.query.all()]
    print(support_lang)
    sum_keyword = ['summary', 'define', '定義', 'định nghĩa', 'tra']

    command = command.lower().strip()
    content = content.lower().strip()

    if command in lang_keyword:
        if content in support_lang:
            lang_id = Language.query.filter(Language.symbol == content).first().id
            db.session.merge(LineUser(event.source.user_id, lang_id))
            db.session.commit()
            return 'Language changed to: ' + content

    if command in sum_keyword:
        return summary_keyword(event, content)

    return 'Wrong syntax, try "Summary: [keyword]"!'


def reply_message(event, messages):
    line_bot_api.reply_message(
        event.reply_token,
        messages=messages,
    )


def summary_keyword(event, keyword):
    lang = get_language(event)
    wikipedia.set_lang(lang)
    return wikipedia.summary(keyword, sentences=5)


def get_language(event):
    user = LineUser.query.filter(LineUser.line_id == event.source.user_id).first()
    if user:
        return Language.query.filter(Language.id == user.lang_id).first().symbol
    else:
        db.session.merge(LineUser(event.source.user_id, 1))
        db.session.commit()
        return Language.query.filter(Language.id == 1).first().symbol


@application.route("/hello", methods=['GET'])
def hello():
    return ' '.join(k.symbol for k in Language.query.all())


@application.route("/log", methods=['GET'])
def log():
    f = open('linebot.log')
    log_text = f.readline()
    f.close()
    return log_text


if __name__ == "__main__":
    wikipedia.set_rate_limiting(True)
    application.run()
