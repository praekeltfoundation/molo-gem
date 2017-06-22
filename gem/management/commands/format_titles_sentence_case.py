from __future__ import absolute_import, unicode_literals

import csv
from babel import Locale
from django.core.management.base import BaseCommand
from molo.core.models import (
    Languages, Tag, ArticlePage, ArticlePageTags, Main, SectionIndexPage,
    TagIndexPage)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for article in ArticlePage.objects.all():
            article.title = article.title.lstrip()
            if article.title.isupper():
                article.title = article.title.lower().capitalize()
                for index in range(len(article.title)):
                    print index
                    if article.title[index].isalpha():
                        if not article.title[index].isupper():
                            article.title = article.title[:index] + \
                                article.title[index].upper() + \
                                article.title[index + 1:]
                        break
            if article.live:
                article.save_revision().publish()
            else:
                article.save()
