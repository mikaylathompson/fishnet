from flask.ext.wtf import Form, TextAreaField, TextField, BooleanField, SelectField, PasswordField, RadioField
from flask.ext.wtf import Required, Length, ValidationError, URL, InputRequired
from app.models import User, Link, Folder

class LoginForm(Form):
	# openid = TextField('openid', validators = [Required()])
	remember_me = BooleanField('remember_me', default = False)
	email = TextField('email', validators = [Required()])
	pswd = PasswordField('pswd', validators = [Length(min = 5, max=25)])

class RegisterForm(Form):
	email = TextField('email', validators = [Required()])
	name = TextField('name', validators = [Required()])
	pswd = PasswordField('pswd', validators = [Length(min = 5, max=25)])
 

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

class ChangePassForm(Form):
	oldPass = PasswordField('old', validators = [Required()])
	newPass = PasswordField('new', validators = [Length(min = 5, max=25)])

class NewLinkForm(Form):
	title = TextField('title', validators = [InputRequired(message='Enter a title.'), ])
	url = TextField('url', validators = [InputRequired(message='Enter a URL.'), URL(require_tld=False, message="Not a valid URL.")])
	annotation = TextAreaField('annotation', validators = [Length(min = 0, max = 499)])
	folder = SelectField('folder', validators = [InputRequired(message='Choose a folder.')]) 

	def validate_on_submit(self):
		if self.title.errors:
			print 'Error in title.'
			return False
		if self.url.errors:
			print 'Error in url.'
			return False
		if self.annotation.errors:
			print 'Error in annotation.'
			return False
		if self.folder.errors:
			print 'Error in folder.'
			return False
		return True

class EditLinkForm(Form):
	annotation = TextAreaField('annotation', validators = [Length(min = 0, max = 499)])
	folder = SelectField('folder', validators = [InputRequired(message='Choose a folder.')]) 

	def validate_on_submit(self):
		if self.annotation.errors:
			print 'Error in annotation.'
			return False
		if self.folder.errors:
			print 'Error in folder.'
			return False
		return True


class NewFolder(Form):
	label = TextField('label', validators = [Required()])
	visibility = RadioField('visibility', choices=[('0', 'Private'), ('1', 'With Link'), ('2', 'Public')], default=2)



