from gem.settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'gem_test.db',
    }
}

DEBUG = True
CELERY_ALWAYS_EAGER = True

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
