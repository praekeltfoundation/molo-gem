from django.contrib.auth.models import User
from datetime import date
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
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from django.core.urlresolvers import reverse

urlpatterns = [
    url(r'^admin/login/', RedirectWithQueryStringView.as_view(
        pattern_name="oidc_authentication_init")),
    url(r'^oidc/', include('mozilla_django_oidc.urls')),
    url(r'^admin/', include(wagtailadmin_urls)),
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

    def test_create_user_from_claims(self):
        claims = {'sub': 'e2556752-16d0-445a-8850-f190e860dea4',
                  'preferred_username': 'testuser'}
        backend = GirlEffectOIDCBackend()
        returned_user = backend.create_user(claims)
        self.assertEqual(returned_user.username, 'testuser')
        self.assertEqual(returned_user.profile.auth_service_uuid,
                         'e2556752-16d0-445a-8850-f190e860dea4')

    def test_auth_backend_filter_users_by_claims(self):
        claims = {'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        user = get_user_model().objects.create(
            username='test_user', password='pass')
        user.profile.auth_service_uuid = claims['sub']
        user.profile.save()
        backend = GirlEffectOIDCBackend()
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEqual(returned_user[0].pk, user.pk)

        # it should return none if user does not DoesNotExist
        claims['sub'] = 'e5135879-16d0-445a-8850-f190e860dea4'
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEquals(returned_user.count(), 0)

    def test_filter_users_by_claims_migrated_user(self):
        claims = {'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        user = get_user_model().objects.create(
            username='test_user', password='pass')
        claims['migration_information'] = {'user_id': user.id}
        backend = GirlEffectOIDCBackend()
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEqual(returned_user[0].pk, user.pk)

        # it should return none if user does not DoesNotExist
        claims['sub'] = 'e5135879-16d0-445a-8850-f190e860dea4'
        claims['migration_information'] = {'user_id': -2}
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEquals(returned_user.count(), 0)

    def test_add_superuser_role_from_claims(self):
        roles = ['Product Tech Admin', ]
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4',
            'gender': 'Female',
            'birthdate': '1988-05-22'}
        user = get_user_model().objects.create(
            username='testuser', password='password')
        self.assertFalse(user.is_staff)
        _update_user_from_claims(user, claims)
        user = get_user_model().objects.get(id=user.pk)
        self.assertTrue(user.is_superuser)
        self.assertEquals(user.first_name, 'testgivenname')
        self.assertEquals(user.last_name, 'testfamilyname')
        self.assertEquals(user.email, 'test@email.com')
        self.assertEquals(str(user.profile.auth_service_uuid),
                          'e2556752-16d0-445a-8850-f190e860dea4')
        self.assertEquals(user.profile.gender, 'f')
        self.assertEquals(user.profile.date_of_birth, date(1988, 5, 22))

    def test_add_user_role_from_claims(self):
        roles = ['Data Admin', ]
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        user = get_user_model().objects.create(
            username='testuser', password='password')
        _update_user_from_claims(user, claims)
        user = get_user_model().objects.get(id=user.pk)
        self.assertFalse(user.is_superuser)
        self.assertEquals(user.groups.all().count(), 1)
        self.assertEquals(user.groups.first().name, 'Data Admin')

    def test_removing_user_role(self):
        roles = ['Product Tech Admin', 'Data Admin', 'Content Admin']
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        user = get_user_model().objects.create(
            username='testuser', password='password')
        _update_user_from_claims(user, claims)
        user = get_user_model().objects.get(id=user.pk)
        self.assertTrue(user.is_superuser)
        self.assertEquals(user.groups.all().count(), 2)
        self.assertEquals(user.groups.first().name, 'Data Admin')
        self.assertEquals(user.groups.last().name, 'Content Admin')

        roles = ['Data Admin', 'Content Admin']
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        _update_user_from_claims(user, claims)
        self.assertFalse(user.is_superuser)
        self.assertEquals(user.groups.all().count(), 2)
        self.assertEquals(user.groups.first().name, 'Data Admin')
        self.assertEquals(user.groups.last().name, 'Content Admin')

        roles = ['Content Admin']
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        _update_user_from_claims(user, claims)
        self.assertFalse(user.is_superuser)
        self.assertEquals(user.groups.all().count(), 1)
        self.assertEquals(user.groups.first().name, 'Content Admin')

    def test_update_user_from_claims_creates_profile(self):
        user = get_user_model().objects.create(
            username='testuser', password='password')
        user.profile.delete()
        user = get_user_model().objects.get(id=user.pk)
        roles = ['Product Tech Admin', ]
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        _update_user_from_claims(user, claims)
        user = get_user_model().objects.get(id=user.pk)
        self.assertTrue(user.is_superuser)
        self.assertEquals(user.first_name, 'testgivenname')
        self.assertEquals(user.last_name, 'testfamilyname')
        self.assertEquals(user.email, 'test@email.com')
        self.assertEquals(str(user.profile.auth_service_uuid),
                          'e2556752-16d0-445a-8850-f190e860dea4')

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

    @override_settings(LOGOUT_URL='oidc_logout')
    def test_admin_logout_button_when_oidc_is_true(self):
        # check that users need to login
        response = self.client.get('/admin/')
        self.assertEquals(response['location'], "/admin/login/?next=/admin/")
        # test that the admin logs the user in
        User.objects.create_superuser(
            'testadmin', 'testadmin@example.org', 'testadmin')
        self.client.login(username='testadmin', password='testadmin')
        response = self.client.get('/admin/')
        self.assertContains(response, "Welcome to the GEM Wagtail CMS")
        # test that the correct logout button is in in the template
        self.assertContains(response, "oidc/logout")
