# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from molo.profiles.models import UserProfilesSettings

from wagtail.wagtailcore.models import Site


def set_site_settings(apps, schema_editor):
    for site in Site.objects.all():
        settings = UserProfilesSettings.for_site(site)

        settings.show_security_question_fields = True
        settings.security_questions_required = True
        settings.num_security_questions = 2

        settings.activate_display_name = True
        settings.capture_display_name_on_reg = True

        settings.activate_gender = True
        settings.capture_gender_on_reg = True

        settings.save()


def unset_site_settings(apps, schema_editor):
    # We don't know what we should be unsetting the
    # site settings to here. It might be safest to
    # do a no-op.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0026_migrate_security_answers_off_gem_profile'),
        ('profiles', '0013_add_location_gender_education_level_fields'),
    ]

    operations = [
        migrations.RunPython(
            set_site_settings,
            unset_site_settings,
        ),
    ]
