from molo.core import models
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


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
            try:
                old_lang = models.SiteLanguage.objects.get(pk=old_lang_pk)
                new_lang = models.SiteLanguage.objects.get(pk=new_lang_pk)
                if not old_lang or not new_lang:
                    self.stdout.write(self.style.WARNING(
                        "Invalid language primary keys were entered" +
                        str(old_lang_pk) + " and " + str(new_lang_pk)))
                else:
                    pages = models.MoloPage.objects.all()
                    for page in pages:
                        if hasattr(page.specific, 'language'):
                            if page.specific.language == old_lang:
                                page.specific.language = new_lang
                                if not page.specific.has_unpublished_changes:
                                    page.specific.save_revision().publish()
                                else:
                                    page.specific.save_revision().publish()
                                    page.specific.unpublish()
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                self.stdout.write(self.style.WARNING(
                    "Invalid language primary keys were entered" +
                    str(old_lang_pk) + " and " + str(new_lang_pk)))
