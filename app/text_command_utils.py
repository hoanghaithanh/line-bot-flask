from models import Language, LineUser
import wikipedia

def handle_command(db, line_event, command, content):
    lang_keyword = ['language', 'lang', 'ngon ngu', 'ngôn ngữ', '言語']
    support_lang = [k.symbol for k in Language.query.all()]
    print(support_lang)
    sum_keyword = ['summary', 'define', '定義', 'định nghĩa', 'tra']

    command = command.lower().strip()
    content = content.lower().strip()

    if command in lang_keyword:
        if content in support_lang:
            lang_id = Language.query.filter(Language.symbol == content).first().id
            db.session.merge(LineUser(line_event.source.user_id, lang_id))
            db.session.commit()
            return 'Language changed to: ' + content

    if command in sum_keyword:
        return summary_keyword(line_event, content)

    return 'Wrong syntax, try "Summary: [keyword]"!'


def summary_keyword(line_event, keyword):
    lang = get_language(line_event)
    wikipedia.set_lang(lang)
    return wikipedia.summary(keyword, sentences=5)


def get_language(db, line_event):
    user = LineUser.query.filter(LineUser.line_id == line_event.source.user_id).first()
    if user:
        return Language.query.filter(Language.id == user.lang_id).first().symbol
    else:
        db.session.merge(LineUser(line_event.source.user_id, 1))
        db.session.commit()
        return Language.query.filter(Language.id == 1).first().symbol
