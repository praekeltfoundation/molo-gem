# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User

from molo.core.tests.base import MoloTestCaseMixin

from molo.profiles.admin import ProfileUserAdmin, download_as_csv
from molo.profiles.models import UserProfile


class ModelsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.mk_main()

    def test_download_csv(self):
        profile = self.user.profile
        profile.alias = 'The Alias'
        profile.mobile_number = '+27784667723'
        profile.save()

        response = download_as_csv(ProfileUserAdmin(UserProfile, self.site),
                                   None,
                                   User.objects.all())
        date = str(self.user.date_joined.strftime("%Y-%m-%d %H:%M"))
        expected_output = ('Content-Type: text/csv\r\nContent-Disposition: '
                           'attachment;filename=export.csv\r\n\r\nusername,'
                           'email,first_name,last_name,is_staff,date_joined,'
                           'alias,mobile_number\r\ntester,tester@example.com,'
                           ',,False,' + date + ',The Alias,+27784667723\r\n')
        self.assertEquals(str(response), expected_output)
