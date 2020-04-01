import pytest

from datetime import date
from django.core import mail
from django.urls import reverse
from django.conf import settings
from django.http import HttpRequest
from django.conf.urls import url, include
from django.core.exceptions import FieldError
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import Group, Permission

from allauth.socialaccount.models import SocialLogin, SocialAccount
from wagtail.core import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

from gem.models import OIDCSettings, Invite
from gem.tests.base import GemTestCaseMixin
from gem.middleware import CustomSessionRefresh
from gem.adapter import StaffUserSocialAdapter, StaffUserAdapter
from gem.backends import GirlEffectOIDCBackend, _update_user_from_claims
from gem.views import (
    RedirectWithQueryStringView, CustomAuthenticationCallbackView,
    CustomAuthenticationRequestView)


urlpatterns = [
    url(r'^admin/login/', RedirectWithQueryStringView.as_view(
        pattern_name="oidc_authentication_init")),
    url(r'^oidc/', include('mozilla_django_oidc.urls')),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'', include(wagtail_urls)),

]


class GirlEffectOIDCBackendMock(GirlEffectOIDCBackend):

    def get_userinfo(self, access_token, id_token, payload):
        return {
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4',
            'preferred_username': 'testuser'
        }


@override_settings(
    ROOT_URLCONF='gem.tests.test_auth',
    USE_OIDC_AUTHENTICATION='true',
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
        self.assertTrue(returned_user.is_active)
        self.assertEqual(returned_user.username, 'testuser')
        self.assertEqual(returned_user.profile.auth_service_uuid,
                         'e2556752-16d0-445a-8850-f190e860dea4')

    def test_get_or_create_user_from_claims(self):
        id_token = 'id_token'
        access_token = 'access_token'
        claims = {
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4',
            'preferred_username': 'testuser'
        }

        backend = GirlEffectOIDCBackendMock()
        returned_user = backend.get_or_create_user(
            access_token, id_token, claims)

        self.assertEqual(returned_user.username, 'testuser')
        self.assertEqual(
            returned_user.profile.auth_service_uuid,
            'e2556752-16d0-445a-8850-f190e860dea4'
        )

    def test_create_user_from_claims_with_errors(self):
        user2 = get_user_model().objects.create(
            username='john', password='password')
        user2.profile.auth_service_uuid = \
            'e2556552-16d0-445a-0850-f190e860dea6'
        user2.profile.save()
        claims = {'sub': 'e2556752-16d0-445a-8850-f190e860dea4',
                  'preferred_username': 'john'}
        backend = GirlEffectOIDCBackend()
        with pytest.raises(FieldError):
            backend.create_user(claims)

    def test_create_user_from_claims_with_clashes(self):
        user2 = get_user_model().objects.create(
            username='john', password='password')
        claims = {'sub': 'e2556752-16d0-445a-8850-f190e860dea4',
                  'preferred_username': 'john'}
        backend = GirlEffectOIDCBackend()
        returned_user = backend.create_user(claims)
        self.assertEqual(returned_user.username, 'john')
        self.assertEqual(returned_user.is_active, True)
        self.assertEqual(returned_user.profile.auth_service_uuid,
                         'e2556752-16d0-445a-8850-f190e860dea4')
        user2.refresh_from_db()
        self.assertEqual(user2.username, '3_john')
        self.assertEqual(user2.is_active, True)

    def test_create_user_from_claims_with_clashing_username(self):
        get_user_model().objects.create(
            username='3_john', password='password')
        get_user_model().objects.create(
            username='john', password='password')
        claims = {
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4',
            'preferred_username': 'john'
        }
        backend = GirlEffectOIDCBackend()
        with pytest.raises(FieldError):
            backend.create_user(claims)

    def test_auth_backend_filter_users_by_claims(self):
        claims = {'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        user = get_user_model().objects.create(
            username='test_user', password='pass')
        user.profile.auth_service_uuid = claims['sub']
        user.profile.save()
        backend = GirlEffectOIDCBackend()
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEqual(returned_user[0].pk, user.pk)
        self.assertTrue(returned_user[0].is_active)

        # it should return none if user does not DoesNotExist
        claims['sub'] = 'e5135879-16d0-445a-8850-f190e860dea4'
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEqual(returned_user.count(), 0)

    def test_filter_users_by_claims_migrated_user(self):
        claims = {'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        user = get_user_model().objects.create(
            username='test_user', password='pass')
        claims['migration_information'] = {'user_id': user.id}
        backend = GirlEffectOIDCBackend()
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEqual(returned_user[0].pk, user.pk)
        self.assertTrue(returned_user[0].is_active)

        # it should return none if user does not DoesNotExist
        claims['sub'] = 'e5135879-16d0-445a-8850-f190e860dea4'
        claims['migration_information'] = {'user_id': -2}
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEqual(returned_user.count(), 0)

    def test_add_superuser_role_from_claims(self):
        roles = ['product_tech_admin', ]
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
        self.assertTrue(user.is_active)
        _update_user_from_claims(user, claims)
        user = get_user_model().objects.get(id=user.pk)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.first_name, 'testgivenname')
        self.assertEqual(user.last_name, 'testfamilyname')
        self.assertEqual(user.email, 'test@email.com')
        self.assertEqual(
            str(user.profile.auth_service_uuid),
            'e2556752-16d0-445a-8850-f190e860dea4')
        self.assertEqual(user.profile.gender, 'f')
        self.assertEqual(user.profile.date_of_birth, date(1988, 5, 22))

    def test_add_user_role_from_claims(self):
        roles = ['data_admin', ]
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
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.groups.all().count(), 1)
        self.assertEqual(user.groups.first().name, 'data_admin')

    def test_alias_set_to_username(self):
        roles = ['data_admin', ]
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        user = get_user_model().objects.create(
            username='testuser', password='password')
        # check that alias is initially empty
        self.assertEqual(user.profile.alias, None)
        _update_user_from_claims(user, claims)
        # test that empty alias is set to username
        self.assertEqual(user.profile.alias, user.username)
        # test that alias will only change on update from claims
        user.profile.alias = "an_alias"
        self.assertNotEqual(user.profile.alias, user.username)
        # test that non-empty alias is also set to username
        _update_user_from_claims(user, claims)
        self.assertEqual(user.profile.alias, user.username)
        self.assertTrue(user.is_active)

    def test_removing_user_role(self):
        roles = ['product_tech_admin', 'data_admin', 'content_admin']
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
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.groups.all().count(), 2)
        self.assertEqual(user.groups.first().name, 'data_admin')
        self.assertEqual(user.groups.last().name, 'content_admin')

        roles = ['data_admin', 'content_admin']
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        _update_user_from_claims(user, claims)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.groups.all().count(), 2)
        self.assertEqual(user.groups.first().name, 'data_admin')
        self.assertEqual(user.groups.last().name, 'content_admin')

        roles = ['content_admin']
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        _update_user_from_claims(user, claims)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.groups.all().count(), 1)
        self.assertEqual(user.groups.first().name, 'content_admin')

        roles = []
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        _update_user_from_claims(user, claims)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.groups.all().count(), 0)

    def test_update_user_from_claims_creates_profile(self):
        user = get_user_model().objects.create(
            username='testuser', password='password')
        user.profile.delete()
        user = get_user_model().objects.get(id=user.pk)
        roles = ['product_tech_admin', ]
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        _update_user_from_claims(user, claims)
        user = get_user_model().objects.get(id=user.pk)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(user.first_name, 'testgivenname')
        self.assertEqual(user.last_name, 'testfamilyname')
        self.assertEqual(user.email, 'test@email.com')
        self.assertEqual(
            str(user.profile.auth_service_uuid),
            'e2556752-16d0-445a-8850-f190e860dea4')

    def test_update_user_from_claims_with_errors(self):
        user = get_user_model().objects.create(
            username='testuser', password='password')
        user2 = get_user_model().objects.create(
            username='john', password='password')
        user2.profile.auth_service_uuid = \
            'e2556552-16d0-445a-0850-f190e860dea6'
        user2.profile.save()
        claims = {
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'preferred_username': 'john',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        with pytest.raises(FieldError):
            _update_user_from_claims(user, claims)

    def test_update_user_from_claims_max_length_errors(self):
        user = get_user_model().objects.create(
            username='john', password='password')
        user.profile.auth_service_uuid = \
            'e2556552-16d0-445a-0850-f190e860dea6'
        user.profile.save()
        claims = {
            'given_name': 'a'*31,
            'family_name': 'testfamilyname',
            'preferred_username': 'john',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        with pytest.raises(FieldError):
            _update_user_from_claims(user, claims)

    def test_update_user_from_claims_updates_username(self):
        user = get_user_model().objects.create(
            username='testuser', password='password')
        user2 = get_user_model().objects.create(
            username='john', password='password')
        claims = {
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'preferred_username': 'john',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
        _update_user_from_claims(user, claims)
        user = get_user_model().objects.get(id=user.pk)
        user2 = get_user_model().objects.get(id=user2.pk)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(user.first_name, 'testgivenname')
        self.assertEqual(user.last_name, 'testfamilyname')
        self.assertEqual(user.email, 'test@email.com')
        self.assertEqual(user2.username, '3_john')
        self.assertEqual(user.username, 'john')
        self.assertEqual(
            str(user.profile.auth_service_uuid),
            'e2556752-16d0-445a-8850-f190e860dea4')

    @override_settings(USE_OIDC_AUTHENTICATION='true')
    def test_admin_url_changes_when_use_oidc_set_true(self):
        self.assertTrue(settings.USE_OIDC_AUTHENTICATION)
        OIDCSettings.objects.create(
            site=self.main.get_site(), oidc_rp_client_secret='secret',
            oidc_rp_client_id='id',
            wagtail_redirect_url='https://redirecit.com')
        response = self.client.get('/admin/login/')
        self.assertEqual(response['location'], '/oidc/authenticate/')

    def test_auth_backend_authenticate(self):
        site = self.main.get_site()
        request = HttpRequest()
        request.site = site
        backend = GirlEffectOIDCBackend()

        # it should change the client id and client secret if successful
        self.assertEqual(backend.OIDC_RP_CLIENT_SECRET, 'unused')
        self.assertEqual(backend.OIDC_RP_CLIENT_ID, 'unused')
        OIDCSettings.objects.create(
            site=site, oidc_rp_client_secret='secret', oidc_rp_client_id='id',
            wagtail_redirect_url='https://redirecit.com')
        backend = GirlEffectOIDCBackend()
        backend.authenticate(request=request)
        self.assertEqual(backend.OIDC_RP_CLIENT_SECRET, 'secret')
        self.assertEqual(backend.OIDC_RP_CLIENT_ID, 'id')

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
        self.assertEqual(view.success_url, settings.wagtail_redirect_url)

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
        self.assertEqual(response['location'], '/')

    def test_auth_middleware(self):
        # it should throw an error if site has no OIDC settings
        site = self.main.get_site()
        request = HttpRequest()
        request.site = site
        middleware = CustomSessionRefresh()
        self.assertRaises(
            RuntimeError, middleware.process_request, request)

    # @override_settings(LOGOUT_URL='oidc_logout')
    # def test_admin_logout_button_when_oidc_is_true(self):
    #     OIDCSettings.objects.create(
    #         site=self.main.get_site(), oidc_rp_client_secret='secret',
    #         oidc_rp_client_id='id',
    #         wagtail_redirect_url='http://main1.localhost:8000')
    #     # check that users need to login
    #     response = self.client.get('/admin/')
    #     self.assertEqual(response['location'], "/admin/login/?next=/admin/")
    #     # test that the admin logs the user in
    #     User.objects.create_superuser(
    #         'testadmin', 'testadmin@example.org', 'testadmin')
    #     self.client.login(username='testadmin', password='testadmin')
    #     response = self.client.get('/admin/')
    #     self.assertContains(response, "Welcome to the GEM Wagtail CMS")
    #     # test that the correct logout button is in in the template
    #     self.assertContains(response, "oidc/logout")


class TestAllAuth(GemTestCaseMixin, TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='superuser', email='superuser@email.com', password='pass')
        self.main = self.mk_main(
            title='main1', slug='main1',
            path='00010002', url_path='/main1/'
        )
        self.site = self.main.get_site()

    @override_settings(ENABLE_ALL_AUTH=True)
    def test_admin_login_view(self):
        res = self.client.get(reverse('wagtailadmin_login'))
        self.assertEqual(res.status_code, 200)
        # toDo: find a better way to handle conditional urls patterns,
        #  because django only loads them once on server instantiation
        # self.assertTemplateUsed(res, 'wagtailadmin/social_login.html')

    @override_settings(ENABLE_ALL_AUTH=True)
    def test_admin_views_authed_user(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse('wagtailadmin_login'))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(settings.ENABLE_ALL_AUTH, True)
        self.assertEqual(res.url, '/admin/')

        res = self.client.get(res.url)
        self.assertEqual(res.status_code, 200)

    @override_settings(ENABLE_ALL_AUTH=True)
    def test_invite_create_view(self):
        req = RequestFactory()
        req.site = self.site
        req.user = self.user

        self.client.force_login(self.user)
        url = '/admin/gem/invite/create/'
        data = {
            'email': 'testinvite@test.com'
        }
        res = self.client.post(url, data=data, request=req)

        subject = '{}: Admin site invitation'.format('localhost [default]')
        self.assertEqual(res.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertEqual(mail.outbox[0].from_email, 'no-reply@gehosting.org')

        self.assertTrue(
            Invite.objects.filter(user=self.user).exists())

    @override_settings(ENABLE_ALL_AUTH=True)
    def test_invite_edit_view(self):
        data = {
            'email': 'testinvite@test.com'
        }
        req = RequestFactory()
        req.site = self.site
        req.user = self.user

        invite = Invite.objects.create(
            email=data['email'], user=self.user, site=self.site)
        self.client.force_login(self.user)

        url = '/admin/gem/invite/edit/{}/'.format(invite.pk)
        res = self.client.post(url, request=req)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, data['email'])
        res = self.client.post(url, data=data, request=req)

        self.assertEqual(res.status_code, 302)
        # Note: email sent on creation of invite object by signal
        # testing that a duplicate email was not sent on update
        self.assertEqual(len(mail.outbox), 1)

    def test_staff_social_adaptor(self):
        """
        Test a front-end user getting an invite to admin site
        """
        request = RequestFactory()
        request.site = self.site

        adaptor = StaffUserSocialAdapter(request=request)
        user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='pass'
        )
        sociallogin = SocialLogin(user=user)
        group = Group.objects.filter().first()
        perm = Permission.objects.filter().first()

        self.assertFalse(adaptor.is_open_for_signup(request, sociallogin))

        invite = Invite.objects.create(
            email=user.email, user=self.user, site=self.site)
        invite.groups.add(group)
        invite.permissions.add(perm)

        self.assertFalse(user.groups.all().exists())
        self.assertFalse(user.user_permissions.all().exists())

        adaptor.add_perms(user)
        invite.refresh_from_db()
        self.assertTrue(invite.is_accepted)
        self.assertTrue(user.groups.all().exists())
        self.assertTrue(user.user_permissions.all().exists())

        user.delete()
        invite.delete()

    def test_staff_social_adaptor_new_user(self):
        """
        Test a new user getting an invite to admin site
        """
        request = RequestFactory()
        request.site = self.site

        adaptor = StaffUserSocialAdapter(request=request)
        user = get_user_model()(
            username='testuser',
            email='testuser@email.com',
            password='pass'
        )
        sociallogin = SocialLogin(user=user)
        group = Group.objects.filter().first()
        perm = Permission.objects.filter().first()

        self.assertFalse(user.pk)
        self.assertFalse(adaptor.is_open_for_signup(request, sociallogin))

        invite = Invite.objects.create(
            email=user.email, user=self.user, site=self.site)
        invite.groups.add(group)
        invite.permissions.add(perm)

        adaptor.add_perms(user)
        invite.refresh_from_db()
        self.assertTrue(invite.is_accepted)
        self.assertTrue(user.groups.all().exists())
        self.assertTrue(user.user_permissions.all().exists())

        user.delete()
        invite.delete()

    def test_staff_social_adaptor_staff(self):
        """
        Test a regular staff login
        """
        request = RequestFactory()
        request.site = self.site
        adaptor = StaffUserSocialAdapter(request=request)
        user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='pass',
            is_staff=True,
        )
        sociallogin = SocialLogin(user=user)
        group = Group.objects.filter().first()
        perm = Permission.objects.filter().first()

        user.groups.add(group)
        user.user_permissions.add(perm)
        self.assertFalse(adaptor.is_open_for_signup(request, sociallogin))

        adaptor.add_perms(user)
        self.assertTrue(user.groups.all().exists())
        self.assertTrue(user.user_permissions.all().exists())

        user.delete()

    def test_staff_social_adaptor_superuser(self):
        """
        Test a superuser login
        """
        request = RequestFactory()
        adaptor = StaffUserSocialAdapter(request=request)
        user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            is_superuser=True,
            password='pass'
        )
        request.site = self.site
        sociallogin = SocialLogin(user=user)
        self.assertFalse(adaptor.is_open_for_signup(request, sociallogin))
        self.assertFalse(user.groups.all().exists())
        self.assertFalse(user.user_permissions.all().exists())

        adaptor.add_perms(user)
        self.assertFalse(user.groups.all().exists())
        self.assertFalse(user.user_permissions.all().exists())

        user.delete()

    def test_staff_user_adapter_new_user(self):
        adaptor = StaffUserAdapter()
        user = get_user_model()(
            username='testuser',
            email='testuser@email.com',
            password='pass'
        )
        request = RequestFactory().post(
            data={
                'username': user.username,
                'password': user.password
            }, path=reverse('wagtailadmin_login'))
        request.site = self.site
        self.assertFalse(adaptor.is_open_for_signup(request, None))

    def test_staff_user_adapter_front_end_user(self):
        adaptor = StaffUserAdapter()
        user = get_user_model().objects.create(
            username='testuser',
            email='testuser@email.com',
            password='pass'
        )
        request = RequestFactory().post(
            data={
                'username': user.username,
                'password': user.password
            }, path=reverse('wagtailadmin_login'))
        request.site = self.site
        self.assertFalse(adaptor.is_open_for_signup(request, None))

    def test_staff_user_adapter_staff_user(self):
        adaptor = StaffUserAdapter()
        user = get_user_model().objects.create(
            username='testuser',
            email='testuser@email.com',
            is_staff=True,
            password='pass'
        )
        request = RequestFactory().post(
            data={
                'username': user.username,
                'password': user.password
            }, path=reverse('wagtailadmin_login'))
        request.site = self.site
        self.assertFalse(adaptor.is_open_for_signup(request, None))

    def test_staff_user_adapter_staff_user_perms(self):
        adaptor = StaffUserAdapter()
        group = Group.objects.filter().first()
        perm = Permission.objects.filter().first()
        user = get_user_model().objects.create(
            username='testuser',
            email='testuser@email.com',
            is_staff=True,
            password='pass'
        )
        user.groups.add(group)
        user.user_permissions.add(perm)
        request = RequestFactory().post(
            data={
                'username': user.username,
                'password': user.password
            }, path=reverse('wagtailadmin_login'))
        request.site = self.site
        self.assertFalse(adaptor.is_open_for_signup(request, None))

    def test_user_delete(self):
        user = get_user_model().objects.create(
            username='testuser',
            email='testuser@email.com',
            is_staff=True,
            password='pass'
        )
        SocialAccount.objects.create(
            user=user, provider='google', uid='1')
        user.delete()
        self.assertFalse(
            SocialAccount.objects.filter(user=user)
        )


class TestAllAuthDisabled(GemTestCaseMixin, TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='superuser', email='superuser@email.com', password='pass')
        self.main = self.mk_main(
            title='main1', slug='main1',
            path='00010002', url_path='/main1/'
        )
        self.site = self.main.get_site()

    @override_settings(ENABLE_ALL_AUTH=False)
    def test_login_all_auth_disabled(self):
        res = self.client.get(reverse('wagtailadmin_login'))
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, '<span class="fa fa-google"></span>Google')
