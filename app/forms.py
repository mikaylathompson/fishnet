from flask.ext.wtf import Form, TextField, BooleanField, TextAreaField
from flask.ext.wtf import Required, Length
from app.models import User

class LoginForm(Form):
	openid = TextField('openid', validators = [Required()])
	remember_me = BooleanField('remember_me', default = False)

class EditForm(Form):
	name = TextField('name', validators = [Required()])
	about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 500)])

	def __init__(self, original_name, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.original_name = original_name

	def validate(self):
		if not Form.validate(self)
			return False
		if self.name.data == self.original_name:
			return True
		user = User.query.filter_by(name = self.name.data).first()
		if user != None:
			self.name.errors.append('This name is already in use.  Please choose another.')
			return False
		return True

