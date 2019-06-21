from molo.core import models
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('old_lang_pk', type=str)
        parser.add_argument('new_lang_pk', type=str)

    def handle(self, *args, **options):
        old_lang_pk = options.get('old_lang_pk', None)
        new_lang_pk = options.get('new_lang_pk', None)
        if not old_lang_pk or not new_lang_pk or old_lang_pk == new_lang_pk:
            self.stdout.write(self.style.WARNING(
                "Invalid language primary keys were entered" +
                str(old_lang_pk) + " and " + str(new_lang_pk)))
        else:
            old_lang = models.SiteLanguage.objects.filter(pk=old_lang_pk)[0]
            new_lang = models.SiteLanguage.objects.filter(pk=new_lang_pk)[0]
            if not old_lang or not new_lang:
                self.stdout.write(self.style.WARNING(
                    "Invalid language primary keys were entered" +
                    str(old_lang_pk) + " and " + str(new_lang_pk)))
            else:
                old_lang_articles = models.ArticlePage.objects.filter(
                    language=old_lang)
                for art in old_lang_articles:
                    art.language = new_lang
                    art.save()
