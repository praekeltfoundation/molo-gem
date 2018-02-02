from molo.core.tests.base import MoloTestCaseMixin
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class TestProfileInformationDisplay(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()

    def test_gender_displays_correctly(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client.login(username='tester', password='tester')
        self.user.profile.gender = 'f'
        self.user.profile.save()
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, '<span>female</span>')
        self.user.profile.gender = 'None'
        self.user.profile.save()
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, '<span>Not set</span>')
