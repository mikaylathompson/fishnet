from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, NewLinkForm, NewFolder, RegisterForm, EditLinkForm, ChangePassForm
from models import User, Link, Folder, ROLE_USER, ROLE_ADMIN
from datetime import datetime
import hashlib

@app.route('/')
@app.route('/index')
def index():
	try:
		name = g.user.name
		user = g.user
		#make sure every link is in a folder.
		for link in user.links:
			if link.folder_id is None:
				link.folder_id = 1
				db.session.add(link)
		db.session.commit()
		folders = Folder.query.filter_by(user_id = g.user.id).order_by(Folder.id).all()
		sortedLinks = {}
		for f in folders:
			#make sure every folder has a visibility set.
			if f.visibility == None:
				f.visibility = 2
				db.session.add(f)
				db.session.commit()
			sortedLinks[f] = f.links
		links = Link.query.filter_by(user_id = g.user.id).order_by(Link.timestamp)	
		return render_template("index.html",
			user = user,
			sortedLinks = sortedLinks)
	except AttributeError:
		return render_template('welcome.html')
		

@app.route('/admin')
@login_required
def admin():
	u = g.user
	if u.email == 'mikayla.thompson@yale.edu' or u.email == 'mt1993@gmail.com':
		users = []
		for user in User.query.all():
			users.append(user)
		#make sure every link is in a folder.
		all_links = Link.query.all()
		for link in all_links:
			if link.folder_id is None:
				link.folder_id = User.query.get(link.user_id).folders.all()[0].id
				db.session.add(link)
				db.session.commit()
		#make sure every folder has a visibility set.
		all_folders = Folder.query.all()
		for f in all_folders:	
			if f.visibility == None:
				f.visibility = 2
				db.session.add(f)
				db.session.commit()
		return render_template('admin.html',
			user = u,
			users = users)
	else:
		flash('You\'re not authorized to view that page.  If you believe that\'s in error, '
			'you should have the authority to go in and edit the code yourself.')
		return redirect(url_for('index'))



@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index', user = g.user))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user == None:
			flash('Email isn\'t found.  Register instead?')
			return redirect(url_for('register'))
		else:
			passhash = hashlib.sha224(form.pswd.data + user.email).hexdigest()
			if passhash == user.passhash:
				login_user(user)
				flash("Logged in successfully.")
	        	return redirect(request.args.get("next") or url_for("index"))
	        if form.email.data != None:
		        flash('Incorrect email or password.')
	return render_template('login.html', form = form)


@app.route('/register', methods = ['GET', 'POST'])
def register():
	if g.user is not None and g.user.is_authenticated():
		flash('You\'re already logged in.')
		return redirect(url_for('index'))
	form = RegisterForm()
	if form.validate_on_submit():
		if User.query.filter_by(email = form.email.data).first() != None:
			flash('This email is already registered.  Login instead.')
			return(redirect(url_for('login')))
		if User.query.filter_by(name = form.name.data).first() != None:
			flash('That name is taken.  Try another.')
			return render_template('register.html', form = form)
		email = form.email.data
		name = form.name.data
		passhash = hashlib.sha224(form.pswd.data + form.email.data).hexdigest()
		user = User(email = email, name = name, passhash = passhash, role = ROLE_USER)
		db.session.add(user)
		db.session.commit()
		default = Folder(label = 'Default', user_id = user.id)
		db.session.add(default)
		db.session.commit()
		conns = Folder(label = 'Connections', user_id = user.id)
		db.session.add(conns)
		db.session.commit()
		login_user(user)
		flash("You've successfully registered.")
		return redirect(url_for('index'))
	return render_template('register.html', form = form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/user/<name>')
def user(name):
	user = User.query.filter_by(name = name).first()
	if user == None:
		flash('User' + name + ' not found.')
		return redirect(url_for('index'))
	if user == g.user:
		folders = Folder.query.filter_by(user_id = user.id).all()
	else:
		folders = Folder.query.filter_by(user_id = user.id, visibility = 2).all()
	sortedLinks = {}
	for f in folders:
		sortedLinks[f] = f.links
	links = Link.query.filter_by(user_id = user.id).order_by(Link.timestamp)	
	folders = Folder.query.filter_by(user_id = user.id).all()
	return render_template('user.html', 
		user = user, 
		viewer = g.user,
		sortedLinks = sortedLinks)

@app.route('/user/<name>/folder/<label>')
def folder(name, label):
	user = User.query.filter_by(name = name).first()
	if user == None:
		flash('User ' + name + ' not found.')
		return redirect(url_for('index'))
	folder = Folder.query.filter_by(label = label, user_id=user.id).first()
	if folder == None:
		flash(name + ' doesn\'t have a folder of that name.')
		return redirect(url_for('user', name=name))
	permission = False
	if folder.visibility != 0:
		permission = True
	elif user == g.user:
		permission = True
	if permission:
		return render_template('folder.html', 
			user = user, 
			folder = folder)
	else:
		flash(name + ' doesn\'t have a folder of that name, or you don\'t have permission to view it.')
		return redirect(url_for('user', name = user.name))
	

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.name)
	if form.validate_on_submit():
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('user', name = g.user.name))
	else:
		form.name.data = g.user.name
		form.about_me.data = g.user.about_me
	return render_template('edit.html', user = g.user, form = form)

