# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import csv
from django.core.management.base import BaseCommand
from molo.core.models import (
    Languages, ReactionQuestion, ReactionQuestionChoice,
    ReactionQuestionIndexPage, PageTranslation, Main)
from wagtail.images.tests.utils import Image


class Command(BaseCommand):
    def handle(self, **options):
        mains = Main.objects.all()
        reaction_questions = {}
        with open('data/reaction_questions.csv') as reaction_questions_csv:
            reader = csv.DictReader(reaction_questions_csv)
            if mains:
                for row in reader:
                    key = row.pop('Questions')
                    reaction_questions[key] = row

        question_choices = {}
        with open(
                'data/reaction_question_choices.csv') as question_choices_csv:
            reader = csv.DictReader(question_choices_csv)
            if mains:
                for row in reader:
                    key = row.pop('Choices')
                    question_choices[key] = row

        choice_messeges = {}
        with open('data/question_choice_messeges.csv') as choice_messeges_csv:
            reader = csv.DictReader(choice_messeges_csv)
            if mains:
                for row in reader:
                    key = row.pop('Choices')
                    choice_messeges[key] = row

        for main in mains:
            question_index = ReactionQuestionIndexPage.objects.child_of(
                main).first()
            main_lang = Languages.for_site(main.get_site()).languages.filter(
                is_active=True, is_main_language=True).first()
            child_languages = Languages.for_site(
                main.get_site()).languages.filter(
                is_active=True, is_main_language=False).all()
            if main_lang:
                self.add_reaction_questions(
                    main_lang, child_languages, question_index,
                    reaction_questions, question_choices, choice_messeges)
            else:
                self.stdout.write(self.style.NOTICE(
                    'Main language does not exist in "%s"' % main))

    def add_reaction_questions(
        self, main_lang, child_languages, question_index,
            reaction_questions, question_choices, messages):
        for reaction_question in reaction_questions:
            if reaction_questions.get(reaction_question).get(main_lang.locale):
                main_reaction_question = self.create_reaction_question(
                    reaction_questions.get(
                        reaction_question).get(main_lang.locale),
                    question_index)
                self.add_reaction_choices(
                    main_lang, child_languages,
                    main_reaction_question, question_choices, messages)

                for child_lang in child_languages:
                    if reaction_questions.get(
                            reaction_question).get(child_lang.locale):
                        self.create_reaction_question_translation(
                            main_reaction_question, child_lang,
                            reaction_questions.get(reaction_question).get(
                                child_lang.locale), question_index)
                    else:
                        self.stdout.write(self.style.NOTICE(
                            'Reaction question %s does not exist '
                            'for %s in the CSV'
                            % (reaction_question, child_lang)))
            else:
                self.stdout.write(self.style.NOTICE(
                    'Reaction question %s does not exist for %s in the CSV' % (
                        reaction_question, main_lang)))

    def create_reaction_question(self, title, question_index):
        reaction_question = ReactionQuestion.objects.filter(
            title=title).child_of(question_index).first()
        if reaction_question:
            return reaction_question
        else:
            reaction_question = ReactionQuestion(title=title)
            question_index.add_child(instance=reaction_question)
            reaction_question.save_revision().publish()
            return reaction_question

    def create_reaction_question_translation(
            self, main_reaction_question, language, trans_title,
            question_index):
        if not ReactionQuestion.objects.filter(
                title=trans_title).child_of(question_index).exists():
            translated_reaction_question = self.create_reaction_question(
                trans_title, question_index)
            if translated_reaction_question:
                lang_relation = translated_reaction_question.languages.first()
                lang_relation.language = language
                lang_relation.save()
                translated_reaction_question.save_revision().publish()
                PageTranslation.objects.get_or_create(
                    page=main_reaction_question,
                    translated_page=translated_reaction_question)

    def add_reaction_choices(
            self, main_lang, child_languages, question,
            reaction_choices, messages):
        for reaction_choice in reaction_choices:
            if reaction_choices.get(reaction_choice).get(main_lang.locale):
                main_reaction_choice = self.create_reaction_choice(
                    reaction_choices.get(reaction_choice).get(
                        main_lang.locale),
                    question, main_lang.locale, messages.get(
                        reaction_choice).get(main_lang.locale))
                self.create_reaction_choice_image(
                    main_reaction_choice, messages.get(
                        reaction_choice).get(main_lang.locale))

                for child_lang in child_languages:
                    if reaction_choices.get(
                            reaction_choice).get(child_lang.locale):
                        self.create_reaction_choice_translation(
                            main_reaction_choice, child_lang,
                            reaction_choices.get(reaction_choice).get(
                                child_lang.locale), question, messages.get(
                                    reaction_choice).get(child_lang.locale))
                    else:
                        self.stdout.write(self.style.NOTICE(
                            'Reaction choice %s does not exist '
                            'for %s in the CSV'
                            % (reaction_choice, child_lang)))
            else:
                self.stdout.write(self.style.NOTICE(
                    'Reaction choice %s does not exist for %s in the CSV' % (
                        reaction_choice, main_lang)))

    def create_reaction_choice(self, title, question, language, message):
        reaction_choice = ReactionQuestionChoice.objects.filter(
            title=title,
            languages__language__locale=language).child_of(
            question).first()
        if reaction_choice:
            return reaction_choice
        else:
            reaction_choice = ReactionQuestionChoice(
                title=title, success_message=message)
            question.add_child(instance=reaction_choice)
            reaction_choice.save_revision().publish()
            return reaction_choice

    def create_reaction_choice_translation(
            self, main_reaction_choice, language, trans_title,
            question, message):
        if not ReactionQuestionChoice.objects.filter(
                title=trans_title,
                languages__language__locale=language.locale).child_of(
                question).exists():
            translated_reaction_choice = self.create_reaction_choice(
                trans_title, question, language, message)
            if translated_reaction_choice:
                lang_relation = translated_reaction_choice.languages.first()
                lang_relation.language = language
                lang_relation.save()
                translated_reaction_choice.save_revision().publish()
                PageTranslation.objects.get_or_create(
                    page=main_reaction_choice,
                    translated_page=translated_reaction_choice)

    def create_reaction_choice_image(self, main_reaction_choice, message):
            choice_image = Image.objects.filter(
                title=str(main_reaction_choice) + ".png").first()
            success_image = Image.objects.filter(
                title=str(message) + ".png").first()
            if choice_image:
                main_reaction_choice.image = choice_image
                main_reaction_choice.success_image = success_image
                main_reaction_choice.save_revision().publish()
