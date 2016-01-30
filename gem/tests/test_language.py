from django.test import TestCase
from molo.core.models import LanguagePage
from molo.core.tests.base import MoloTestCaseMixin


class TestLanguageCodeSetting(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()

        self.bahasa = LanguagePage(
            title='Bahasa',
            code='id',
            slug='bahasa')
        self.main.add_child(instance=self.bahasa)
        self.bahasa.save_revision().publish()

    def test_language_code_setting(self):
        self.mk_section(
            self.english, title='English Section')
        self.mk_section(
            self.bahasa, title='Bahasa Section')

        # First check for the default behavior
        response = self.client.get('/')
        self.assertContains(response, 'English Section')

        # Then override the LANGUAGE_CODE setting
        with self.settings(LANGUAGE_CODE='id'):
            response = self.client.get('/')
            self.assertContains(response, 'Bahasa Section')
