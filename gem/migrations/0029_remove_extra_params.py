# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-30 09:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0028_oidc_settings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oidcsettings',
            name='extra_params',
        ),
    ]
