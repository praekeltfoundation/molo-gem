# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_language_relation(apps, schema_editor):
    from molo.core.models import SiteLanguage, LanguageRelation
    from wagtail.core.models import Page

    if not (SiteLanguage.objects.filter(is_main_language=True)).exists():
        from molo.core.models import LanguagePage
        current_language = LanguagePage.objects.live().first()

        if current_language:
            main_lang = SiteLanguage.objects.create(
                locale=current_language.code)
            for p in Page.objects.all().descendant_of(current_language):
                LanguageRelation.objects.create(page=p, language=main_lang)


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0005_gemsettings'),
        ('polls', '0003_create_polls_index_pages'),
        ('yourwords', '0006_create_your_words_index_pages'),
    ]

    operations = [
        migrations.RunPython(add_language_relation),
    ]
