import json
from django.core.management.base import BaseCommand
from molo.core.models import SiteLanguage


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = {}
        langs = SiteLanguage.objects.all()
        print(langs)

        for lang in langs:
            lang_data = {}
            lang_data["locale"] = lang.locale
            data[lang.pk] = lang_data

        with open('langs.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
