# coding=utf-8
import pytest

from copy import deepcopy

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from molo.core.models import (
    SiteSettings, Site, Languages, SiteLanguageRelation,
    SectionIndexPage)
from molo.forms.models import (
    MoloFormPage, MoloFormField, FormsIndexPage)
from gem.models import GemSettings
from gem.tests.base import GemTestCaseMixin
from gem.templatetags.gem_tags import content_is

from os.path import join

from bs4 import BeautifulSoup


@pytest.mark.django_db
class TestModels(TestCase, GemTestCaseMixin):

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
        self.form_index = FormsIndexPage.objects.child_of(
            self.main).first()
        self.section_index = SectionIndexPage.objects.child_of(
            self.main).first()
        self.site_settings = SiteSettings.for_site(self.main.get_site())
        self.site_settings.enable_tag_navigation = True
        self.site_settings.save()
        self.banner_message = ("Share your opinions and stories, " +
                               "take polls, win fun prizes.")
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(Site.objects.first()),
            locale='fr',
            is_active=True)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')

    def test_content_is(self):
        self.assertTrue(content_is(self.yourmind, 'Your mind in french'))
        self.assertTrue(content_is(self.yourmind, 'Your mind'))
        self.assertFalse(content_is(self.yourmind, 'Your body'))

    def test_partner_credit(self):
        response = self.client.get('/')
        self.assertNotContains(response, 'Thank You')
        self.assertNotContains(response, 'https://www.google.co.za/')

        setting = GemSettings.for_site(self.main.get_site())
        setting.show_partner_credit = True
        setting.partner_credit_description = "Thank You"
        setting.partner_credit_link = "https://www.google.co.za/"
        setting.save()

        response = self.client.get('/')
        self.assertContains(response, 'Thank You')
        self.assertContains(response, 'https://www.google.co.za/')

    def test_show_join_banner(self):
        template_settings = deepcopy(settings.TEMPLATES)
        template_settings[0]['DIRS'] = [
            join(settings.PROJECT_ROOT, 'templates', 'springster')
        ]

        with self.settings(TEMPLATES=template_settings):
            molo_form_page = MoloFormPage(
                title='from title',
                slug='form-slug',
                homepage_introduction='Introduction to Test Form ...',
                thank_you_text='Thank you for taking the Test Form',
                allow_anonymous_submissions=False
            )
            self.form_index.add_child(instance=molo_form_page)

            molo_form_page2 = MoloFormPage(
                title='form title',
                slug='another-form-slug',
                homepage_introduction='Introduction to Test Form ...',
                thank_you_text='Thank you for taking the Test Form',
                allow_anonymous_submissions=True
            )

            self.form_index.add_child(instance=molo_form_page2)

            MoloFormField.objects.create(
                page=molo_form_page,
                sort_order=1,
                label='Your favourite animal',
                field_type='singleline',
                required=True
            )
            MoloFormField.objects.create(
                page=molo_form_page2,
                sort_order=1,
                label='Your birthday month',
                field_type='singleline',
                required=True
            )
            molo_form_page.save_revision().publish()
            molo_form_page2.save_revision().publish()
            setting = GemSettings.for_site(self.main.get_site())
            self.assertFalse(setting.show_join_banner)
            response = self.client.get('%s?next=%s' % (
                reverse('molo.profiles:auth_logout'),
                reverse('molo.profiles:auth_login')))
            response = self.client.get('/')
            self.assertNotContains(
                response,
                self.banner_message)
            setting.show_join_banner = True
            setting.save()

            self.assertTrue(GemSettings.for_site(
                self.main.get_site()).show_join_banner)
            self.assertTrue(SiteSettings.for_site(
                self.main.get_site()).enable_tag_navigation)
            response = self.client.get('/')
            self.assertContains(
                response,
                self.banner_message)

            # test that the join banner only shows up once
            soup = BeautifulSoup(response.content, 'html.parser')
            self.assertEqual(
                soup.get_text().count(self.banner_message), 1)
