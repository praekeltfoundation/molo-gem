from __future__ import absolute_import, unicode_literals

import csv
from django.core.management.base import BaseCommand
from molo.core.models import (
    Languages, Tag, ArticlePage, ArticlePageTags, Main, SectionIndexPage,
    TagIndexPage)


class Command(BaseCommand):
    def handle(self, **options):
        mains = Main.objects.all()
        articles = {}
        with open('articles_tags.csv') as articles_tags:
            reader = csv.reader(articles_tags)
            if mains:
                for row in reader:
                    key = row[0]
                    articles[key] = row[1:]

        for main in mains:
            section_index = SectionIndexPage.objects.child_of(main).first()
            tag_index = TagIndexPage.objects.child_of(main).first()
            main_lang = Languages.for_site(main.get_site()).languages.filter(
                is_active=True, is_main_language=True).first()
            if main_lang.locale == "en":
                for article_slug in articles:
                    article = ArticlePage.objects.descendant_of(
                        section_index).filter(slug=article_slug).first()
                    if article:
                        for tag_title in articles.get(article_slug):
                            tag = Tag.objects.child_of(
                                tag_index).filter(title=tag_title).first()
                            if tag and not article.nav_tags.filter(
                                    tag__title=tag):
                                article_page_ag = ArticlePageTags(
                                    page=article, tag=tag)
                                article_page_ag.save()
                    else:
                        print "Article ", article_slug,\
                            "does not exist in", main.get_site()
            else:
                print "Main language of ", main.get_site(),\
                    "is not English, it is ", main_lang
