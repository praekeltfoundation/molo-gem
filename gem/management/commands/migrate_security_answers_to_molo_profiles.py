# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from molo.profiles.models import (
    SecurityAnswer,
    SecurityQuestion,
    SecurityQuestionIndexPage,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for question_number in range(1, 3):
            question_setting = 'SECURITY_QUESTION_{0}'.format(question_number)
            question_text = getattr(settings, question_setting, None)

            if question_text is None:
                raise ImproperlyConfigured(
                    'Security question {0} is unset'.format(question_setting))

            logging.info('Migrating answers for {0}'.format(question_setting))

            for user in get_user_model().objects.all():
                if not hasattr(user, 'profile'):
                    logging.warn('User {0} has no profile'.format(user.id))
                    continue

                main_page = user.profile.site.root_page
                security_index = SecurityQuestionIndexPage.objects.child_of(
                    main_page).first()

                question = SecurityQuestion.objects.filter(
                    title=question_text).child_of(security_index).first()

                if not question:
                    logging.warn('Unable to migrate "{0}" for {1}'.format(
                        question_text, user.id))
                    continue

                answer_hashes = [
                    user.gem_profile.security_question_1_answer,
                    user.gem_profile.security_question_2_answer,
                ]

                answer_hash = answer_hashes[question_number-1]

                if answer_hash is None or len(answer_hash) == 0:
                    logging.warn('User {0} has empty hash for {1}'.format(
                        user.id,
                        question_setting,
                    ))
                    continue

                security_answer, _ = SecurityAnswer.objects.get_or_create(
                    question=question,
                    user=user.profile,
                )
                security_answer.answer = answer_hash
                security_answer.save(is_import=True)
