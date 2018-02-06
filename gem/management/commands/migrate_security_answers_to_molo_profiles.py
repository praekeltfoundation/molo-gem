# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from gem.tasks import migrate_security_answers_to_profiles


class Command(BaseCommand):
    def handle(self, *args, **options):
        for question_number in range(1, 3):
            question_setting = 'SECURITY_QUESTION_{0}'.format(question_number)
            question_text = getattr(settings, question_setting, None)

            if question_text is None:
                raise ImproperlyConfigured(
                    'Security question {0} is unset'.format(question_setting))

            logging.info('Migrating answers for {0}'.format(question_setting))

            migrate_security_answers_to_profiles.delay(
                question_text, question_number, question_setting)
