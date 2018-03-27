from __future__ import absolute_import

import os

from celery import Celery
from celery.signals import celeryd_init

from django.conf import settings
from django.core.management import call_command

from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'gem.settings.production')

app = Celery('proj')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if hasattr(settings, 'RAVEN_DSN'):
    raven_client = Client(settings.RAVEN_DSN)

    register_logger_signal(raven_client)
    register_signal(raven_client)


@celeryd_init.connect
def ensure_search_index_updated(sender, instance, **kwargs):
    '''
    Run update_index when celery starts
    '''
    try:
        from wagtail.wagtailsearch.backends.db import DBSearch
        backend = DBSearch
    except ImportError:
        from wagtail.wagtailsearch.backends.db import DatabaseSearchBackend
        backend = DatabaseSearchBackend

    from wagtail.wagtailsearch.backends import get_search_backend

    if not isinstance(get_search_backend(), backend):
        call_command('update_index')
