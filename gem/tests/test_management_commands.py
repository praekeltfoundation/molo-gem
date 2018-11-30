# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django_comments.models import Comment
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django.utils.six import StringIO
from wagtail.wagtailimages.tests.utils import Image, get_test_image_file
from molo.commenting.models import MoloComment
from gem.tests.base import GemTestCaseMixin
from molo.core.models import (SiteLanguageRelation, Languages,
                              ReactionQuestion, ReactionQuestionChoice,
                              ArticlePage, BannerPage, SectionIndexPage,
                              BannerIndexPage, TagIndexPage, Tag)
from os.path import join


class GemManagementCommandsTest(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.language_setting = Languages.objects.get(
            site_id=self.main.get_site().pk)
        self.main2 = self.mk_main(
            title='main2', slug='main2', path='00010003', url_path='/main2/')

        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')

        self.content_type = ContentType.objects.get_for_model(self.user)
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

    def test_create_new_banner_relations(self):
        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')
        self.yourmind2 = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main2).first(), title='Your mind')
        first_main_article = self.mk_article(
            parent=self.yourmind, title='first_main_article')
        first_main_banner = BannerPage(
            title='first_main_banner', slug='firstmainbanner',
            banner_link_page=first_main_article)
        self.banner_index = BannerIndexPage.objects.child_of(
            self.main).first()
        self.banner_index.add_child(instance=first_main_banner)
        first_main_banner.save_revision().publish()
        second_main_article = self.mk_article(
            parent=self.yourmind2, title='first_main_article')
        second_main_article.slug = first_main_article.slug
        second_main_article.save_revision().publish()
        second_main_banner = BannerPage(
            title='second_main_banner', slug='secondmainbanner',
            banner_link_page=first_main_article)
        self.banner_index2 = BannerIndexPage.objects.child_of(
            self.main2).first()
        self.banner_index2.add_child(instance=second_main_banner)
        second_main_banner.save_revision().publish()

        out = StringIO()
        call_command('create_new_banner_link_page_relations', stdout=out)
        second_main_banner = BannerPage.objects.get(pk=second_main_banner.pk)
        self.assertEquals(
            second_main_banner.banner_link_page.pk, second_main_article.pk)

    def test_convert_title_to_sentence_case(self):
        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main).first(), title='Your mind')
        spanish_capitals_spaced_article = self.mk_article(
            parent=self.yourmind, title=' ¿QUE TAL?')
        spaced_article = self.mk_article(
            parent=self.yourmind, title='  spaced article title')
        spaced_article.unpublish()
        self.assertFalse(spaced_article.live)
        russian_capitals_article = self.mk_article(
            parent=self.yourmind, title='Ё Ф')
        out = StringIO()
        call_command('format_titles_sentence_case', stdout=out)
        new_spanish_article = ArticlePage.objects.get(
            pk=spanish_capitals_spaced_article.pk)
        new_spaced_article = ArticlePage.objects.get(
            pk=spaced_article.pk)
        new_russian_article = ArticlePage.objects.get(
            pk=russian_capitals_article.pk)
        self.assertEquals(new_spanish_article.title, u'¿Que tal?')
        self.assertEquals(new_spaced_article.title, u'spaced article title')
        self.assertFalse(spaced_article.live)
        self.assertEquals(new_russian_article.title, u'Ё ф')

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
        self.assertEqual(reaction_question.count(), 8)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 3)
        self.assertEqual(
            str(choices.first().image), str(choices.first()) + ".png")
        self.assertTrue(choices.first().success_message)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='es',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 12)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 6)
        self.assertTrue(choices.first().success_message)

        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='ar',
            is_active=True)
        out = StringIO()
        call_command('add_reaction_questions_and_choices', stdout=out)
        self.assertIn('', out.getvalue())
        reaction_question = ReactionQuestion.objects.all()
        self.assertEqual(reaction_question.count(), 16)
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
        self.assertEqual(reaction_question.count(), 20)
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
        self.assertEqual(reaction_question.count(), 24)
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
        self.assertEqual(reaction_question.count(), 28)
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
        self.assertEqual(reaction_question.count(), 32)
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
        self.assertEqual(reaction_question.count(), 36)
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
        self.assertEqual(reaction_question.count(), 40)
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
        self.assertEqual(reaction_question.count(), 44)
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
        self.assertEqual(reaction_question.count(), 48)
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
        self.assertEqual(reaction_question.count(), 52)
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
        self.assertEqual(reaction_question.count(), 56)
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
        self.assertEqual(reaction_question.count(), 60)
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
        self.assertEqual(reaction_question.count(), 64)
        choices = ReactionQuestionChoice.objects.child_of(
            reaction_question.first())
        self.assertEqual(choices.count(), 45)

    def test_add_images_to_articles(self):
        out = StringIO()
        call_command('add_images_to_articles', 'data/articles_image.csv',
                     'en', stdout=out)
        self.assertIn('Main language does not exist in "Main"', out.getvalue())

        out = StringIO()
        call_command('add_images_to_articles', 'data/articles_image.csv',
                     'en', stdout=out)
        self.assertIn('Article "it-gets-better" does not exist in'
                      ' "main1-1.localhost"', out.getvalue())

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')
        article = self.mk_article(
            self.yourmind, title='it gets better', slug='it-gets-better')
        out = StringIO()
        call_command('add_images_to_articles', 'data/articles_image.csv',
                     'en', stdout=out)
        self.assertIn('Image "01_happygirl_feature_It gets better"'
                      ' does not exist in "main1"', out.getvalue())

        Image.objects.create(
            title="01_happygirl_feature_It gets better.jpg",
            file=get_test_image_file(),
        )
        call_command('add_images_to_articles', 'data/articles_image.csv',
                     'en', stdout=out)
        article.refresh_from_db()
        self.assertEqual(str(article.image),
                         "01_happygirl_feature_It gets better.jpg")

    def test_remove_placeholder_text_from_comments(self):
        SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main).first(), title='Your mind')
        article = self.mk_article(
            self.yourmind, title='it gets better', slug='it-gets-better')

        MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=article.pk,
            content_object=self.user,
            site=Site.objects.get_current(),
            user=self.user,
            comment="comment without place holder text",
            submit_date=timezone.now())

        MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=article.pk,
            content_object=self.user,
            site=Site.objects.get_current(),
            user=self.user,
            comment="Type your comment here...comment with placeholder text",
            submit_date=timezone.now())

        MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=article.pk,
            content_object=self.user,
            site=Site.objects.get_current(),
            user=self.user,
            comment="some text before theplaceholder"
            " Type your comment here...more text after the place holder",
            submit_date=timezone.now())

        call_command(
            'remove_placeholder_text_from_comments',
            'Type your comment here...'
        )

        for comment in Comment.objects.all().iterator():
            self.assertNotIn(comment.comment, 'Type your comment here...')


