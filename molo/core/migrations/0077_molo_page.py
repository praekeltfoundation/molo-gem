# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-22 10:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0040_page_draft_title'),
        ('core', '0076_create_cmssettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoloPage',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('wagtailcore.page',),
        ),
    ]