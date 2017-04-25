from django.test import TestCase
from molo.core.models import SiteLanguageRelation, Main, Languages
from molo.core.tests.base import MoloTestCaseMixin


class TestLanguageCodeSetting(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.bahasa = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
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
