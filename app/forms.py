from flask.ext.wtf import Form, TextAreaField, TextField, BooleanField
from flask.ext.wtf import Required, Length
from app.models import User, Link

class LoginForm(Form):
	openid = TextField('openid', validators = [Required()])
	remember_me = BooleanField('remember_me', default = False)

class EditForm(Form):
	name = TextField('name', validators = [Required()])
	about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 499)])
	
	def __init__(self, oldName, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.oldName = oldName
	
	def validate(self):
		if not Form.validate(self):
			return False
		if self.name.data == self.oldName:
			return True
		user = User.query.filter_by(name = self.name.data).first()
		if user != None:
			self.name.errors.append('This name is already in use.  Choose another.')
			return False
		return True

class NewLinkForm(Form):
	title = TextField('title', validators = [Required()])
	url = TextField('url', validators = [Required()])
	annotation = TextAreaField('annotation', validators = [Length(min = 0, max = 499)])
	
	def validate(self):
#		if not Form.validate(self):
#			return False
		return True
 

