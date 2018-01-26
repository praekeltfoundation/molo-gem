# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.utils.translation import activate, ugettext

from molo.core.models import Languages, Main, PageTranslation
from molo.profiles.models import SecurityQuestionIndexPage, SecurityQuestion


class Command(BaseCommand):
    def handle(self, *args, **options):
        for question_number in range(1, 3):
            setting = 'SECURITY_QUESTION_{0}'.format(question_number)
            english_question_text = getattr(settings, setting, None)

            if english_question_text is None:
                raise ImproperlyConfigured(
                    'Security question {0} is unset'.format(setting))

            for main_page in Main.objects.all():
                security_index = SecurityQuestionIndexPage.objects.child_of(
                    main_page).first()

                site = main_page.get_site()

                main_language = Languages.for_site(site).languages.filter(
                    is_active=True, is_main_language=True,
                ).first()
                other_languages = Languages.for_site(site).languages.filter(
                    is_active=True, is_main_language=False,
                ).all()

                if main_language is None:
                    logging.info(
                        'Main language unset, not creating security questions')
                    continue

                activate(main_language.locale)
                question_text_main_language = ugettext(english_question_text)

                question = SecurityQuestion(title=question_text_main_language)
                security_index.add_child(instance=question)
                question.save_revision().publish()

                for language in other_languages:
                    activate(language.locale)
                    question_text_localised = ugettext(english_question_text)

                    question_localised = SecurityQuestion(
                        title=question_text_localised)
                    security_index.add_child(instance=question_localised)

                    question_language = question_localised.languages.first()
                    question_language.language = language
                    question_language.save()

                    question_localised.save_revision().publish()

                    PageTranslation.objects.get_or_create(
                        page=question,
                        translated_page=question_localised,
                    )
