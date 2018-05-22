# coding=utf-8
import pytest

from copy import deepcopy

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from wagtail.wagtailcore.models import Site

from molo.core.models import SiteSettings
from molo.surveys.models import (
    MoloSurveyPage, MoloSurveyFormField, SurveysIndexPage)
from gem.models import GemSettings, GemUserProfile
from gem.tests.base import GemTestCaseMixin

from os.path import join

from bs4 import BeautifulSoup


@pytest.mark.django_db
class TestModels(TestCase, GemTestCaseMixin):

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')

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

        default_site = Site.objects.get(is_default_site=True)
        setting = GemSettings.for_site(default_site)
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
            )
            molo_survey_page2 = MoloSurveyPage(
                title='survey title',
                slug='another-survey-slug',
                homepage_introduction='Introduction to Test Survey ...',
                thank_you_text='Thank you for taking the Test Survey',
            )

            self.survey_index.add_child(instance=molo_survey_page)
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

            response = self.client.get('/')
            self.assertContains(
                response,
                self.banner_message)

            # test that the join banner only shows up once
            soup = BeautifulSoup(response.content, 'html.parser')
            self.assertEquals(
                soup.get_text().count(self.banner_message), 1)


class TestGemUserProfile(TestCase, GemTestCaseMixin):
    def test_security_questions_check(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        get_user_model().objects.create_user(
            username='user', email='user@example.com', password='pass')
        profile = GemUserProfile.objects.first()
        profile.set_security_question_1_answer('Answer 1')
        profile.set_security_question_2_answer('Answer 2')

        self.assertTrue(profile.check_security_question_1_answer('Answer 1'))
        self.assertTrue(profile.check_security_question_2_answer('Answer 2'))
