# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-10 13:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0031_add_view_yourwords_entry_to_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gemuserprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='GemUserProfile',
        ),
    ]
