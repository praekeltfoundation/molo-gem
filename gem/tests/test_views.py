from datetime import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from molo.core.tests.base import MoloTestCaseMixin
from molo.commenting.models import MoloComment

from gem.forms import GemRegistrationForm


class GemRegistrationViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_view(self):
        response = self.client.get(reverse('user_register'))
        self.assertTrue(isinstance(response.context['form'],
                        GemRegistrationForm))

    def test_register_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse('user_register'), {
        })
        self.assertFormError(
            response, 'form', 'username', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'password', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'gender', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'security_question_1_answer',
            ['This field is required.']
        )
        self.assertFormError(
            response, 'form', 'security_question_2_answer',
            ['This field is required.']
        )


class CommentingTestCase(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.mk_main()

    def create_comment(self, article, comment, parent=None):
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(article),
            object_pk=article.pk,
            content_object=article,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            parent=parent,
            submit_date=datetime.now())

    def test_comment_shows_user_display_name(self):
        self.yourmind = self.mk_section(
            self.main, title='Your mind')
        article = self.mk_article(self.yourmind, title='article 1',
                                  subtitle='article 1 subtitle',
                                  slug='article-1')

        # check when user doesn't have an alias
        self.create_comment(article, 'test comment1 text')
        response = self.client.get('/your-mind/article-1/')
        self.assertContains(response, "Anonymous")

        # check when user have an alias
        self.user.profile.alias = 'this is my alias'
        self.user.profile.save()
        self.create_comment(article, 'test comment2 text')
        response = self.client.get('/your-mind/article-1/')
        self.assertContains(response, "this is my alias")
        self.assertNotContains(response, "tester")


class GemFeedViewsTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.client = Client()

        self.mk_main()

        section_page = self.mk_section(self.english, title='Test Section')

        self.article_page = self.mk_article(
            section_page, title='Test Article',
            subtitle='This should appear in the feed')

    def test_rss_feed_view(self):
        response = self.client.get(reverse('feed_rss'))

        self.assertContains(response, self.article_page.title)
        self.assertContains(response, self.article_page.subtitle)
        self.assertNotContains(response, 'example.com')

    def test_atom_feed_view(self):
        response = self.client.get(reverse('feed_atom'))

        self.assertContains(response, self.article_page.title)
        self.assertContains(response, self.article_page.subtitle)
        self.assertNotContains(response, 'example.com')


class TagManagerAccountTestCase(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.client = Client()

    def test_gtm_account(self):
        response = self.client.get('/')
        self.assertNotContains(response, 'GTM-XXXXXX')

        with self.settings(GOOGLE_TAG_MANAGER_ACCOUNT='GTM-XXXXXX'):
            response = self.client.get('/')
            self.assertContains(response, 'GTM-XXXXXX')
