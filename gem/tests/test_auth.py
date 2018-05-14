from django.test import TestCase
from molo.core.tests.base import MoloTestCaseMixin
from gem.utils import provider_login_url


class TestOIDCAuthIntegration(TestCase, MoloTestCaseMixin):

    def test_login_url(self):
        login_url_with_oidc = provider_login_url(USE_OIDC_AUTHENTICATION=True)
        self.assertEquals(login_url_with_oidc, 'oidc_authentication_init')
        login_url_without_oidc = provider_login_url(
            USE_OIDC_AUTHENTICATION=False)
        self.assertEquals(login_url_without_oidc, 'molo.profiles:auth_login')
