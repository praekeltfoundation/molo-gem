from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from gem.forms import GemRegistrationForm
from molo.core.tests.base import MoloTestCaseMixin


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

    def test_atom_feed_view(self):
        response = self.client.get(reverse('feed_atom'))

        self.assertContains(response, self.article_page.title)
        self.assertContains(response, self.article_page.subtitle)
