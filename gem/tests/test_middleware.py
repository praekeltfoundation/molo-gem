from mock import patch

from django.conf import settings
from django.test.client import Client
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language_from_request

from molo.core.models import SiteSettings
from molo.core.models import (
    Tag, ArticlePageTags,
    SectionIndexPage, TagIndexPage, FooterIndexPage,
    FooterPage, SiteLanguageRelation, Site, Languages)

from gem.tests.base import GemTestCaseMixin
from gem.middleware import GemMoloGoogleAnalyticsMiddleware


class TestCustomGemMiddleware(TestCase, GemTestCaseMixin):
    submit_tracking_method = (
        "gem.middleware.GemMoloGoogleAnalyticsMiddleware.submit_tracking"
    )

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
        self.response = self.client.get('/')
        self.site_settings = SiteSettings.for_site(self.main.get_site())
        self.site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        self.site_settings.save()
        site = Site.objects.first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(site),
            locale='en',
            is_active=True)

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.get(slug='sections'),
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

        self.tag_index = TagIndexPage.objects.get(slug='tags')
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
        self.footer_index = FooterIndexPage.objects.get(slug='footer-pages')
        self.footer = FooterPage(title='Test Footer Page')
        self.footer_index.add_child(instance=self.footer)
        self.footer.save_revision().publish()

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_account(self, mock_submit_tracking):
        request = RequestFactory().get(
            '/',
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01",)

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
        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.process_response(
            request, self.response)
        mock_submit_tracking.assert_not_called()

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_valid_info(self, mock_submit_tracking):
        request = RequestFactory().get(
            '/search/?q=whatislife',
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01")
        site = request._wagtail_site
        site_settings = SiteSettings.for_site(site)
        site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        site_settings.save()

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
            '/sections/{}/{}/'.format(
                self.yourmind.slug,
                self.article2.slug),
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01"
        )
        site = request._wagtail_site
        site_settings = SiteSettings.for_site(site)
        site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        site_settings.save()
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
            '/sections/{}/{}/'.format(
                self.yourmind.slug,
                french_article.slug),
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01"
        )
        site = request._wagtail_site
        site_settings = SiteSettings.for_site(site)
        site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        site_settings.save()
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = french.locale

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
            '/sections/{}/{}/'.format(
                self.yourmind.slug,
                self.article.slug),
            HTTP_HOST='localhost',
            HTTP_X_DCMGUID="0000-000-01"
        )
        site = request._wagtail_site
        site_settings = SiteSettings.for_site(site)
        site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        site_settings.save()
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
            '/sections/{}/{}/'.format(
                self.yourmind.slug,
                self.article2.slug),
            HTTP_X_DCMGUID="0000-000-01"
        )
        site = request._wagtail_site
        site_settings = SiteSettings.for_site(site)
        site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        site_settings.save()

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
            '/footer-pages/{}/'.format(
                self.footer.slug),
            HTTP_X_DCMGUID="0000-000-01"
        )
        site = request._wagtail_site
        site_settings = SiteSettings.for_site(site)
        site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        site_settings.save()
        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.process_response(
            request, self.response)
        # a normal response should activate GA tracking
        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code',
            request, self.response,
            {'cd5': self.footer.title,
                "cd3": 'Visitor', 'cd1': "0000-000-01"})


class TestGemLocaleMiddleware(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
        self.site_settings = SiteSettings.for_site(self.main.get_site())

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')

        self.article = self.mk_article(self.yourmind, title='article')
        self.article.save_revision().publish()

        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='fr',
            is_active=True)

        self.fr_article = self.mk_article_translation(
            self.article, self.french)

        self.fr_yourmind = self.mk_section_translation(
            self.yourmind, self.french)

    def test_non_default_language_existing_session(self):
        request = RequestFactory().get('/locale/en/')
        self.assertEqual(get_language_from_request(request), 'en')

        request = RequestFactory()
        request.session = {'django_langauge': 'en'}

        fr_url = self.fr_article.url
        request = request.get(fr_url)
        self.assertEqual(get_language_from_request(request), 'en')

    def test_non_default_language_new_session(self):
        self.client.get("/locale/fr/")
        fr_url = self.fr_article.url
        res = self.client.get(fr_url)
        self.assertTrue('lang="fr"' in str(res.content))

    def test_default_language(self):
        res = self.client.get('/')
        self.assertTrue('lang="en"' in str(res.content))


class TestAdminSiteAdminMiddleware(TestCase, GemTestCaseMixin):
    def get_admin_perms(self):
        wagtailadmin_content_type, created = ContentType.objects.get_or_create(
            app_label='wagtailadmin',
            model='admin'
        )
        admin_permission, created = Permission.objects.get_or_create(
            content_type=wagtailadmin_content_type,
            codename='access_admin',
            name='Can access Wagtail admin'
        )
        return admin_permission

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.site = self.main.get_site()
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
        self.site_settings = SiteSettings.for_site(self.site)

        self.user = User.objects.create_user(
            username='tester',
            is_staff=True,
            email='tester@example.com',
            password='tester')
        self.user.profile.admin_sites.add(self.site)
        self.user.user_permissions.add(self.get_admin_perms())

    def test_access_admin_no_site_admin_permissions_superuser(self):
        user, created = User.objects.get_or_create(
            username='testusermidware',
            is_staff=True, password='1234', is_superuser=True
        )
        user.user_permissions.add(self.get_admin_perms())
        self.client.force_login(user)
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 200)

    def test_access_admin_no_site_admin_permissions(self):
        user, created = User.objects.get_or_create(
            username='testusermidware',
            is_staff=True, password='1234'
        )
        user.user_permissions.add(self.get_admin_perms())
        self.client.force_login(user)
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, '/')

        site = Site.objects.create(
            hostname='dummysite.com',
            root_page=self.main
        )
        user.profile.admin_sites.add(site)
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, site.hostname + '/admin/')

    def test_access_admin(self):
        self.client.force_login(self.user)
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 200)
