# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from molo.core.models import (
    SiteLanguage, Tag, TagIndexPage, Main, PageTranslation)


def add_default_tags(apps, schema_editor):
    main_lang = SiteLanguage.objects.filter(
        is_active=True, is_main_language=True).first()
    tag_index = TagIndexPage.objects.first()
    tags_list = [
        [{'title': 'health', 'locale': 'en'}, {'title': 'الصحة', 'locale': 'ar'}, {'title': 'স্বাস্থ্য', 'locale': 'bn'}],
        [{'title': 'periods', 'locale': 'en'}, {'title': 'الدورة', 'locale': 'ar'}, {'title': 'পিরিয়ড', 'locale': 'bn'}]
    ]
    for tag in tags_list:
        for t in tag:
            if main_lang.locale == t['locale']:
                main_tag = create_tag(t['title'], tag_index)
        for t in tag:
            child_lang = SiteLanguage.objects.filter(
                locale=t['locale'], is_main_language=False).first()
            if child_lang:
                create_tag_translation(
                    main_tag, child_lang, t['title'], tag_index)


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
        migrations.RunPython(add_default_tags),
    ]
