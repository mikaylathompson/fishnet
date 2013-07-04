from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, NewLinkForm, EditLinkForm, NewFolder
from models import User, ROLE_USER, ROLE_ADMIN, Link, Folder
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = g.user
	#make sure every link is in a folder.
	for link in user.links:
		if link.folder_id is None:
			link.folder_id = 1
			db.session.add(link)
	db.session.commit()
	folders = Folder.query.filter_by(user_id = g.user.id).all()
	sortedLinks = {}
	for f in folders:
		sortedLinks[f] = f.links
	links = Link.query.filter_by(user_id = g.user.id).order_by(Link.timestamp)	
	return render_template("index.html",
		user = user,
		sortedLinks = sortedLinks)

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index', user = g.user))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for = ['email']) # ['name', 'email'])
	return render_template('login.html',
		form = form,
		providers = app.config['OPENID_PROVIDERS'])

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
	folders = Folder.query.filter_by(user_id = user.id).all()
	sortedLinks = {}
	for f in folders:
		sortedLinks[f] = f.links
	links = Link.query.filter_by(user_id = user.id).order_by(Link.timestamp)	
	folders = Folder.query.filter_by(user_id = user.id).all()
	return render_template('user.html', 
		user = user, 
		sortedLinks = sortedLinks)

@app.route('/user/<name>/folder/<label>')
def folder(name, label):
	user = User.query.filter_by(name = name).first()
	if user == None:
		flash('User' + name + ' not found.')
		return redirect(url_for('index'))
	folder = Folder.query.filter_by(label = label, user_id=user.id).first()
	if folder == None:
		flash(name + ' doesn\'t have a folder of that name.')
		return redirect(url_for('user', name=name))
	return render_template('folder.html', 
		user = user, 
		folder = folder)


@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.name)
	if form.validate_on_submit():
		g.user.name = form.name.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('user', name = g.user.name))
	else:
		form.name.data = g.user.name
		form.about_me.data = g.user.about_me
	return render_template('edit.html', user = g.user, form = form)

@app.route('/link/<id>', methods = ['GET', 'POST'])
@login_required
def editlink(id):
	link = Link.query.get(id)
	if link == None:
		flash('That link doesn\'t exist.')
		return redirect(url_for('index', user = g.user))
	if link.user_id == g.user.id:
		form = EditLinkForm()
		if form.validate_on_submit():
			if form.url.data != link.url and form.url.data != None:
				url_raw = form.url.data
				if url_raw[0:7] == 'http://' or url_raw[0:8] == 'https://':
					url_clean = url_raw
				else:
					url_clean = 'http://' + url_raw
				link.folder = form.url_clean
			link.title = form.title.data
			link.annotation = form.annotation.data
			print "CAN ANYONE HEAR ME?!?"
			print form.folder.data
			if form.folder.data != None:
				link.folder = int(form.folder.data)
			db.session.add(link)
			db.session.commit()
			flash('Your changes have been saved.')
			return redirect(url_for('user', name = g.user.name))
		else:
			form.title.data = link.title
			form.url.data = link.url
			form.annotation.data = link.annotation
			# form.folder.data = link.folder
	return render_template('link.html', link = link, user = g.user, form = form)

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
			if form.folder.data == None:
				folder = 1
			else:
				folder = int(form.folder.data)
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
		flash('Mysterious error. The form didn\'t validate.  Make sure you have both a title and URL.')
	return render_template('newlink.html', user = g.user, form = form)

@app.route('/newfolder', methods = ['GET', 'POST'])
@login_required
def newfolder():
	form = NewFolder()
	if form.label.data:
		if form.validate_on_submit():
			folder = Folder(label = form.label.data, user_id = g.user.id)
			db.session.add(folder)
			db.session.commit()
			flash('Folder added.')
			return redirect(url_for('index'))
		flash('The form wasn\'t created.  Try again.')
	return render_template('newfolder.html', user = g.user, form = form)


@app.route('/delete/<id>')
@login_required
def delete(id):
	link = Link.query.get(id)
	if link.user_id == g.user.id:
		#User has authority to delete link
		db.session.delete(link)
		db.session.commit()
		flash('The link has been deleted.')
	else:
		#User doesn't have authority to delete
		flash('You can\'t delete a post that\'s not yours.')
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
		default_folder = Folder(label='default', user_id=user.id)
		db.session.add(user)
		db.session.add(default_folder)
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

