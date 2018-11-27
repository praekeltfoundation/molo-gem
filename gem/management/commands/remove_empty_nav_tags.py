from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.models import ArticlePage


class Command(BaseCommand):
    help = 'Remove empty nav_tags from all articles'

    def handle(self, **options):
        for article in ArticlePage.objects.all():
            if not (article.tags is None):
                for nav_tag in article.nav_tags.all():
                    if nav_tag.tag is None:
                        nav_tag.delete()
