from django.core.management.base import BaseCommand
from molo.core.models import ArticlePage, BannerPage, Main


class Command(BaseCommand):
    def handle(self, *args, **options):
        for main in Main.objects.all():
            for banner in BannerPage.objects.descendant_of(main):
                if banner.banner_link_page:
                    old_article_slug = ArticlePage.objects.get(
                        pk=banner.banner_link_page.pk).slug
                    new_article = ArticlePage.objects.descendant_of(
                        main).filter(slug=old_article_slug).first()
                    if new_article:
                        banner.banner_link_page = new_article
                    else:
                        self.stdout.write(self.style.ERROR(
                            'Article "%s" does not exist in "%s"'
                            % (old_article_slug, main.get_site())))
                        banner.banner_link_page = None
                    if banner.live:
                        banner.save_revision().publish()
                    else:
                        banner.save_revision()
