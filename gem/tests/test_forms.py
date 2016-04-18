from django.test import TestCase
from django.contrib.auth.models import User

from gem.forms import RegistrationForm


class RegisterTestCase(TestCase):

    def test_register_username_correct(self):
        form_data = {
            'username': 'Jeyabal@-1',
            'password': '1234',
            'gender': 'f',
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_register_username_incorrect(self):
        form_data = {
            'username': 'Jeyabal#',
            'password': '1234',
            'gender': 'f',
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_register_password_incorrect(self):
        form_data = {
            'username': 'Jeyabal@-1',
            'password': '12345',
            'gender': 'f',
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_username_exists(self):
        User.objects.create_user(
            'testing', 'testing@example.com', 'testing')
        form_data = {
            'username': 'testing',
            'password': '12345',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        [validation_error] = form.errors.as_data()['username']
        self.assertEqual(
            'Username already exists.', validation_error.message)

    def test_register_gender_required(self):
        form_data = {
            'username': 'Jeyabal@-1',
            'password': '1234',
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
