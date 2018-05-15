from django.test import TestCase
from django.contrib.auth import get_user_model
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import Main, Languages, SiteLanguageRelation
from gem.utils import (
    provider_login_url, provider_registration_url, provider_logout_url)
from gem.backends import GirlEffectOIDCBackend


class TestOIDCAuthIntegration(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

    def test_login_url(self):
        login_url_with_oidc = provider_login_url(USE_OIDC_AUTHENTICATION=True)
        self.assertEquals(login_url_with_oidc, 'oidc_authentication_init')
        login_url_without_oidc = provider_login_url(
            USE_OIDC_AUTHENTICATION=False)
        self.assertEquals(login_url_without_oidc, 'molo.profiles:auth_login')

    def test_logout_url(self):
        login_url_with_oidc = provider_logout_url(USE_OIDC_AUTHENTICATION=True)
        self.assertEquals(login_url_with_oidc, 'oidc_logout')
        login_url_without_oidc = provider_logout_url(
            USE_OIDC_AUTHENTICATION=False)
        self.assertEquals(login_url_without_oidc, 'molo.profiles:auth_logout')

    def test_registration_url(self):
        registration_url_with_oidc = provider_registration_url(
            USE_OIDC_AUTHENTICATION=True)
        self.assertEquals(
            registration_url_with_oidc,
            '/registration/?theme=springster&hide=end-user&redirect_url=')
        registration_url_without_oidc = provider_registration_url(
            USE_OIDC_AUTHENTICATION=False)
        self.assertEquals(
            registration_url_without_oidc, 'molo.profiles:user_register')

    def test_filter_users_by_claims(self):
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
