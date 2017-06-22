from django.core.management.base import BaseCommand
from molo.core.models import ArticlePage


class Command(BaseCommand):
    def handle(self, *args, **options):
        for article in ArticlePage.objects.all():
            article.title = article.title.lstrip()
            if article.title.isupper():
                article.title = article.title.lower().capitalize()
                for index in range(len(article.title)):
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
