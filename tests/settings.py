# -*- coding: utf-8 -*-
import os

USER_CONNECTION_MODEL_MIXIN = 'tests.test_models.AbstractUserConnectionMixin'
USER_CONNECTION_MANAGER = 'tests.test_models.managers.UserConnectionManager'

# Do not run in DEBUG in production!!!
DEBUG = False

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_user_connections',
    'django_testing',
    'django_core',
    'django_nose',
    'test_models',
)

SECRET_KEY = '12345abcd'
ALLOWED_HOSTS = ['*']

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

here = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': here('test_db.db')
    }
}