class AddDefaultTagsTest(TestCase):
    def test_command_works(self):
        call_command('add_default_tags')


class AddDefaultTagsToArticlesTest(TestCase):
    def test_command_works(self):
        csv_file = join('gem', 'tests', 'fixtures',
                        'add_default_tags_to_articles.csv')
        call_command('add_default_tags_to_articles', csv_file, 'en')


class AddImagesToSectionsTest(TestCase, GemTestCaseMixin):
    def test_command_works(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        call_command('add_images_to_sections', 'en')


class RemoveEmptyNavigationTags(TestCase, GemTestCaseMixin):
    def test_command_works(self):
        """
            Test that deleted navigation tags are removed
            from articles
        """
        main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        tag_index = TagIndexPage.objects.child_of(main).first()
        yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(main).first(),
            title='Your mind')
        article = self.mk_article(
            parent=yourmind, title='first_main_article')
        tag = Tag(title='New tag')
        tag_index.add_child(instance=tag)
        tag.save_revision().publish()
        tag2 = Tag(title='New tag 2')
        tag_index.add_child(instance=tag2)
        tag2.save_revision().publish()
        article.nav_tags.create(tag=tag)
        article.nav_tags.create(tag=tag2)
        article.save_revision().publish()
        self.assertTrue(article.nav_tags.get(tag=tag).tag)
        self.assertTrue(article.nav_tags.get(tag=tag2).tag)
        self.assertEqual(article.nav_tags.count(), 2)
        # delete the first tag
        tag.delete()
        # test that the article still refers to the deleted tag
        self.assertEqual(article.nav_tags.count(), 2)
        self.assertEqual(article.nav_tags.all()[0].tag.title, 'New tag')

        call_command(
            'remove_empty_nav_tags',
        )
        article = ArticlePage.objects.get(pk=article.pk)
        # test that the article only points to existing tags
        self.assertEqual(article.nav_tags.count(), 1)
        self.assertEqual(article.nav_tags.all()[0].tag.title, 'New tag 2')

        site = main.sites_rooted_here.all().first()
        # delete the second tag and the main's site
        tag2.delete()
        site.delete()

        # test that an integrity error is thrown
        self.assertEqual(
            call_command('remove_empty_nav_tags',),
            "IntegrityError: Only articles with sites can be saved",
        )

    def test_command_works_with_unpublished_articles(self):
        """
            Test that deleted navigation tags are removed
            from articles
        """
        main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        tag_index = TagIndexPage.objects.child_of(main).first()
        yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(main).first(),
            title='Your mind')
        article = self.mk_article(
            parent=yourmind, title='first_main_article')
        tag = Tag(title='New tag')
        tag_index.add_child(instance=tag)
        tag.save_revision()
        tag2 = Tag(title='New tag 2')
        tag_index.add_child(instance=tag2)
        tag2.save()
        article.nav_tags.create(tag=tag)
        article.nav_tags.create(tag=tag2)
        article.save()
        self.assertTrue(article.nav_tags.get(tag=tag).tag)
        self.assertTrue(article.nav_tags.get(tag=tag2).tag)
        self.assertEqual(article.nav_tags.count(), 2)
        # delete the first tag
        tag.delete()
        # test that the article still refers to the deleted tag
        self.assertEqual(article.nav_tags.count(), 2)

        call_command(
            'remove_empty_nav_tags',
        )
        article = ArticlePage.objects.get(pk=article.pk)
        # test that the article only points to existing tags

        self.assertEqual(article.nav_tags.count(), 1)
        self.assertEqual(article.nav_tags.all()[0].tag.title, 'New tag 2')
