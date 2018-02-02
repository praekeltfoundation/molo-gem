# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management import call_command
from django.db import migrations


def migrate_security_answers(apps, schema_editor):
    call_command('migrate_security_answers_to_molo_profiles')


def unmigrate_security_answers(apps, schema_editor):
    # We probably shouldn't delete everybody's security answers
    # as part of the reverse migration. The questions might not
    # be in the settings anymore.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0025_move_gender_to_molo_profiles'),
        ('profiles', '0018_userprofile_admin_sites'),
    ]

    operations = [
        migrations.RunPython(
            migrate_security_answers,
            unmigrate_security_answers,
        ),
    ]
