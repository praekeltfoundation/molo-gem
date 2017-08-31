# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-08-31 15:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0018_remove_rendition_filter'),
        ('core', '0066_add_custom_media_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_hash', models.CharField(max_length=256, null=True)),
                ('image', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='image_info', to='wagtailimages.Image')),
            ],
        ),
    ]
