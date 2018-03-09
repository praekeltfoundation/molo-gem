from django.test import Client, TestCase

from molo.core.models import SiteLanguageRelation, Main, Languages
from molo.core.tests.base import MoloTestCaseMixin


class TestModels(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        main = Main.objects.all().first()
        language_setting = Languages.objects.create(
            site_id=main.get_site().pk)
        SiteLanguageRelation.objects.create(
            language_setting=language_setting,
            locale='en',
            is_active=True)

    def test_cache_control_decorator_for_wagtail_pages(self):
        client = Client()
        section = self.mk_section(self.section_index)
        response = client.get(section.url)
        self.assertEqual(response['Cache-Control'], 'public, max-age=600')
