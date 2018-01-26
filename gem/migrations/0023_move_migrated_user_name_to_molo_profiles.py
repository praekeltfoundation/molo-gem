# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from gem.models import GemProfile


def switch_to_using_profiles_migrated_username(
        switch_to_using_profiles_migrated_username):
    '''
    Copies the migrated username from gem_profiles and adds it to molo profile
    '''
    for gem_profile in GemProfile.objects.all():
        if hasattr(gem_profile.user, 'profile'):
            gem_profile.user.profile.migrated_username = \
                gem_profile.migrated_username


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0018_userprofile_admin_sites'),
    ]

    operations = [
        migrations.RunPython(switch_to_using_profiles_migrated_username),
    ]
