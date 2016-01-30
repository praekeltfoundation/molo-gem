from django.test import TestCase
from molo.core.models import LanguagePage, Main
from django.contrib.contenttypes.models import ContentType
from wagtail.wagtailcore.models import Site, Page


class TestLanguageCodeSetting(TestCase):

    def setUp(self):
        # Create page content type
        page_content_type, created = ContentType.objects.get_or_create(
            model='page',
            app_label='wagtailcore'
        )

        # Create root page
        Page.objects.create(
            title="Root",
            slug='root',
            content_type=page_content_type,
            path='0001',
            depth=1,
            numchild=1,
            url_path='/',
        )

        main_content_type, created = ContentType.objects.get_or_create(
            model='main', app_label='core')

        # Create a new homepage
        main = Main.objects.create(
            title="Main",
            slug='main',
            content_type=main_content_type,
            path='00010001',
            depth=2,
            numchild=0,
            url_path='/home/',
        )
        main.save_revision().publish()

        self.english = LanguagePage(
            title='English',
            code='en',
            slug='english')
        main.add_child(instance=self.english)
        self.english.save_revision().publish()

        self.bahasa = LanguagePage(
            title='Bahasa',
            code='id',
            slug='bahasa')
        main.add_child(instance=self.bahasa)
        self.bahasa.save_revision().publish()

        # Create a site with the new homepage set as the root
        Site.objects.all().delete()
        Site.objects.create(
            hostname='localhost', root_page=main, is_default_site=True)

    def test_language_code_setting(self):

        # First check for the default behavior
        response = self.client.get('/')
        self.assertRedirects(response, '/locale/en/')

        # Then override the LANGUAGE_CODE setting
        with self.settings(LANGUAGE_CODE='id'):
            response = self.client.get('/')
            self.assertRedirects(response, '/locale/id/')
