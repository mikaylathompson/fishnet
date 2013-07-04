from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

#One user to many folders
#One folder to many links

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), index = True, unique = True)
	email = db.Column(db.String(120), index = True, unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	folders = db.relationship('Folder', backref = 'owner', lazy = 'dynamic')
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
			newName = name + str(version)
			if User.query.filter_by(name = newName).first() == None:
				break
			version += 1
		return newName

class Folder(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	label = db.Column(db.String(64))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	links = db.relationship('Link', backref='folder', lazy = 'dynamic')
	
class Link(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(64))
	url = db.Column(db.String(150))
	annotation = db.Column(db.String(500))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))

	def __repr__(self):
		return '<Post %r>' % (self.title)



