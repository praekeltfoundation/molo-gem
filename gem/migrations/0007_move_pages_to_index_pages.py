# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def move_banners_to_index_page(apps, schema_editor):
    from molo.core.models import (
        LanguagePage, BannerPage, BannerIndexPage, Main)
    main = Main.objects.all().first()
    current_language = LanguagePage.objects.live().first()

    if main and current_language:
        # Move existing banners
        index_page = BannerIndexPage.objects.live().first()
        for page in BannerPage.objects.all().child_of(current_language):
            page.move(index_page, pos='last-child')


def move_footers_to_index_page(apps, schema_editor):
    from molo.core.models import (LanguagePage, FooterPage,
                                  FooterIndexPage, Main)

    main = Main.objects.all().first()
    current_language = LanguagePage.objects.live().first()

    if main and current_language:
        # Move existing footers
        index_page = FooterIndexPage.objects.live().first()
        for page in FooterPage.objects.all().child_of(current_language):
            page.move(index_page, pos='last-child')


def move_sections_to_index_page(apps, schema_editor):
    from molo.core.models import (LanguagePage, SectionPage,
                                  SectionIndexPage, Main)
    main = Main.objects.all().first()
    current_language = LanguagePage.objects.live().first()

    if main and current_language:
        # Move existing sections
        index_page = SectionIndexPage.objects.live().first()
        for page in SectionPage.objects.all().child_of(current_language):
            page.move(index_page, pos='last-child')


def move_polls_to_index_page(apps, schema_editor):
    from molo.core.models import (LanguagePage, Main)
    from molo.polls.models import (Question, FreeTextQuestion, PollsIndexPage)
    main = Main.objects.all().first()
    current_language = LanguagePage.objects.live().first()

    if main and current_language:
        # Move existing questions
        index_page = PollsIndexPage.objects.live().first()
        for page in Question.objects.all().child_of(current_language):
            page.move(index_page, pos='last-child')
        # Move existing FreeTextQuestion
        for page in FreeTextQuestion.objects.all().child_of(current_language):
            page.move(index_page, pos='last-child')


def move_yourwords_to_index_page(apps, schema_editor):
    from molo.core.models import (LanguagePage, Main)
    from molo.yourwords.models import (
        YourWordsCompetition, YourWordsCompetitionIndexPage)
    main = Main.objects.all().first()
    current_language = LanguagePage.objects.live().first()

    if main and current_language:
        # Move existing your words competition
        index_page = YourWordsCompetitionIndexPage.objects.live().first()
        for p in YourWordsCompetition.objects.all().child_of(current_language):
            p.move(index_page, pos='last-child')


class Migration(migrations.Migration):

    dependencies = [
        ('gem', '0006_add_language_relation'),
    ]

    operations = [
        migrations.RunPython(move_banners_to_index_page),
        migrations.RunPython(move_footers_to_index_page),
        migrations.RunPython(move_sections_to_index_page),
        migrations.RunPython(move_polls_to_index_page),
        migrations.RunPython(move_yourwords_to_index_page),
    ]
