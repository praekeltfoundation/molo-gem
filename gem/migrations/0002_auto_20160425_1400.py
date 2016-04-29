# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gemuserprofile',
            name='date_of_birth',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='gemuserprofile',
            name='gender',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'f', 'female'), (b'm', 'male'), (b'-', "don't want to answer")]),
        ),
    ]
