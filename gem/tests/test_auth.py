from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from django.conf import settings
from django.conf.urls import url, include
from gem.backends import GirlEffectOIDCBackend, _update_user_from_claims
from gem.tests.base import GemTestCaseMixin
from gem.views import RedirectWithQueryStringView
from wagtail.wagtailcore import urls as wagtail_urls


urlpatterns = [
    url(r'^admin/login/', RedirectWithQueryStringView.as_view(
        pattern_name="oidc_authentication_init")),
    url(r'', include(wagtail_urls)),
]


@override_settings(
    ROOT_URLCONF='gem.tests.test_auth')
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

    def test_filter_users_by_claims(self):
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

    def test_update_user_from_claims(self):
        roles = ['example role', ]
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'e2556752-16d0-445a-8850-f190e860dea4'}
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

    def test_update_user_from_claims_creates_profile(self):
        user = get_user_model().objects.create(
            username='testuser', password='password')
        user.profile.delete()
        user = get_user_model().objects.get(id=user.pk)
        roles = ['example role', ]
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
        response = self.client.get('/admin/login/', follow=True)
        self.assertEquals(response.status_code, 410)
