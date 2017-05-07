# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv
from django.db import migrations
from molo.core.models import (
    SiteLanguage, Tag, TagIndexPage, PageTranslation)


def default_tags(apps, schema_editor):
    main_lang = SiteLanguage.objects.filter(
        is_active=True, is_main_language=True).first()
    tag_index = TagIndexPage.objects.first()
    reader = csv.DictReader(open('tags.csv'))
    child_languages = SiteLanguage.objects.filter(
        is_main_language=False).all()
    tags = {}

    if main_lang:
        for row in reader:
            key = row.pop('Tags')
            tags[key] = row
        add_tags(main_lang, child_languages, tag_index, tags)


def add_tags(main_lang, child_languages, tag_index, tags):
    for tag in tags:
        if tags.get(tag).get(main_lang.locale):
            main_tag = create_tag(
                tags.get(tag).get(main_lang.locale), tag_index)

        for child_lang in child_languages:
            if tags.get(tag).get(child_lang.locale):
                create_tag_translation(
                    main_tag, child_lang, tags.get(tag).get(child_lang.locale),
                    tag_index)


def create_tag(title, tag_index):
    if Tag.objects.filter(title=title).exists():
        return Tag.objects.filter(title=title).first()
    else:
        tag = Tag(title=title)
        tag_index.add_child(instance=tag)
        tag.save_revision().publish()
        return tag


def create_tag_translation(main_tag, language, translated_title, tag_index):
    translated_tag = create_tag(translated_title, tag_index)
    if translated_tag:
        language_relation = translated_tag.languages.first()
        language_relation.language = language
        language_relation.save()
        translated_tag.save_revision().publish()
        PageTranslation.objects.get_or_create(
            page=main_tag, translated_page=translated_tag)


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0013_gemsettings_moderator_name'),
    ]

    operations = [
        migrations.RunPython(default_tags),
    ]
