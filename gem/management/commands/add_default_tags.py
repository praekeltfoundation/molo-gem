from __future__ import absolute_import, unicode_literals

import csv
from django.core.management.base import BaseCommand
from molo.core.models import (
    Languages, Tag, TagIndexPage, PageTranslation, Main)


class Command(BaseCommand):
    def handle(self, **options):
        mains = Main.objects.all()
        tags = {}
        with open('tags.csv') as tags_csv:
            reader = csv.DictReader(tags_csv)
            if mains:
                for row in reader:
                    key = row.pop('Tags')
                    tags[key] = row
        for main in mains:
            tag_index = TagIndexPage.objects.child_of(main).first()
            main_lang = Languages.for_site(main.get_site()).languages.filter(
                is_active=True, is_main_language=True).first()
            child_languages = Languages.for_site(
                main.get_site()).languages.filter(
                is_active=True, is_main_language=False).all()
            if main_lang:
                add_tags(main_lang, child_languages, tag_index, tags)


def add_tags(main_lang, child_languages, tag_index, tags):
    for tag in tags:
        if tags.get(tag).get(main_lang.locale):
            main_tag = create_tag(
                tags.get(tag).get(main_lang.locale), tag_index)

            for child_lang in child_languages:
                if tags.get(tag).get(child_lang.locale):
                    create_tag_translation(
                        main_tag, child_lang, tags.get(tag).get(
                            child_lang.locale), tag_index)


def create_tag(title, tag_index):
    if Tag.objects.filter(title=title).child_of(tag_index).exists():
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
