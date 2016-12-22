# coding=utf-8
import pytest
from django.test import TestCase, RequestFactory

from wagtail.wagtailcore.models import Site

from molo.core.models import SiteLanguage
from molo.core.tests.base import MoloTestCaseMixin

from gem.models import GemSettings


@pytest.mark.django_db
class TestModels(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.factory = RequestFactory()
        self.english = SiteLanguage.objects.create(locale='en')
        self.french = SiteLanguage.objects.create(locale='fr')
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

    def test_partner_credit(self):
        response = self.client.get('/')
        self.assertNotContains(response, 'Thank You')
        self.assertNotContains(response, 'https://www.google.co.za/')

        default_site = Site.objects.get(is_default_site=True)
        setting = GemSettings.objects.get(site=default_site)
        setting.show_partner_credit = True
        setting.partner_credit_description = "Thank You"
        setting.partner_credit_link = "https://www.google.co.za/"
        setting.save()

        response = self.client.get('/')
        self.assertContains(response, 'Thank You')
        self.assertContains(response, 'https://www.google.co.za/')
