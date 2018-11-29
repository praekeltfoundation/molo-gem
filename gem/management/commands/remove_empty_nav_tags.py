from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.models import ArticlePage
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Remove empty nav_tags from all articles'

    def handle(self, **options):
        for article in ArticlePage.objects.all():
            for nav_tag in article.nav_tags.all():
                if nav_tag.tag is None:
                    try:
                        nav_tag.delete()
                        if article.live:
                            article.save_revision().publish()
                        else:
                            article.save_revision()
                    except IntegrityError:
                            print("IntegrityError: Articles that belong sites "
                                  "taht are not used cannot be saved")
