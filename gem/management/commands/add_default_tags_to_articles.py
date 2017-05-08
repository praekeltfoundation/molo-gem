from __future__ import absolute_import, unicode_literals

import csv
from django.core.management.base import BaseCommand
from molo.core.models import (
    SiteLanguage, Tag, ArticlePage, ArticlePageTags)


class Command(BaseCommand):
    def handle(self, **options):
        main_lang = SiteLanguage.objects.filter(
            is_active=True, is_main_language=True).first()
        reader = csv.reader(open('articles_tags.csv'))

        articles = {}

        if main_lang.locale == "en":
            for row in reader:
                key = row[0]
                articles[key] = row[1:]
            for article_slug in articles:
                article = ArticlePage.objects.filter(slug=article_slug).first()
                if article:
                    for tag_title in articles.get(article_slug):
                        tag = Tag.objects.filter(title=tag_title).first()
                        if tag:
                            article_page_ag = ArticlePageTags(
                                page=article, tag=tag)
                            article_page_ag.save()
