from molo.core.tests.base import MoloTestCaseMixin
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class GemRegistrationViewTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_user_info_displaying_after_registration(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.user.profile.gender = 'female'
        self.user.profile.alias = 'useralias'
        self.user.profile.save()
        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('edit_my_profile'))
        print response
        self.assertContains(response, 'useralias')
        self.assertNotContains(response, '<option value="f">female</option>')
