from datetime import date

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User

from gem.forms import GemRegistrationForm


class GemRegistrationViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_view(self):
        response = self.client.get(reverse('user_register'))
        self.assertTrue(isinstance(response.context['form'],
                        GemRegistrationForm))

    def test_register_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse('user_register'), {
        })
        self.assertFormError(
            response, 'form', 'username', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'password', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'gender', ['This field is required.'])


class RegistrationDone(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')

    def test_date_of_birth(self):
        response = self.client.post(reverse(
            'registration_done'), {
            'date_of_birth': '2000-01-01',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.gem_profile.date_of_birth, date(2000, 1, 1))
