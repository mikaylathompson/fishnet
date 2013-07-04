from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), index = True, unique = True)
	email = db.Column(db.String(120), index = True, unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	links = db.relationship('Link', backref = 'author', lazy = 'dynamic')
	about_me = db.Column(db.String(500))
	last_seen = db.Column(db.DateTime)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def __repr__(self):
		return '<USER %r>' % (self.name)

	@staticmethod
	def make_unique_name(name):
		if User.query.filter_by(name = name).first() == None:
			return name
		version = 2
		while True:
			new_name = name + str(version)
			if User.query.filter_by(name = new_name).first() == None:
				break
			version += 1
		return new_name

class Link(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(64))
	url = db.Column(db.String(150))
	annotation = db.Column(db.String(500))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.title)

