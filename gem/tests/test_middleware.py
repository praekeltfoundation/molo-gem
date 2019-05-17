from django.test import RequestFactory, TestCase
from django.test.client import Client

from gem.middleware import GemMoloGoogleAnalyticsMiddleware
from gem.models import GemSettings

from mock import patch
from django.contrib.auth.models import User
from molo.core.models import(
    SiteSettings, SectionIndexPage,
    SiteLanguageRelation, Languages)
from gem.tests.base import GemTestCaseMixin


class TestCustomGemMiddleware(TestCase, GemTestCaseMixin):

    submit_tracking_method = (
        "gem.middleware.GemMoloGoogleAnalyticsMiddleware.submit_tracking"
    )

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

        self.site_settings = SiteSettings.for_site(self.main.get_site())
        self.site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        self.site_settings.save()

        GemSettings.objects.create(
            site_id=self.main.get_site().id,
            bbm_ga_account_subdomain='bbm',
            bbm_ga_tracking_code='bbm_tracking_code',
        )
        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='es',
            is_active=True)

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')

        self.sp_yourmind = self.mk_section_translation(
            self.yourmind, self.spanish, title='Your mind in spanish')

        self.article = self.mk_article(
            self.yourmind, title='article2',
            subtitle='article 2 subtitle',
            slug='article2')
        self.article.tags.add("tag1")
        self.article.save_revision().publish()
        self.article.tags.add("tag2")
        self.article.save_revision().publish()

        # make a translated version of the articles
        self.sp_article = self.mk_article_translation(
            self.article, self.spanish,
            title=self.article.title + ' in spanish',
            subtitle=self.article.subtitle + ' in spanish',
        )
        self.sp_article.tags.add("sp_tag1")
        self.sp_article.save_revision().publish()
        self.sp_article.tags.add("sp_tag2")
        self.sp_article.save_revision().publish()

        # article with no tags
        self.article2 = self.mk_article(
            self.yourmind, title='article',
            subtitle='article 1 subtitle',
            slug='article')
        self.article2.save_revision().publish()

        self.response = self.client.get('/')

    @patch(submit_tracking_method)
    def test_submit_to_additional_ga_account(self, mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the URL contains the
        bbm_ga_account_subdomain, info should be sent to
        the additional GA account.
        '''

        request = RequestFactory().get(
            '/',
            HTTP_HOST='bbm.localhost',
            HTTP_X_DCMGUID="0000-000-01"
        )
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            'bbm_tracking_code',
            request, self.response, {"cd3": 'Visitor', 'cd1': "0000-000-01"})

    @patch(submit_tracking_method)
    def test_submit_to_bbm_analytics_if_cookie_set(self, mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the BBM cookie is set, info
        should be sent to the additional GA account.
        '''

        request = RequestFactory().get(
            '/',
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01"
        )
        request.COOKIES['bbm'] = 'true'
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            'bbm_tracking_code',
            request, self.response, {"cd3": 'Visitor', 'cd1': "0000-000-01"})

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_account(self, mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the URL does not contain the
        bbm_ga_account_subdomain, info should be sent to
        the local GA account, not the additional GA account.
        '''

        request = RequestFactory().get(
            '/',
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01",)
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code',
            request,
            self.response,
            {"cd3": 'Visitor', 'cd1': "0000-000-01"}
        )

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_account__custom_params(self,
                                                       mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the URL does not contain the
        bbm_ga_account_subdomain, info should be sent to
        the local GA account, not the additional GA account.
        '''
        # create a user with a profile
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client.login(username='tester', password='tester')
        self.user.profile.gender = 'f'

        self.user.profile.save()

        request = RequestFactory().get(
            '/',
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01",
        )
        request.site = self.main.get_site()
        request.user = self.user
        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)
        cd1 = middleware.get_visitor_id(request)
        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code',
            request,
            self.response,
            {"cd3": 'Registered', 'cd2': self.user.profile.uuid, 'cd1': cd1})

    @patch(submit_tracking_method)
    def test_submit_to_local_ga__ignored_info(self, mock_submit_tracking):
        '''
        Paths in GOOGLE_ANALYTICS_IGNORE_PATH should not invoke
        a call to google analytics tracking
        '''

        request = RequestFactory().get(
            '/profiles/password-reset/',
            HTTP_HOST='localhost',
        )
        request.site = self.main.get_site()
        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.process_response(
            request, self.response)
        # test that the tracking method is not called with senstive info
        mock_submit_tracking.assert_not_called()

        request = RequestFactory().get(
            '/profiles/reset-success/',
            HTTP_HOST='localhost',
        )
        middleware.process_response(
            request, self.response)
        mock_submit_tracking.assert_not_called()

        request = RequestFactory().get(
            '/profiles/reset-password/',
            HTTP_HOST='localhost',
        )
        middleware.process_response(
            request, self.response)
        mock_submit_tracking.assert_not_called()

    @patch(submit_tracking_method)
    def test_submit_to_local_ga__sensitive_info(self, mock_submit_tracking):
        '''
        Paths with sensitive information should not
        be tracked on google analytics
        '''

        request = RequestFactory().get(
            '/search/?q=user%40user.com',
            HTTP_HOST='localhost',
        )
        request.site = self.main.get_site()
        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.process_response(
            request, self.response)
        mock_submit_tracking.assert_not_called()

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_valid_info(self, mock_submit_tracking):

        request = RequestFactory().get(
            '/search/?q=whatislife',
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01"
        )
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.process_response(
            request, self.response)
        # a normal response should activate GA tracking
        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code',
            request, self.response,
            {"cd3": 'Visitor', 'cd1': "0000-000-01"})

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_articlepage_with_tags(
            self, mock_submit_tracking):
        """requests for article with tags should
        make a submit tracking with a cd6 value in the
        custom params containing all the article tags"""

        request = RequestFactory().get(
            '/sections-main1-1/{}/{}/'.format(
                self.yourmind.slug,
                self.article.slug),
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01"
        )
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.process_response(
            request, self.response)
        # a normal response should activate GA tracking
        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code',
            request, self.response,
            {"cd3": 'Visitor', 'cd1': "0000-000-01",
             'cd6': '|'.join(self.article.tags_list())}
        )

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_articlepage_no_tags(
            self, mock_submit_tracking):
        '''request for articles with not tags
        should not have a cd6 value in
        the custom params'''

        request = RequestFactory().get(
            '/sections-main1-1/{}/{}/'.format(
                self.yourmind.slug,
                self.article2.slug),
            HTTP_X_DCMGUID="0000-000-01"
        )

        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.process_response(
            request, self.response)
        # a normal response should activate GA tracking
        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code',
            request, self.response,
            {"cd3": 'Visitor', 'cd1': "0000-000-01"})

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_articlepage_translated_with_tags(
            self, mock_submit_tracking):
        '''test that the tags are shown in the language that the
        user accessed the page in'''

        request = RequestFactory().get(
            '/sections-main1-1/{}/{}/'.format(
                self.yourmind.slug,
                self.sp_article.slug),
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01"
        )
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.process_response(
            request, self.response)
        # a normal response should activate GA tracking
        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code',
            request, self.response,
            {"cd3": 'Visitor', 'cd1': "0000-000-01", 'cd6': "sp_tag1|sp_tag2"})
