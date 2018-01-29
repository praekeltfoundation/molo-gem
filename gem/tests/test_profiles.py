from molo.core.tests.base import MoloTestCaseMixin
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class GemRegistrationViewTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()

    def test_user_info_displaying_after_registration(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('edit_my_profile'))
        self.assertNotContains(response, 'useralias')
        self.assertContains(response, '<option value="f">female</option>')
        self.user.profile.gender = 'f'
        self.user.profile.alias = 'useralias'
        self.user.profile.save()
        response = self.client.get(reverse('edit_my_profile'))
        self.assertContains(response, 'useralias')
        self.assertNotContains(response, '<option value="f">female</option>')
