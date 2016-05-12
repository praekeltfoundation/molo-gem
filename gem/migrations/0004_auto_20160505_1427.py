# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0003_remove_gemuserprofile_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='gemuserprofile',
            name='security_question_1_answer',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='gemuserprofile',
            name='security_question_2_answer',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
