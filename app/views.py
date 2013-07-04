from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, NewLinkForm
from models import User, ROLE_USER, ROLE_ADMIN, Link
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = g.user
	links = Link.query.filter_by(user_id = g.user.id).order_by(Link.timestamp)	
	return render_template("index.html",
		title = 'Home',
		user = user,
		links = links)

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
@login_required
def user(name):
	user = User.query.filter_by(name = name).first()
	if user == None:
		flash('User' + name + ' not found.')
		return redirect(url_for('index'))
	links = Link.query.filter_by(user_id = user.id).order_by(Link.timestamp)	
	return render_template('user.html', user = user, links = links)

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

@app.route('/newlink', methods = ['GET', 'POST'])
@login_required
def newlink():
	form = NewLinkForm()
	if form.url.data:
		if form.validate():
			url_raw = form.url.data
			if url_raw[0:7] == 'http://':
				url_clean = url_raw
			else:
				url_clean = 'http://' + url_raw
			title = form.title.data
			annotation = form.annotation.data
			timestamp = datetime.utcnow()
			user_id = g.user.id
			link = Link(title = title, url = url_clean, annotation = annotation, timestamp = timestamp, user_id = user_id)
			db.session.add(link)
			db.session.commit()
			flash('Link added.')
			return redirect(url_for('index'))
		flash('Mysterious error. The form didn\'t validate.')
	return render_template('newlink.html', user = g.user, form = form)

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