@app.route('/changepass', methods = ['GET', 'POST'])
@login_required
def changepass():
	form = ChangePassForm()
	user = g.user
	if form.validate_on_submit():
		oldhash = hashlib.sha224(form.oldPass.data + user.email).hexdigest()
		if oldhash == user.passhash:
			newhash = hashlib.sha224(form.newPass.data + user.email).hexdigest()
			user.passhash = newhash
			db.session.add(user)
			db.session.commit()
			flash('Your changes have been saved.')
			return redirect(url_for('user', name = g.user.name))
		else:
			flash('Current password was incorrect.')
			return redirect(url_for('changepass'))
	else:
		return render_template('changepass.html', user = g.user, form = form)

@app.route('/newlink', methods = ['GET', 'POST'])
@login_required
def newlink():
	form = NewLinkForm()
	form.folder.choices = [(f.id, f.label) for f in g.user.folders.all()]
	if form.url.data:
		if form.validate_on_submit():
			url_raw = form.url.data
			if url_raw[0:7] == 'http://' or url_raw[0:8] == 'https://':
				url_clean = url_raw
			else:
				url_clean = 'http://' + url_raw
			title = form.title.data
			annotation = form.annotation.data
			try:
				folder = int(form.folder.data)
			except ValueError:
				folder = g.user.folders.all()[0].id
			timestamp = datetime.utcnow()
			user_id = g.user.id
			link = Link(title = title,
				url = url_clean,
				annotation = annotation, 
				timestamp = timestamp,
				folder_id = folder, 
				user_id = user_id)
			db.session.add(link)
			db.session.commit()
			flash('Link added.')
			return redirect(url_for('index'))
		flash('The form didn\'t validate.  Make sure you have both a title and URL.')
	return render_template('newlink.html', user = g.user, form = form)

@app.route('/editlink/<id>', methods = ['GET', 'POST'])
@login_required
def editlink(id):
	try:
		link = Link.query.get(id)
		if link.user_id != g.user.id:
			flash('You don\'t have permission to edit that link.')
			return redirect(url_for('index'))
		form = EditLinkForm()
		form.folder.choices = [(f.id, f.label) for f in g.user.folders.all()]
		if form.validate_on_submit() and form.annotation.data != None:
			link.annotation = form.annotation.data
			try:
				link.folder_id = int(form.folder.data)
			except ValueError:
				pass
			db.session.add(link)
			db.session.commit()
			flash('Your changes have been saved.')
			return redirect(url_for('index'))
		form.annotation.data = link.annotation
		return render_template('editlink.html', user = g.user, form = form, link = link)
	except AttributeError:
		flash('Link does not exist.')
		return redirect(url_for('index'))


@app.route('/newfolder', methods = ['GET', 'POST'])
@login_required
def newfolder():
	form = NewFolder()
	if form.label.data:
		if form.validate_on_submit():
			try:
				vis = int(form.visibility.data)
			except ValueError:
				vis = 2
			folder = Folder(label = form.label.data, visibility = vis, user_id = g.user.id)
			db.session.add(folder)
			db.session.commit()
			flash('Folder added.')
			return redirect(url_for('index'))
		flash('The form wasn\'t created.  Try again.')
	return render_template('newfolder.html', user = g.user, form = form)

@app.route('/vis/<folderid>/<vis_set>')
@login_required
def vis_to(folderid, vis_set):
	folder = Folder.query.get(folderid)
	if folder == None:
		flash('That folder does not exist.')
		return redirect(url_for('index'))
	owner = User.query.get(folder.user_id)
	if g.user != owner:
		flash('You don\'t have permission to change this folder.')
		return redirect(url_for('index'))
	folder.visibility = int(vis_set)
	db.session.add(folder)
	db.session.commit()
	flash('Visibility adjusted.')
	return redirect(url_for('folder', name = owner.name, label = folder.label))

@app.route('/connect/<userid>')
@login_required
def connect(userid):
	u = User.query.get(userid)
	#Make a connections folder if they don't have one:
	if len(g.user.folders.all()) < 2:
		conns = Folder(label = 'Connections', user_id = g.user.id)
		db.session.add(conns)
		db.session.commit()
	title = str(u.name) + '\'s fishnet'
	url = url_for('user', name = u.name)
	annotation = str(u.name) + '\'s fishnet'
	timestamp = datetime.utcnow()
	folder = Folder.query.get(g.user.folders.order_by(Folder.id).all()[1].id)
	link = Link(title = title,
				url = url,
				annotation = annotation, 
				timestamp = timestamp,
				folder_id = folder.id, 
				user_id = g.user.id)
	db.session.add(link)
	db.session.commit()
	return redirect(url_for('folder',
		name = g.user.name,
		label = folder.label))


@app.route('/deletelink/<id>')
@login_required
def deletelink(id):
	link = Link.query.get(id)
	if link == None:
		flash('That link doesn\'t exist.')
	else:
		if link.user_id == g.user.id:
			#User has authority to delete link
			db.session.delete(link)
			db.session.commit()
			flash('The link has been deleted.')
		else:
			#User doesn't have authority to delete
			flash('You can\'t delete a link that\'s not yours.')
	return redirect(url_for('index'))

#end of app.route

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()

@app.errorhandler(404)
def internal_error(error):
	return render_template('404.html', user = g.user), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('500.html', user = g.user), 500
#end of app.

@oid.after_login
def after_login(resp):
	if resp.email is None or resp.email == "":
		flash('Invalid login.  Please try again.')
		return redirect(url_for('login'))
	user = User.query.filter_by(email = resp.email).first()
	if user is None:
		name = resp.name
		if name is None or name == "":
			name = resp.email.split('@')[0]
		name = User.make_unique_name(name)
		user = User(name = name, email = resp.email, role = ROLE_USER)
		db.session.add(user)
		db.session.commit()
	remember_me = False
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))
#end of oid.

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))
#end of lm.

