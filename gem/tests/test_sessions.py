import time

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.test.utils import override_settings
from molo.core.tests.base import MoloTestCaseMixin


@override_settings(SESSION_COOKIE_AGE=1)
class GemAutomaticLogoutTest(TestCase, MoloTestCaseMixin):
    """
    Note that SESSION_SAVE_EVERY_REQUEST must = True for this to work
    """
    def setUp(self):
        self.client = Client()
        self.mk_main()

        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

    def test_session_expires_if_no_activity_within_session_cookie_age(self):
        self.client.login(username='tester', password='tester')

        response = self.client.get('/profiles/view/myprofile/')

        self.assertContains(response, 'Hello tester')
        self.assertContains(response, 'log out')

        # wait for the session to expire
        time.sleep(1)

        response = self.client.get('/profiles/view/myprofile/', follow=True)

        # note that due to the value of the LOGIN_URL setting, users will be
        # redirected to the wagtail login page
        self.assertRedirects(response,
                             '/profiles/login/?next=/profiles/view/myprofile/')
        self.assertNotContains(response, 'Hello tester')
        self.assertNotContains(response, 'log out')

    def test_session_does_not_expire_if_activity_within_session_cookie_age(
            self
    ):
        self.client.login(username='tester', password='tester')

        response = self.client.get('/profiles/view/myprofile/')

        self.assertContains(response, 'Hello tester')
        self.assertContains(response, 'log out')

        # wait for less time than it takes for the session to expire
        time.sleep(0.5)

        response = self.client.get('/profiles/view/myprofile/')

        self.assertContains(response, 'Hello tester')
        self.assertContains(response, 'log out')

        # check that the previous request reset the timeout
        time.sleep(0.6)
        # more than SESSION_COOKIE_AGE seconds have passed since the first
        # request

        response = self.client.get('/profiles/view/myprofile/')

        self.assertContains(response, 'Hello tester')
        self.assertContains(response, 'log out')
