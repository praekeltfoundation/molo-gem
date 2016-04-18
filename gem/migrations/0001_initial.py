# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='GemUserProfile',
            fields=[
                ('user', models.OneToOneField(related_name='gem_profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('gender', models.CharField(blank=True, max_length=1, null=True, choices=[(b'f', b'female'), (b'm', b'male'), (b't', b'trans')])),
            ],
        ),
    ]
