from django.test import TestCase

from gem.forms import GemRegistrationForm


class GemRegisterTestCase(TestCase):
    def test_register_gender_required(self):
        form_data = {
            'username': 'Jeyabal@-1',
            'password': '1234',
        }
        form = GemRegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
