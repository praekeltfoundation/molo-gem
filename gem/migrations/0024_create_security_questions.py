# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management import call_command
from django.db import migrations


def create_security_questions(apps, schema_editor):
    call_command('create_security_questions_from_settings')


def delete_security_questions(apps, schema_editor):
    # It's difficult to know which questions we should be deleting
    # from the database. The questions may not be in the settings anymore.
    # It's much safer to just do a no-op here and there aren't really
    # any downsides. Questions can be modified in Wagtail admin.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0023_move_migrated_user_name_to_molo_profiles'),
        ('profiles', '0018_userprofile_admin_sites'),
    ]

    operations = [
        migrations.RunPython(
            create_security_questions,
            delete_security_questions,
        ),
    ]
