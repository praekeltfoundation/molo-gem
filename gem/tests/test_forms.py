from django.test import TestCase

from gem.forms import GemRegistrationForm
from molo.core.tests.base import MoloTestCaseMixin


class GemRegisterTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()

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
