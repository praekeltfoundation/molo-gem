from django.test import RequestFactory, TestCase, override_settings

from gem.context_processors import (
    compress_settings,
    detect_bbm,
    detect_freebasics,
)
from gem.models import OIDCSettings
from gem.tests.base import GemTestCaseMixin


class TestDetectBbm(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_returns_false_for_requests_without_bbm_cookie(self):
        request = self.request_factory.get('/')
        self.assertEqual(detect_bbm(request), {'is_via_bbm': False})

    def test_returns_true_for_requests_with_bbm_host(self):
        request = self.request_factory.get('/', HTTP_HOST='bbm.localhost:80')
        self.assertEqual(detect_bbm(request), {'is_via_bbm': True})

    def test_returns_true_for_requests_with_bbm_cookie(self):
        request = self.request_factory.get('/')
        request.COOKIES['bbm'] = 'true'
        self.assertEqual(detect_bbm(request), {'is_via_bbm': True})


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
                'LOGIN_URL': 'molo.profiles:auth_login',
                'VIEW_PROFILE_URL': u'/profiles/view/myprofile/',
                'EDIT_PROFILE_URL': u'/profiles/edit/myprofile/',
                'REGISTRATION_URL': u'/profiles/register/',
                'LOGOUT_URL': 'molo.profiles:auth_logout',
                'ENV': 'test_env',
                'STATIC_URL': 'test_static_url',
            }
        )

    @override_settings(ENV='test_env', STATIC_URL='test_static_url',
                       USE_OIDC_AUTHENTICATION='True')
    def test_returns_oidc_settings(self):
        """ Test OIDC settings for a site are used when getting the settings
        for a request
        """
        # Create request and add settings to site
        request = RequestFactory().get('/')
        site = self.main.get_site()
        site.oidcsettings = OIDCSettings.objects.create(
            oidc_rp_client_id='client_id',
            oidc_rp_client_secret='client_secret', oidc_rp_scopes='scopes',
            wagtail_redirect_url='http://example.url', site_id=site.id)
        request.site = site

        # Check settings
        settings = compress_settings(request)
        self.assertEqual(settings['LOGIN_URL'], 'molo.profiles:auth_login')
        self.assertEqual(
            settings['VIEW_PROFILE_URL'],
            u'/profile/edit/?theme=springster&redirect_uri='
            'http://example.url&client_id=client_id&language=en')
        self.assertEqual(settings['EDIT_PROFILE_URL'],
                         u'/profile/edit/?theme=springster&redirect_uri='
                         'http://example.url&client_id=client_id&language=en')
        self.assertEqual(
            settings['REGISTRATION_URL'],
            u'/registration/?theme=springster&hide=end-user&redirect_uri='
            'http://main1-1.localhost/oidc/authenticate/&client_id=client_id&'
            'language=en')
        self.assertEqual(settings['LOGOUT_URL'], 'molo.profiles:auth_logout')
        self.assertEqual(settings['ENV'], 'test_env')
        self.assertEqual(settings['STATIC_URL'], 'test_static_url')
