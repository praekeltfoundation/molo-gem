# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-19 11:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0010_banned_names_with_offensive_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gemsettings',
            name='banned_names_with_offensive_language',
            field=models.TextField(blank=True, help_text=b'Banned names with offensive language, separated by a line a break. Use only lowercase letters for keywords.', null=True, verbose_name=b'Banned Names With Offensive Language'),
        ),
    ]
