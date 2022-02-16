import json
from django.core.management.base import BaseCommand
from molo.core.models import Main


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = {}
        mains = Main.objects.all()

        for main in mains:
            main_data = {}
            main_data["title"] = main.title
            main_data["locale"] = main.language.locale
            main_data["hostname"] = main.get_site().hostname
            main_data["port"] = main.get_site().port
            data[main.pk] = main_data

        with open('mains.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
