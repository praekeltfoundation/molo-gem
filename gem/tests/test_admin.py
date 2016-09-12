# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User

from molo.core.tests.base import MoloTestCaseMixin

from molo.profiles.models import UserProfile
from gem.admin import GemUserAdmin, download_as_csv_gem


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
        date = str(self.user.date_joined.strftime("%Y-%m-%d %H:%M"))
        gem_profile = self.user.gem_profile
        gem_profile.gender = 'f'
        gem_profile.date_of_birth = date
        gem_profile.save()
        response = download_as_csv_gem(GemUserAdmin(UserProfile, self.site),
                                       None,
                                       User.objects.all())
        expected_output = (
            'Content-Type: text/csv\r\nContent-Disposition: attachment;filen'
            'ame=export.csv\r\n\r\nusername,email,first_name,last_name,is_sta'
            'ff,date_joined,alias,mobile_number,date_of_birth,gender\r\nte'
            'ster,tester@example.com,,,False,' + date + ',The Alias,+277'
            '84667723,,f\r\n')
        self.assertEquals(str(response), expected_output)

    def test_download_csv_no_gem_profile(self):
        gem_profile = self.user.gem_profile
        gem_profile.delete()
        response = download_as_csv_gem(GemUserAdmin(UserProfile, self.site),
                                       None,
                                       User.objects.all())
        expected_output = (
            'Content-Type: text/csv\r\nContent-Disposition: attachment;file'
            'name=export.csv\r\n\r\nusername,email,first_name,last_name,is_st'
            'aff,date_joined,alias,mobile_number,date_of_birth,gender\r\n')
        self.assertEquals(str(response), expected_output)
