from __future__ import unicode_literals

import os

USER_CONNECTION_MODEL_MIXIN = 'test_models.AbstractUserConnectionMixin'
USER_CONNECTION_MANAGER = 'test_models.managers.UserConnectionManager'

# Do not run in DEBUG in production!!!
DEBUG = False

ALLOWED_HOSTS = ['*']
LANGUAGE_CODE = 'en-us'
SECRET_KEY = '12345abcd'
SITE_ID = 1
TIME_ZONE = 'UTC'
USE_I18N = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_testing',
    'django_core',
    'test_models',
    'user_connections',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

here = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': here('test_db.db')
    }
}
