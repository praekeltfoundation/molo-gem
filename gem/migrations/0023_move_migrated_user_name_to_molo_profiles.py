# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def switch_to_using_profiles_migrated_username(apps, schema_editor):
    call_command('copy_migrated_username_to_profile')


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0018_userprofile_admin_sites'),
        ('gem', '0015_add_migrated_username'),
    ]

    operations = [
        migrations.RunPython(switch_to_using_profiles_migrated_username),
    ]
