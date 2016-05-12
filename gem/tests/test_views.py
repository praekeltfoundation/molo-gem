from datetime import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from gem.models import GemSettings
from molo.commenting import MoloCommentForm

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


class CommentingTestCase(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.mk_main()

        self.yourmind = self.mk_section(
            self.main, title='Your mind')
        self.article = self.mk_article(self.yourmind,
                                       title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')

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

    def getData(self):
        return {
            'name': self.user.username,
            'email': self.user.email
        }

    def test_comment_shows_user_display_name(self):
        # check when user doesn't have an alias
        self.create_comment(self.article, 'test comment1 text')
        response = self.client.get('/your-mind/article-1/')
        self.assertContains(response, "Anonymous")

        # check when user have an alias
        self.user.profile.alias = 'this is my alias'
        self.user.profile.save()
        self.create_comment(self.article, 'test comment2 text')
        response = self.client.get('/your-mind/article-1/')
        self.assertContains(response, "this is my alias")
        self.assertNotContains(response, "tester")

    def getValidData(self, obj):
        form = MoloCommentForm(obj)
        form_data = self.getData()
        form_data.update(form.initial)
        return form_data

    def test_comment_filters(self):
        site = Site.objects.get(id=1)
        site.name = 'GEM'
        site.save()
        GemSettings.objects.create(site_id=site.id,
                                   banned_keywords_and_patterns='naughty')

        form_data = self.getValidData(self.article)

        # check if user has typed in a number
        comment_form = MoloCommentForm(
            self.article, data=dict(form_data, comment="0821111111")
        )

        self.assertFalse(comment_form.is_valid())

        # check if user has typed in an email address
        comment_form = MoloCommentForm(
            self.article, data=dict(form_data, comment="test@test.com")
        )

        self.assertFalse(comment_form.is_valid())

        # check if user has used a banned keyword
        comment_form = MoloCommentForm(
            self.article, data=dict(form_data, comment="naughty")
        )

        self.assertFalse(comment_form.is_valid())


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
