import json
from django.core.management.base import BaseCommand
from wagtail.images.models import Image


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = {}
        images = Image.objects.all()

        for image in images:
            image_data = {}
            image_data["title"] = image.title
            image_data["filename"] = image.filename
            image_data["usage_url"] = image.usage_url
            image_data["url"] = image.file.url
            image_data["width"] = image.file.width
            image_data["height"] = image.file.height
            data[image.pk] = image_data

        with open('images.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
