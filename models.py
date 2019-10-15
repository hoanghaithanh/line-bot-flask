from app.extentions import db


class LineUser(db.Model):
	__table_args__ = {"schema": "line"}
	__tablename__ = 'line_user'

	line_id = db.Column(db.String(), primary_key=True)
	lang_id = db.Column(db.Integer, db.ForeignKey('line.language.id'), default=1)
	image_command_id = db.Column(db.Integer, db.ForeignKey('line.image_command.id'), default=1)

	def __init__(self, line_id, lang_id):
		self.line_id = line_id
		self.lang_id = lang_id

	def __repr__(self):
		return '<line_id {}: lang_id {}>'.format(self.line_id, self.lang_id)


class Language(db.Model):
	__table_args__ = {"schema": "line"}
	__tablename__ = 'language'

	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String())

	def __init__(self, lang_id, symbol):
		self.id = lang_id
		self.symbol = symbol

	def __repr__(self):
		return '<line_id {}: lang_id {}>'.format(self.id, self.symbol)


class ImageCommand(db.Model):
	__table_args__ = {"schema": "line"}
	__tablename__ = 'image_command'

	id = db.Column(db.Integer, db.Sequence('image_command'), primary_key=True)
	command = db.Column(db.String(), unique=True, nullable=False)