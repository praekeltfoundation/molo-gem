import os
from .base import *  # noqa


# Disable debug mode

DEBUG = False
ENV = 'prd'

# Compress static files offline
# http://django-compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_OFFLINE

COMPRESS_OFFLINE = True


# Send notification emails as a background task using Celery,
# to prevent this from blocking web server threads
# (requires the django-celery package):
# http://celery.readthedocs.org/en/latest/configuration.html

# import djcelery
#
# djcelery.setup_loader()
#
# CELERY_SEND_TASK_ERROR_EMAILS = True
# BROKER_URL = 'redis://'


# Use Redis as the cache backend for extra performance
# (requires the django-redis-cache package):
# http://wagtail.readthedocs.org/en/latest/howto/performance.html#cache

# CACHES = {
#     'default': {
#         'BACKEND': 'redis_cache.cache.RedisCache',
#         'LOCATION': '127.0.0.1:6379',
#         'KEY_PREFIX': 'base',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
#         }
#     }
# }


# service-directory settings
# NB: You should also have a secrets.py file that contains the settings
# SERVICE_DIRECTORY_API_USERNAME & SERVICE_DIRECTORY_API_PASSWORD &
# GOOGLE_PLACES_API_SERVER_KEY
SERVICE_DIRECTORY_API_BASE_URL = 'http://gem-sd.qa.praekelt.com/api/'

# try to fetch settings from environment variables
SERVICE_DIRECTORY_API_USERNAME = os.environ.get(
    'SERVICE_DIRECTORY_API_USERNAME', None
)
SERVICE_DIRECTORY_API_PASSWORD = os.environ.get(
    'SERVICE_DIRECTORY_API_PASSWORD', None
)

GOOGLE_PLACES_API_SERVER_KEY = os.environ.get(
    'GOOGLE_PLACES_API_SERVER_KEY', None
)

# Setup for CAS
ENABLE_SSO = True

MIDDLEWARE_CLASSES += [
    'molo.core.middleware.MoloCASMiddleware',
    'molo.core.middleware.Custom403Middleware',
]


AUTHENTICATION_BACKENDS = [
    'gem.backends.GemModelBackend',
    'django.contrib.auth.backends.ModelBackend',
    'molo.core.backends.MoloCASBackend',
]

CAS_SERVER_URL = ''
CAS_ADMIN_PREFIX = '/admin/'
LOGIN_URL = 'molo.profiles:auth_login'
CAS_VERSION = '3'


COMPRESS_OFFLINE_CONTEXT = {  # noqa
    'STATIC_URL': STATIC_URL,  # noqa
    'ENV': ENV,  # noqa
}  # noqa

DEFAULT_TEMPLATE['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        "django.template.loaders.filesystem.Loader",
        "mote.loaders.app_directories.Loader",
        "django.template.loaders.app_directories.Loader", ]),
]

TEMPLATES = [
    DEFAULT_TEMPLATE,
]

try:
    from .local import *  # noqa
except ImportError:
    pass

try:
    from secrets import *  # noqa
except ImportError:
    pass
