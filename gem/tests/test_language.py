from django.test import TestCase, Client
from molo.core.models import SiteLanguageRelation, Languages
from gem.tests.base import GemTestCaseMixin


class TestLanguageCodeSetting(TestCase, GemTestCaseMixin):

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
        language_setting = Languages.objects.get(
            site_id=self.main.get_site().pk)
        self.bahasa = SiteLanguageRelation.objects.create(
            language_setting=language_setting,
            locale='id',
            is_active=True)

    def test_language_code_setting(self):
        eng_section = self.mk_section(
            self.section_index, title='English Section')
        self.mk_section_translation(
            eng_section, self.bahasa, title='Bahasa Section')

        # First check for the default behavior
        response = self.client.get('/')
        self.assertContains(response, 'English Section')

        # Then override the LANGUAGE_CODE setting
        with self.settings(LANGUAGE_CODE='id'):
            response = self.client.get('/')
            self.assertContains(response, 'Bahasa Section')
