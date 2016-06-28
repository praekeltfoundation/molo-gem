from django.test import TestCase
from molo.core.models import SiteLanguage
from molo.core.tests.base import MoloTestCaseMixin


class TestLanguageCodeSetting(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        # Creates Main language
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
        # Creates translation Language
        self.bahasa = SiteLanguage.objects.create(
            locale='id',
        )

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
