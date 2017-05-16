from __future__ import absolute_import, unicode_literals

import csv
from babel import Locale
from django.core.management.base import BaseCommand
from wagtail.wagtailimages.tests.utils import Image
from molo.core.models import (
    Languages, Tag, ArticlePage, ArticlePageTags, Main, SectionIndexPage,
    TagIndexPage)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_name', type=str)

    def handle(self, *args, **options):
        csv_name = options.get('csv_name', None)
        mains = Main.objects.all()
        articles = {}
        with open(csv_name) as articles_tags:
            reader = csv.reader(articles_tags)
            if mains:
                for row in reader:
                    key = row[0]
                    articles[key] = row[1:]

        for main in mains:
            section_index = SectionIndexPage.objects.child_of(main).first()
            main_lang = Languages.for_site(main.get_site()).languages.filter(
                is_active=True, is_main_language=True).first()
            if section_index and main_lang:
                if main_lang.locale == 'en':
                    for article_slug in articles:
                        article = ArticlePage.objects.descendant_of(
                            section_index).filter(slug=article_slug).first()
                        if article:
                            for image_title in articles.get(article_slug):
                                image = Image.objects.filter(
                                    title=image_title).first()
                                if image:
                                    article.image = image
                                    article.save_revision().publish()

                                else:
                                    self.stdout.write(self.style.NOTICE(
                                        'Image "%s" does not exist in "%s"'
                                        % (image_title, main)))
                        else:
                            self.stdout.write(self.style.ERROR(
                                'Article "%s" does not exist in "%s"'
                                % (article_slug, main.get_site())))
                else:
                    self.stdout.write(self.style.NOTICE(
                        'Main language of "%s" is not English.'
                        ' The main language is "%s"'
                        % (main.get_site(), main_lang)))
            else:
                if not section_index:
                    self.stdout.write(self.style.NOTICE(
                        'Section Index Page does not exist in "%s"' % main))
                if not main_lang:
                    self.stdout.write(self.style.NOTICE(
                        'Main language does not exist in "%s"' % main))
