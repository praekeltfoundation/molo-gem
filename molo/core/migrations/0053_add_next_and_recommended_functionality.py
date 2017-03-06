# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-30 06:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0032_add_bulk_delete_page_permission'),
        ('core', '0052_update_permissions_for_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticlePageRecommendedSections',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommended_articles', to='core.ArticlePage')),
                ('recommended_article', models.ForeignKey(blank=True, help_text='Recommended articles for this article', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='enable_next_section',
            field=models.BooleanField(default=False, help_text=b"Activate up next section underneath articles in this section will appear with the heading and subheading of that article. The text will say 'next' in order to make the user feel like it's fresh content.", verbose_name=b'Activate up next section underneath articles'),
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='enable_recommended_section',
            field=models.BooleanField(default=False, help_text=b"Underneath the area for 'next articles' recommended articles will appear, with the image + heading + subheading", verbose_name=b'Activate recommended section underneath articles'),
        ),
    ]
