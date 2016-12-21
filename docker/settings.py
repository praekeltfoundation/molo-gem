"""Django settings for use within the docker container."""

from os import environ

import dj_database_url

from .production import *


# Disable debug mode

DEBUG = False

SECRET_KEY = environ.get('SECRET_KEY') or 'please-change-me'
PROJECT_ROOT = (
    environ.get('PROJECT_ROOT') or dirname(dirname(abspath(__file__))))

SERVICE_DIRECTORY_API_BASE_URL = environ.get(
    'SERVICE_DIRECTORY_API_BASE_URL', '')
SERVICE_DIRECTORY_API_USERNAME = environ.get(
    'SERVICE_DIRECTORY_API_USERNAME', '')
SERVICE_DIRECTORY_API_PASSWORD = environ.get(
    'SERVICE_DIRECTORY_API_PASSWORD', '')

GOOGLE_PLACES_API_SERVER_KEY = environ.get(
    'GOOGLE_PLACES_API_SERVER_KEY', '')

RAVEN_DSN = environ.get('RAVEN_DSN')
RAVEN_CONFIG = {'dsn': RAVEN_DSN} if RAVEN_DSN else {}

CAS_SERVER_URL = environ.get('CAS_SERVER_URL') or ''

COMPRESS_OFFLINE = True

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///%s' % (join(PROJECT_ROOT, 'gemmolo.db'),))}

MEDIA_ROOT = join(PROJECT_ROOT, 'media')

STATIC_ROOT = join(PROJECT_ROOT, 'static')

LOCALE_PATHS = (
    join(PROJECT_ROOT, "locale"),
)

ES_HOST = environ.get('ES_HOST')
ES_INDEX = environ.get('ES_INDEX')
ES_VERSION = int(environ.get('ES_VERSION', 2))

ES_BACKEND_V1 = 'molo.core.wagtailsearch.backends.elasticsearch'
ES_BACKEND_V2 = 'molo.core.wagtailsearch.backends.elasticsearch2'

if ES_HOST:
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND':
                ES_BACKEND_V2 if ES_VERSION == 2 else ES_BACKEND_V1,
            'URLS': [ES_HOST],
            'INDEX':
                ES_INDEX or environ.get('MARATHON_APP_ID') or 'gem',
        },
    }
