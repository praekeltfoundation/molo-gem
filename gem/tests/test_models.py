# coding=utf-8
import pytest

from copy import deepcopy

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings

from molo.core.models import SiteSettings
from molo.surveys.models import (
    MoloSurveyPage, MoloSurveyFormField, SurveysIndexPage)
from gem.models import GemSettings
from gem.tests.base import GemTestCaseMixin

from os.path import join

from bs4 import BeautifulSoup


@pytest.mark.django_db
class TestModels(TestCase, GemTestCaseMixin):

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
        self.survey_index = SurveysIndexPage.objects.child_of(
            self.main).first()
        self.site_settings = SiteSettings.for_site(self.main.get_site())
        self.site_settings.enable_tag_navigation = True
        self.site_settings.save()
        self.banner_message = ("Share your opinions and stories, " +
                               "take polls, win fun prizes.")

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
            molo_survey_page = MoloSurveyPage(
                title='survey title',
                slug='survey-slug',
                homepage_introduction='Introduction to Test Survey ...',
                thank_you_text='Thank you for taking the Test Survey',
                allow_anonymous_submissions=False
            )
            self.survey_index.add_child(instance=molo_survey_page)

            molo_survey_page2 = MoloSurveyPage(
                title='survey title',
                slug='another-survey-slug',
                homepage_introduction='Introduction to Test Survey ...',
                thank_you_text='Thank you for taking the Test Survey',
                allow_anonymous_submissions=True
            )

            self.survey_index.add_child(instance=molo_survey_page2)

            MoloSurveyFormField.objects.create(
                page=molo_survey_page,
                sort_order=1,
                label='Your favourite animal',
                field_type='singleline',
                required=True
            )
            MoloSurveyFormField.objects.create(
                page=molo_survey_page2,
                sort_order=1,
                label='Your birthday month',
                field_type='singleline',
                required=True
            )
            molo_survey_page.save_revision().publish()
            molo_survey_page2.save_revision().publish()
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
            self.assertEquals(
                soup.get_text().count(self.banner_message), 1)
