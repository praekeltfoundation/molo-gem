from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO
from wagtail.wagtailimages.tests.utils import Image, get_test_image_file
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (SiteLanguageRelation, Main, Languages,
                              ReactionQuestion, ReactionQuestionChoice)


class GemManagementCommandsTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        Image.objects.create(
            title="Yes.png",
            file=get_test_image_file(),
        )
        Image.objects.create(
            title="No.png",
            file=get_test_image_file(),
        )
        Image.objects.create(
            title="Maybe.png",
            file=get_test_image_file(),
        )

    def test_add_reaction_questions_and_choices_command(self):
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('Main language does not exist in "Main"', out.getvalue())

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 4)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 3)
        self.assertEqual(
            str(choices.first().image), str(choices.first()) + ".png")

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='es',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 8)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 6)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='ar',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 12)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 9)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 16)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 12)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='bn',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 20)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 15)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='ur',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 24)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 18)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='sw',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 28)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 21)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='th',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 32)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 24)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='pt',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 36)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 27)
        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='ru',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 40)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 30)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='km',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 44)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 33)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='my',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 48)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 36)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='id',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 52)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 39)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='ha',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 56)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 42)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='tl',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 60)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 45)
