from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from molo.core.models import (
    Languages,
    Main,
    SiteLanguageRelation,
    SiteSettings
)
from molo.core.tests.base import MoloTestCaseMixin
from molo.surveys.models import (
    MoloSurveyFormField,
    MoloSurveyPage,
    SurveysIndexPage,
)

User = get_user_model()


class TestSurveyViews(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.client = Client()
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)

        self.section = self.mk_section(self.section_index, title='section')
        self.article = self.mk_article(self.section, title='article')

        # Create surveys index pages
        self.surveys_index = SurveysIndexPage.objects.child_of(
            self.main).first()

        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)
        self.french2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='fr',
            is_active=True)

        self.mk_main2(title='main3', slug='main3', path="00010003")
        self.client2 = Client(HTTP_HOST=self.main2.get_site().hostname)
        settings = SiteSettings.for_site(self.main.get_site())
        settings.enable_tag_navigation = True
        settings.save()

    def create_molo_survey_page(self, parent, **kwargs):
        molo_survey_page = MoloSurveyPage(
            title='Test Survey', slug='test-survey',
            introduction='Introduction to Test Survey ...',
            homepage_introduction='Shorter homepage introduction',
            thank_you_text='Thank you for taking the Test Survey',
            submit_text='survey submission text',
            **kwargs
        )

        parent.add_child(instance=molo_survey_page)
        molo_survey_page.save_revision().publish()
        molo_survey_form_field = MoloSurveyFormField.objects.create(
            page=molo_survey_page,
            sort_order=1,
            label='Your favourite animal',
            field_type='singleline',
            required=True
        )
        return molo_survey_page, molo_survey_form_field

    def test_translated_survey_not_showing_when_unpublished(self):
        self.user = self.login()
        molo_survey_page, molo_survey_form_field = \
            self.create_molo_survey_page(parent=self.surveys_index)

        self.client.post(reverse(
            'add_translation', args=[molo_survey_page.id, 'fr']))
        translated_survey = MoloSurveyPage.objects.get(
            slug='french-translation-of-test-survey')
        translated_survey.save_revision().publish()
        translated_survey.refresh_from_db()

        response = self.client.get("/")
        self.assertContains(response, 'Test Survey')
        self.assertNotContains(response, 'French translation of Test Survey')

        response = self.client.get('/locale/fr/')
        response = self.client.get('/')
        self.assertNotContains(response, '<h1>Test Survey')
        self.assertContains(response, 'French translation of Test Survey')

        translated_survey.unpublish()
        response = self.client.get('/locale/fr/')
        response = self.client.get('/')
        self.assertNotContains(response, 'French translation of Test Survey')
