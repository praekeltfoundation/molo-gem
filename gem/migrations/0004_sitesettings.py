# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
        ('gem', '0003_remove_gemuserprofile_date_of_birth'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('banned_keywords_and_patterns', models.TextField(help_text=b'Comments containing these words will not be allowed to be posted. separate words with a space.', null=True, verbose_name=b'Banned Keywords', blank=True)),
                ('comment_filters', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='wagtailcore.Page', null=True)),
                ('site', models.OneToOneField(editable=False, to='wagtailcore.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
