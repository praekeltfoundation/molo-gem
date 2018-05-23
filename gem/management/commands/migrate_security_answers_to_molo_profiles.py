# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        # This management command was created to migrate security answers from
        # a user's gem_profile to their molo profile. It's referenced in
        # migration 0026 so we can't remove the whole command without modifying
        # the file, but we it's in production so we never need to run it again.
        pass
