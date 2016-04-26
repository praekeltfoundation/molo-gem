# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0002_auto_20160425_1400'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gemuserprofile',
            name='date_of_birth',
        ),
    ]
