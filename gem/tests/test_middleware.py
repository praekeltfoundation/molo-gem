from copy import deepcopy

from django.test import RequestFactory, TestCase
from django.test.client import Client

from gem.middleware import GemMoloGoogleAnalyticsMiddleware
from gem.models import GemSettings

from mock import patch
from os.path import join

from django.conf import settings
from django.contrib.auth.models import User
from molo.core.models import SiteSettings
from molo.profiles.models import UserProfilesSettings
from gem.tests.base import GemTestCaseMixin

from molo.core.models import (
    Tag, ArticlePageTags,
    SectionIndexPage, TagIndexPage, FooterIndexPage,
    FooterPage, SiteLanguageRelation, Site, Languages)


class TestChhaaJaaLoginMiddleware(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main2', slug='main2', path='00010002', url_path='/main2/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
        profile_settings = UserProfilesSettings.for_site(self.main.get_site())
        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')
        profile_settings.terms_conditions = self.yourmind
        profile_settings.save()

    def test_redirect_for_chhaajaa_login(self):
        # it should not redirect if the site layout base is not chhhaa jaa
        # even if user is not logged in and not requesting a login page
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

        template_settings = deepcopy(settings.TEMPLATES)
        template_settings[0]['DIRS'] = [
            join(settings.PROJECT_ROOT, 'templates', 'chhaajaa')
        ]
        with self.settings(
                TEMPLATES=template_settings, SITE_LAYOUT_BASE='chhaajaa'):
            # it should not redirect if templates chhaajaa
            # user user not loged in and requesting
            # login page
            response = self.client.get('/profiles/login/')
            self.assertEquals(response.status_code, 200)

            # it should redirect if user not logged in, chhaa jaa is template
            # and user not requesting a login page
            # it should keep the query string when redirecting
            response = self.client.get('/?testparam=test1212')
            self.assertEquals(response.status_code, 302)
            self.assertRedirects(
                response, '/profiles/login/?next=/%3Ftestparam%3Dtest1212')

            # it should not redirect if user logged in regardless
            # of template or path
            self.login()
            response = self.client.get('/')
            self.assertEquals(response.status_code, 200)


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
        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')

        self.article = self.mk_article(
            self.yourmind, title='article',
            subtitle='article with nav_tags',
            slug='article')
        self.article.save_revision().publish()
        self.article2 = self.mk_article(
            self.yourmind, title='article2',
            subtitle='artitle without nav_tags',
            slug='article2')
        self.article2.save_revision().publish()

        self.tag_index = TagIndexPage.objects.child_of(self.main).first()
        self.tag = Tag(title='Tag1')
        self.tag2 = Tag(title='Tag2')
        self.tag_index.add_child(instance=self.tag)
        self.tag.save_revision().publish()
        self.tag_index.add_child(instance=self.tag2)
        self.tag2.save_revision().publish()

        self.article.nav_tags.create(tag=self.tag)
        self.article.save_revision().publish()
        self.article.nav_tags.create(tag=self.tag2)
        self.article.save_revision().publish()
        # get footerpage
        self.footer_index = FooterIndexPage.objects.child_of(self.main).first()
        self.footer = FooterPage(title='Test Footer Page')
        self.footer_index.add_child(instance=self.footer)
        self.footer.save_revision().publish()
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
    def test_submit_to_local_ga_articlepage_title(
            self, mock_submit_tracking):
        """requests for article with tags should
        make a submit tracking with a cd6 value in the
        custom params containing all the article tags"""

        request = RequestFactory().get(
            '/sections-main1-1/{}/{}/'.format(
                self.yourmind.slug,
                self.article2.slug),
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
            {'cd5': self.article2.title,
                "cd3": 'Visitor',
                'cd1': "0000-000-01",
             })

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_translated_articlepage_title(
            self, mock_submit_tracking):
        """requests for article with tags should
        make a submit tracking with a cd6 value in the
        custom params containing all the article tags"""

        french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(Site.objects.first()),
            locale='fr',
            is_active=True)
        french_article = self.mk_article_translation(self.article2, french)
        french_article.title = "french translation of article"
        french_article.save_revision().publish()
        request = RequestFactory().get(
            '/sections-main1-1/{}/{}/'.format(
                self.yourmind.slug,
                french_article.slug),
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01"
        )
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = french.locale
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.process_response(
            request, self.response)
        # check that the tilte of the article in the main languge is used
        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code',
            request, self.response,
            {'cd5': self.article2.title,
                "cd3": 'Visitor',
                'cd1': "0000-000-01",
             })

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
        nav_tags = ArticlePageTags.objects.all()
        tags = [nav_tag.tag.title for nav_tag in nav_tags]
        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code',
            request, self.response,
            {'cd5': self.article.title,
                "cd3": 'Visitor', 'cd1': "0000-000-01",
                'cd6': "|".join(tags)}
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
            {'cd5': self.article2.title,
                "cd3": 'Visitor',
                'cd1': "0000-000-01"})

    @patch(submit_tracking_method)
    def test_submit_to_local_ga__footerpage__no_tags(
            self, mock_submit_tracking):
        '''request for articles with not tags
        should not have a cd6 value in
        the custom params'''

        request = RequestFactory().get(
            '/footers-main1-1/{}/'.format(
                self.footer.slug),
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
            {'cd5': self.footer.title,
                "cd3": 'Visitor', 'cd1': "0000-000-01"})
