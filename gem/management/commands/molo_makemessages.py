from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand

from distutils.dir_util import copy_tree, remove_tree
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, **options):
        fromDirectory = "ve/lib/python2.7/site-packages/molo"
        toDirectory = "temp/temp_ve"
        copy_tree(fromDirectory, toDirectory)
        call_command(
            'makemessages',
            locale=('en',),
            ignore=['ve/*', 'admin/*', 'wagtail*', 'models.py',
                    'rules.py', 'node_modules/*'],
            verbosity=1)
        remove_tree(toDirectory)
