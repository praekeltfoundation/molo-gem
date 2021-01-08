# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from os.path import join

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django_comments.models import Comment
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone
from six import StringIO

from wagtail.images.tests.utils import Image, get_test_image_file

from molo.core.models import (
    SiteLanguageRelation, Languages,
    ArticlePage, BannerPage, SectionIndexPage,
    BannerIndexPage, Tag, SectionPage)

from molo.commenting.models import MoloComment

from gem.tests.base import GemTestCaseMixin

from molo.forms.models import MoloFormPage, MoloFormSubmission
from molo.profiles.models import (
    UserProfile, SecurityAnswer, SecurityQuestion, SecurityQuestionIndexPage)


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
        self.assertEqual(
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
        self.assertEqual(new_spanish_article.title, u'¿Que tal?')
        self.assertEqual(new_spaced_article.title, u'spaced article title')
        self.assertFalse(spaced_article.live)
        self.assertEqual(new_russian_article.title, u'Ё ф')

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

    def test_change_content_language(self):
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='fr',
            is_active=True)
        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='es',
            is_active=True)
        self.yourmind2 = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your Mind')
        self.yourmind3 = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main).first(), title='Your mind 2')
        self.tag = self.mk_tag(
            SectionIndexPage.objects.child_of(self.main).first())
        self.tag2 = self.mk_tag(
            SectionIndexPage.objects.child_of(self.main).first())
        # make articles of different sections
        self.mk_articles(self.yourmind2, count=5)
        self.mk_articles(self.yourmind3, count=5)

        # translate the article into those languages
        self.mk_section_translation(self.yourmind2, self.french)
        self.mk_tag_translation(self.tag, self.french)
        articles = ArticlePage.objects.all()[1::2]
        for article in articles:
            self.mk_article_translation(article, self.french)
        fr_pk = self.french.pk
        sp_pk = self.spanish.pk

        fr_articles = [article.title for article in
                       ArticlePage.objects.filter(language=self.french)]
        fr_tags = [tag.title for tag in
                   Tag.objects.filter(language=self.french)]

        fr_sections = [section.title for section in
                       SectionPage.objects.filter(language=self.french)]

        out = StringIO()
        call_command(
            'change_content_language',
            fr_pk, sp_pk, stdout=out
        )
        self.assertEqual('', out.getvalue())
        # test that only the correct articles are translated
        sp_articles = [article.title for article in
                       ArticlePage.objects.filter(language=self.spanish)]

        sp_tags = [tag.title for tag in
                   Tag.objects.filter(language=self.spanish)]

        sp_sections = [section.title for section in
                       SectionPage.objects.filter(language=self.spanish)]

        self.assertEqual(sp_articles, fr_articles)
        self.assertEqual(sp_tags, fr_tags)
        self.assertEqual(sp_sections, fr_sections)

    def test_change_content_language__invalid_languages(self):
        self.yourmind2 = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your Mind')
        self.yourmind3 = self.mk_section(
            SectionIndexPage.objects.child_of(
                self.main).first(), title='Your mind 2')
        # make articles of different sections
        self.mk_articles(self.yourmind2, count=5)
        self.mk_articles(self.yourmind3, count=5)

        # translate the article into those languages
        out = StringIO()
        call_command(
            'change_content_language',
            None, None, stdout=out
        )
        self.assertNotEqual('', out.getvalue())


