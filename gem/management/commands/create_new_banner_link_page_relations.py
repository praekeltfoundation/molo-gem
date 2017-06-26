from django.core.management.base import BaseCommand
from molo.core.models import ArticlePage, BannerPage, Main


class Command(BaseCommand):
    def handle(self, *args, **options):
        for main in Main.objects.all():
            for banner in BannerPage.objects.descendant_of(main):
                old_article_slug = ArticlePage.objects.get(
                    pk=banner.banner_link_page).slug
                new_article = ArticlePage.objects.descendant_of(
                    main).get(slug=old_article_slug)
                banner.banner_link_page = new_article
                if banner.live:
                    banner.save_revision().publish()
                else:
                    banner.save_revision()
