from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from gem.context_processors import (
    compress_settings,
    detect_freebasics,
    detect_kaios,
)
from gem.tests.base import GemTestCaseMixin


class TestDetectKaiOS(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_returns_false_for_requests_without_kaios_subdomain(self):
        request = self.request_factory.get('/')
        self.assertEqual(detect_kaios(request), {'is_via_kaios': False})

    def test_returns_true_for_requests_with_kaios_subdomain(self):
        request = self.request_factory.get('/', HTTP_HOST='kaios.localhost:80')
        self.assertEqual(detect_kaios(request), {'is_via_kaios': True})


class TestDetectFreebasics(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_returns_false_by_default(self):
        request = self.request_factory.get('/')
        self.assertEqual(
            detect_freebasics(request),
            {'is_via_freebasics': False},
        )

    def test_returns_true_if_internetorg_in_httpvia(self):
        request = self.request_factory.get('/', HTTP_VIA='Internet.org')
        self.assertEqual(
            detect_freebasics(request),
            {'is_via_freebasics': True},
        )

    def test_returns_true_if_internetorgapp_in_user_agent(self):
        request = self.request_factory.get(
            '/',
            HTTP_USER_AGENT='InternetOrgApp',
        )
        self.assertEqual(
            detect_freebasics(request),
            {'is_via_freebasics': True},
        )

    def test_returns_true_if_true_in_xiorgsfbs(self):
        request = self.request_factory.get('/', HTTP_X_IORG_FBS='true')
        self.assertEqual(
            detect_freebasics(request),
            {'is_via_freebasics': True},
        )


class TestCompressSettings(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')

    @override_settings(ENV='test_env', STATIC_URL='test_static_url')
    def test_returns_settings(self):
        request = RequestFactory().get('/')
        self.assertEqual(
            compress_settings(request),
            {
                'LOGIN_URL': reverse('molo.profiles:auth_login'),
                'VIEW_PROFILE_URL': u'/profiles/view/myprofile/',
                'EDIT_PROFILE_URL': u'/profiles/edit/myprofile/',
                'REGISTRATION_URL': u'/profiles/register/',
                'LOGOUT_URL': reverse('molo.profiles:auth_logout'),
                'ENV': 'test_env',
                'STATIC_URL': '/test_static_url',
            }
        )
