from django.test import TestCase

from gem.forms import GemRegistrationForm
from gem.tests.base import GemTestCaseMixin


class GemRegisterTestCase(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')

    def test_registration_form_removes_unwanted_fields(self):
        form_data = {
            'email': 'personal_data@domain.com',
            'location': '123 Street, City, Country',
            'mobile_number': '+27710123456',
        }
        form = GemRegistrationForm(data=form_data)
        form.is_valid()
        self.assertEqual(form.cleaned_data['email'], None)
        self.assertEqual(form.cleaned_data['location'], None)
        self.assertEqual(form.cleaned_data['mobile_number'], None)

    def test_register_gender_required(self):
        form_data = {
            'username': 'Jeyabal@-1',
            'password': '1234',
            'security_question_1_answer': 'dog',
            'security_question_2_answer': 'cat'
        }
        form = GemRegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_register_security_question_1_answer_required(self):
        form_data = {
            'username': 'tester',
            'password': 'tester',
            'gender': 'm',
            'security_question_2_answer': 'dog'
        }
        form = GemRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_register_security_question_2_answer_required(self):
        form_data = {
            'username': 'tester',
            'password': 'tester',
            'gender': 'm',
            'security_question_1_answer': 'dog'
        }
        form = GemRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
