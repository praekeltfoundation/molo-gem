from django.test import TestCase
from molo.core.tests.base import MoloTestCaseMixin
from gem.utils import provider_login_url, provider_registration_url


class TestOIDCAuthIntegration(TestCase, MoloTestCaseMixin):

    def test_login_url(self):
        login_url_with_oidc = provider_login_url(USE_OIDC_AUTHENTICATION=True)
        self.assertEquals(login_url_with_oidc, 'oidc_authentication_init')
        login_url_without_oidc = provider_login_url(
            USE_OIDC_AUTHENTICATION=False)
        self.assertEquals(login_url_without_oidc, 'molo.profiles:auth_login')

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
