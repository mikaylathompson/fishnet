import os
CSRF_ENABLED = True
SECRET_KEY = "something-super-duper-secret"

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

OPENID_PROVIDERS = [
	{ 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
	{ 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
	{ 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
