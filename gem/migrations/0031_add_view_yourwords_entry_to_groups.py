# flake8: noqa: E128
# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-24 12:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations
from django.core.management.sql import emit_post_migrate_signal


def add_view_yourwords_entry_to_groups(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    emit_post_migrate_signal(2, False, db_alias)

    Group = apps.get_model('auth.Group')
    Permission = apps.get_model('auth.Permission')

    view_yourwords_entry = Permission.objects.get(
        codename='can_view_yourwords_entry')
    group_names = ('product_admin', 'data_admin', 'data_viewer',
                   'content_editor', 'content_admin')
    for group_name in group_names:
        group = Group.objects.get(name=group_name)
        group.permissions.add(view_yourwords_entry)


surveys_installed = 'molo.yourwords' in settings.INSTALLED_APPS and \
'molo.polls' in settings.INSTALLED_APPS and 'molo.surveys' in settings.INSTALLED_APPS

if surveys_installed:
    operations = [
        migrations.RunPython(add_view_yourwords_entry_to_groups),
    ]
    dependencies = [
        ('gem', '0030_create_groups_and_permissions'),
        ('core', '0002_add_can_view_response_reaction_question_permission'),
        ('yourwords', '0008_add_can_view_entry_permission'),
    ]
else:
    operations = []
    dependencies = [
        ('gem', '0030_create_groups_and_permissions'),
        ('core', '0002_add_can_view_response_reaction_question_permission'),
    ]


class Migration(migrations.Migration):
    dependencies = dependencies
    operations = operations