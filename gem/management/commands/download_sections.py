import json
from django.core.management.base import BaseCommand
from molo.core.models import SectionPage


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = {}
        sections = SectionPage.objects.all()

        for section in sections:
            section_data = {}
            section_data["title"] = section.title
            section_data["slug"] = section.slug
            section_data["locale"] = section.language.locale
            section_data["live"] = section.live
            section_data["uuid"] = section.uuid
            section_data["translation_pks"] = [page.pk for page in section.translated_pages.all()]
            section_data["description"] = section.description
            if section.image:
                section_data["image_name"] = section.image.title
            if section.get_parent_section():
                section_data["section_parent_slug"] = section.get_parent_section().slug
            data[section.pk] = section_data

        with open('sections.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