class TestRemoveDeprecatedSiteContent(GemManagementCommandsTest):
    def setUp(self):
        super().setUp()

        # Create content
        section_index = SectionIndexPage.objects.child_of(self.main).first()
        section = self.mk_section(section_index, title='Section')
        article = self.mk_article(
            parent=section, title='Article')

        # Note: this 'site' attr is the django site, not the wagtail one
        MoloComment.objects.create(
            content_type=self.content_type,
            site=Site.objects.get_current(),
            object_pk=article.pk,
            user=self.user,
            comment="Here's a comment",
            submit_date=timezone.now())

        form = MoloFormPage(
            title='Form',
            slug='form',
        )
        section_index.add_child(instance=form)
        form.save_revision().publish()
        MoloFormSubmission.objects.create(
            form_data='{"checkbox-question": ["option 1", "option 2"]}',
            user=self.user,
            page_id=form.pk
        )

        self.profile = self.user.profile
        sq_index = SecurityQuestionIndexPage.objects.child_of(
            self.main).first()
        sec_q = SecurityQuestion(title='Sec Question')
        sq_index.add_child(instance=sec_q)
        sec_q.save_revision().publish()
        SecurityAnswer.objects.create(
            user=self.profile, question=sec_q, answer="Sec Answer")

    def test_raises_error_for_invalid_site_id(self):
        out = StringIO()

        with self.assertRaises(CommandError) as e:
            call_command(
                'remove_deprecated_site_data',
                '999', stdout=out
            )

        self.assertEqual('Site "999" does not exist', str(e.exception))

    def test_without_commit_only_lists_data(self):
        out = StringIO()
        call_command(
            'remove_deprecated_site_data',
            self.profile.site.pk, stdout=out
        )

        self.assertEqual(MoloComment.objects.all().count(), 1)
        self.assertEqual(MoloFormSubmission.objects.all().count(), 1)
        self.assertEqual(SecurityAnswer.objects.all().count(), 1)
        self.assertEqual(User.objects.filter(username='test').count(), 1)
        self.assertEqual(UserProfile.objects.filter(
            site=self.profile.site.pk).count(), 1)

        self.assertIn('Found 1 profiles for site 3', out.getvalue())
        self.assertIn('Found 0 staff profiles', out.getvalue())
        self.assertIn('Found 1 comments', out.getvalue())
        self.assertIn('Found 1 form submissions', out.getvalue())
        self.assertIn('Found 1 security question answers', out.getvalue())

    def test_removes_all_data(self):
        # Confirm data exists
        self.assertEqual(MoloComment.objects.all().count(), 1)
        self.assertEqual(MoloFormSubmission.objects.all().count(), 1)
        self.assertEqual(SecurityAnswer.objects.all().count(), 1)
        self.assertEqual(User.objects.filter(username='test').count(), 1)
        self.assertEqual(UserProfile.objects.filter(
            site=self.profile.site.pk).count(), 1)

        out = StringIO()
        call_command(
            'remove_deprecated_site_data',
            self.profile.site.pk, '--commit', stdout=out
        )

        self.assertEqual(MoloComment.objects.all().count(), 0)
        self.assertEqual(MoloFormSubmission.objects.all().count(), 0)
        self.assertEqual(SecurityAnswer.objects.all().count(), 0)
        self.assertEqual(User.objects.filter(username='test').count(), 0)
        self.assertEqual(UserProfile.objects.filter(
            site=self.profile.site.pk).count(), 0)

        self.assertIn('Found 1 profiles for site 3', out.getvalue())
        self.assertIn('Found 0 staff profiles', out.getvalue())
        self.assertIn('Found 1 comments', out.getvalue())
        self.assertIn('Found 1 form submissions', out.getvalue())
        self.assertIn('Found 1 security question answers', out.getvalue())

    def test_doesnt_process_staff_data(self):
        self.user.is_staff = True
        self.user.save()

        out = StringIO()
        call_command(
            'remove_deprecated_site_data',
            self.profile.site.pk, '--commit', stdout=out
        )

        self.assertEqual(MoloComment.objects.all().count(), 1)
        self.assertEqual(MoloFormSubmission.objects.all().count(), 1)
        self.assertEqual(SecurityAnswer.objects.all().count(), 1)
        self.assertEqual(User.objects.filter(username='test').count(), 1)
        self.assertEqual(UserProfile.objects.filter(
            site=self.profile.site.pk).count(), 1)

        self.assertIn('Found 1 profiles for site 3', out.getvalue())
        self.assertIn('Found 1 staff profiles', out.getvalue())
        self.assertIn('Found 0 comments', out.getvalue())
        self.assertIn('Found 0 form submissions', out.getvalue())
        self.assertIn('Found 0 security question answers', out.getvalue())

    def test__doesnt_remove_data_from_other_sites(self):
        user2 = User.objects.create_user(
            'test2', 'test2@example.org', 'test2')
        user2.profile.site = self.main2.get_site()
        user2.profile.save()

        # Create content
        section_index_2 = SectionIndexPage.objects.child_of(self.main2).first()
        section = self.mk_section(section_index_2, title='Section 2')
        article = self.mk_article(
            parent=section, title='Article 2')

        # Note: this 'site' attr is the django site, not the wagtail one
        MoloComment.objects.create(
            content_type=self.content_type,
            site=Site.objects.get_current(),
            object_pk=article.pk,
            user=user2,
            comment="Here's a 2nd comment",
            submit_date=timezone.now())

        form_2 = MoloFormPage(
            title='Form 2',
            slug='form-2',
        )
        section_index_2.add_child(instance=form_2)
        form_2.save_revision().publish()
        MoloFormSubmission.objects.create(
            form_data='{"checkbox-question": ["option 1", "option 2"]}',
            user=user2,
            page_id=form_2.pk
        )

        profile2 = user2.profile
        sq_index_2 = SecurityQuestionIndexPage.objects.child_of(
            self.main2).first()
        sec_q = SecurityQuestion(title='Sec Question 2')
        sq_index_2.add_child(instance=sec_q)
        sec_q.save_revision().publish()
        SecurityAnswer.objects.create(
            user=profile2, question=sec_q, answer="Sec Answer 2")

        out = StringIO()
        call_command(
            'remove_deprecated_site_data',
            profile2.site.pk, '--commit', stdout=out
        )

        comments = MoloComment.objects.all()
        self.assertEqual(comments.count(), 1)
        self.assertNotEqual(comments.first().user, user2)

        submissions = MoloFormSubmission.objects.all()
        self.assertEqual(submissions.count(), 1)
        self.assertNotEqual(submissions.first().user, user2)

        answers = SecurityAnswer.objects.all()
        self.assertEqual(answers.count(), 1)
        self.assertNotEqual(answers.first().user, user2)

        users = User.objects.filter(username__contains='test')
        self.assertEqual(users.count(), 1)
        self.assertNotEqual(users.first(), user2)

        self.assertEqual(UserProfile.objects.filter(
            site=profile2.site.pk).count(), 0)

        self.assertIn('Found 1 profiles for site 5', out.getvalue())
        self.assertIn('Found 0 staff profiles', out.getvalue())


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
