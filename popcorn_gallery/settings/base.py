# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'example_css': (
            'css/examples/main.css',
        ),
        'example_mobile_css': (
            'css/examples/mobile.css',
        ),
    },
    'js': {
        'example_js': (
            'js/examples/libs/jquery-1.4.4.min.js',
            'js/examples/libs/jquery.cookie.js',
            'js/examples/init.js',
            ),
    }
}

# Defines the views served for root URLs.
ROOT_URLCONF = 'popcorn_gallery.urls'

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.messages',
    'django_browserid',
    'django_extensions',
    'south',
    'taggit',
    'django_mailer',
    'voting',
    'haystack',
    # Application base, containing global templates.
    'popcorn_gallery.base',
    'popcorn_gallery.popcorn',
    'popcorn_gallery.users',
    'popcorn_gallery.notifications',
    'popcorn_gallery.activity',
    'popcorn_gallery.reports',
    'popcorn_gallery.search',
    'popcorn_gallery.attachments',
]


# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'registration',
]

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['lhtml'] = [
#    ('**/templates/**.lhtml',
#        'tower.management.commands.extract.extract_tower_template'),
# ]

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['javascript'] = [
#    # Make sure that this won't pull in strings from external libraries you
#    # may use.
#    ('media/js/**.js', 'javascript'),
# ]

LOGGING = dict(loggers=dict(playdoh = {'level': logging.DEBUG}))


AUTHENTICATION_BACKENDS = (
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.static',
    'django_browserid.context_processors.browserid_form',
    'popcorn_gallery.users.context_processors.browserid_target_processor',
    'popcorn_gallery.base.context_processors.common',
    'popcorn_gallery.notifications.context_processors.notifications',
    )

TEMPLATE_DIRS = (
    path('popcorn_gallery', 'templates'),
    path('butter', 'templates'),
)


ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda o: "/profile/%s/" % o.username,
}

# funfactory locale middleware shouldn't change these urls.
SUPPORTED_NONLOCALES = ['media', 'admin', 'api', 'static', 'browserid',
                        'vote']

STATIC_URL = '/static/'

# admin is using the django.contrib.staticfiles
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

STATIC_ROOT = path('static')

STATICFILES_DIRS = (
    path('butter'),
    path('assets'),
    )


# user assets
TEMPLATE_MEDIA_ROOT = path('media', 'templates')
TEMPLATE_MEDIA_URL = '/media/templates/'

# contrib.messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# Browser ID
BROWSERID_CREATE_USER = True
LOGIN_REDIRECT_URL = '/dashboard/'
LOGIN_REDIRECT_URL_FAILURE = '/login/failed/'
LOGIN_URL = '/login/'

ANON_ALWAYS = True

AUTH_PROFILE_MODULE = 'users.Profile'


MIDDLEWARE_CLASSES += ('popcorn_gallery.users.middleware.ProfileMiddleware',)

POPCORN_TEMPLATES_ROOT = path('popcorn_gallery', 'templates')

INVALID_USERNAMES = ()

PROJECT_ROOT = path('')


# Valid domains for popcorn, must be lowercase
POPCORN_VALID_DOMAINS = (
    'mozillapopcorn.org',
    'www.youtube.com',
    'twitter.com',
    'vimeo.com',
    'local.mozillapopcorn.org',
    'popcornmaker-dev.allizom.org',
    )

EMAIL_BACKEND = 'django_mailer.smtp_queue.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[Popcorn] '

CACHE_MIDDLEWARE_KEY_PREFIX = 'popcorn'
# in minutes
CACHE_OBJECT_METADATA = 10

# haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': path('whoosh_index'),
        },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
