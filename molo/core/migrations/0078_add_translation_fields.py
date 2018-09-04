# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-03 12:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20180831_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.SiteLanguage'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='translated_pages',
            field=models.ManyToManyField(blank=True, null=True, related_name='_articlepage_translated_pages_+', to='core.ArticlePage'),
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.SiteLanguage'),
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='translated_pages',
            field=models.ManyToManyField(blank=True, null=True, related_name='_sectionpage_translated_pages_+', to='core.SectionPage'),
        ),
        migrations.AddField(
            model_name='tag',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.SiteLanguage'),
        ),
        migrations.AddField(
            model_name='tag',
            name='translated_pages',
            field=models.ManyToManyField(blank=True, null=True, related_name='_tag_translated_pages_+', to='core.Tag'),
        ),
    ]
