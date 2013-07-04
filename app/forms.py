from flask.ext.wtf import Form, TextAreaField, TextField, BooleanField
from flask.ext.wtf import Required, Length

class LoginForm(Form):
	openid = TextField('openid', validators = [Required()])
	remember_me = BooleanField('remember_me', default = False)

class EditForm(Form):
	name = TextField('name', validators = [Required()])
	about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])

