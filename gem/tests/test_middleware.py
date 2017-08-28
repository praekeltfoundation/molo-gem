import mock
from django.test import TestCase
from django.test.client import Client

from gem.middleware import GemMoloGoogleAnalyticsMiddleware
from gem.models import GemSettings
from molo.core.models import (
    Main,
    Languages,
    SiteLanguageRelation,
    SiteSettings
)
from molo.core.tests.base import MoloTestCaseMixin


class TestCustomGemMiddleware(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.client = Client()
        # Creates Main language
        self.mk_main()
        main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='en',
            is_active=True)
        # Creates a section under the index page
        self.english_section = self.mk_section(
            self.section_index, title='English section')

        # fake the site settings
        self.site_settings = mock.Mock()
        self.site_settings.local_ga_tracking_code = 'local_ga_tracking_code'

        # fake the gem settings
        self.gem_settings = mock.Mock()
        self.gem_settings.bbm_ga_account_subdomain = 'bbm'
        self.gem_settings.bbm_ga_tracking_code = "bbm_tracking_code"

        self.request = mock.Mock()
        self.request.site = self.site

    @mock.patch("gem.middleware.GemMoloGoogleAnalyticsMiddleware.submit_tracking")  # noqa
    @mock.patch("gem.models.GemSettings.for_site")
    def test_submit_to_additional_ga_account(self, mock_get_gem_settings,
                                             mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the URL contains the
        bbm_ga_account_subdomain, info should be sent to
        the additional GA account.
        '''
        mock_get_gem_settings.return_value = self.gem_settings

        self.request.get_host.return_value = (
            '{}.za.heyspringster.com'.format(
                self.gem_settings.bbm_ga_account_subdomain)
        )

        request = self.request
        response = self.client.get('/')

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            self.gem_settings.bbm_ga_tracking_code,
            request, response)

    @mock.patch("gem.middleware.GemMoloGoogleAnalyticsMiddleware.submit_tracking")  # noqa
    @mock.patch("gem.models.GemSettings.for_site")
    def test_submit_to_local_ga_account(self, mock_get_gem_settings,
                                        mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the URL does not contain the
        bbm_ga_account_subdomain, info should be sent to
        the local GA account, not the additional GA account.
        '''
        mock_get_gem_settings.return_value = self.gem_settings

        self.request.get_host.return_value = 'za.heyspringster.com'

        request = self.request
        response = self.client.get('/')

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            self.site_settings.local_ga_tracking_code,
            request, response)
