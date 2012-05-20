import logging
from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'popcorn_gallery.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

DEBUG = TEMPLATE_DEBUG = False

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = True

# Playdoh ships with sha512 password hashing by default. Bcrypt+HMAC is safer,
# so it is recommended. Please read <https://github.com/fwenzel/django-sha2#readme>,
# then switch this to bcrypt and pick a secret HMAC key for your application.
PWD_ALGORITHM = 'bcrypt'
HMAC_KEYS = { # for bcrypt only
    '2011-01-01': 'cheesecake',
}

# we need to test the mail that is sent.
EXCLUDED_APPS = ('django_mailer',)
INSTALLED_APPS = filter(lambda a: a not in EXCLUDED_APPS, INSTALLED_APPS)

NOSE_ARGS = [
    '-s',
    '--failed',
    '--stop',
    '--nocapture',
    '--failure-detail',
    '--with-progressive',
    '--logging-filter=-south',
    ]

# NOSE_PLUGINS = []

# Used for the assertion with browserid
SITE_URL = 'http://localhost:8000'

# Only internal IPs can access the API
INTERNAL_IPS =(
    '127.0.0.1',
    )

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INVALID_USERNAMES = (
    'admin',
    )

debug = dict(level=logging.DEBUG)
error = dict(level=logging.ERROR)

LOGGING = {
    'loggers': {
        'south': error,
    },
}

