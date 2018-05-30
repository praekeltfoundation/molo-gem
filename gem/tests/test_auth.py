from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from django.conf import settings
from django.conf.urls import url, include
from django.http import HttpRequest
from gem.backends import GirlEffectOIDCBackend, _update_user_from_claims
from gem.middleware import CustomSessionRefresh
from gem.models import OIDCSettings
from gem.tests.base import GemTestCaseMixin
from gem.views import (
    RedirectWithQueryStringView, CustomAuthenticationCallbackView,
    CustomAuthenticationRequestView)
from wagtail.wagtailcore import urls as wagtail_urls
from django.core.urlresolvers import reverse


urlpatterns = [
    url(r'^admin/login/', RedirectWithQueryStringView.as_view(
        pattern_name="oidc_authentication_init")),
    url(r'^oidc/', include('mozilla_django_oidc.urls')),
    url(r'', include(wagtail_urls)),
]


@override_settings(
    ROOT_URLCONF='gem.tests.test_auth',
    USE_OIDC_AUTHENTICATION=True,
    OIDC_AUTHENTICATE_CLASS="gem.views.CustomAuthenticationRequestView",
    OIDC_CALLBACK_CLASS="gem.views.CustomAuthenticationCallbackView")
class TestOIDCAuthIntegration(TestCase, GemTestCaseMixin):

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

    def test_auth_backend_filter_users_by_claims(self):
        claims = {}
        user = get_user_model().objects.create(
            username='this1234is5678uuid', password='pass')
        claims["sub"] = user.username
        backend = GirlEffectOIDCBackend()
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEqual(returned_user[0].pk, user.pk)

        # it should return none if user does not DoesNotExist
        claims["sub"] = 'thisisnotavaliduuid'
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEquals(returned_user.count(), 0)

    def test_auth_backend_update_user_from_claims(self):
        roles = ['example role', ]
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com'}
        user = get_user_model().objects.create(
            username='testuser', password='password')
        self.assertFalse(user.is_staff)
        _update_user_from_claims(user, claims)
        user = get_user_model().objects.get(id=user.pk)
        self.assertTrue(user.is_superuser)
        self.assertEquals(user.first_name, 'testgivenname')
        self.assertEquals(user.last_name, 'testfamilyname')
        self.assertEquals(user.email, 'test@email.com')

    @override_settings(USE_OIDC_AUTHENTICATION=True)
    def test_admin_url_changes_when_use_oidc_set_true(self):
        self.assertTrue(settings.USE_OIDC_AUTHENTICATION)
        OIDCSettings.objects.create(
            site=self.main.get_site(), oidc_rp_client_secret='secret',
            oidc_rp_client_id='id',
            wagtail_redirect_url='https://redirecit.com')
        response = self.client.get('/admin/login/')
        self.assertEquals(response['location'], '/oidc/authenticate/')

    def test_auth_backend_authenticate(self):
        site = self.main.get_site()
        request = HttpRequest()
        request.site = site
        backend = GirlEffectOIDCBackend()

        # it should change the client id and client secret if successful
        self.assertEquals(backend.OIDC_RP_CLIENT_SECRET, 'unused')
        self.assertEquals(backend.OIDC_RP_CLIENT_ID, 'unused')
        OIDCSettings.objects.create(
            site=site, oidc_rp_client_secret='secret', oidc_rp_client_id='id',
            wagtail_redirect_url='https://redirecit.com')
        backend = GirlEffectOIDCBackend()
        backend.authenticate(request=request)
        self.assertEquals(backend.OIDC_RP_CLIENT_SECRET, 'secret')
        self.assertEquals(backend.OIDC_RP_CLIENT_ID, 'id')

    def test_auth_callback_view_success_url(self):
        site = self.main.get_site()
        request = HttpRequest()
        request.site = site
        view = CustomAuthenticationCallbackView()
        view.request = request
        # it should return the correct redirect url if successful
        settings = OIDCSettings.objects.create(
            site=site, oidc_rp_client_secret='secret', oidc_rp_client_id='id',
            wagtail_redirect_url='https://redirecit.com')
        self.assertEquals(view.success_url, settings.wagtail_redirect_url)

    def test_auth_request_get_view(self):
        # it should throw an error if site has no OIDC settings
        site = self.main.get_site()
        request = HttpRequest()
        request.site = site
        view = CustomAuthenticationRequestView()
        self.assertRaises(
            RuntimeError, view.get, request)

        # it should change the redirect_url and client ID if successful
        OIDCSettings.objects.create(
            site=site, oidc_rp_client_secret='secret', oidc_rp_client_id='id',
            wagtail_redirect_url='http://main1.localhost:8000')
        response = self.client.get(reverse('oidc_authentication_callback'))
        self.assertEquals(response['location'], '/')

    def test_auth_middleware(self):
        # it should throw an error if site has no OIDC settings
        site = self.main.get_site()
        request = HttpRequest()
        request.site = site
        middleware = CustomSessionRefresh()
        self.assertRaises(
            RuntimeError, middleware.process_request, request)
