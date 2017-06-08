from __future__ import absolute_import, unicode_literals

import csv
from babel import Locale
from django.core.management.base import BaseCommand
from wagtail.wagtailimages.tests.utils import Image
from molo.core.models import Languages, SectionPage, Main, SectionIndexPage


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_name', type=str)
        parser.add_argument('locale', type=str)

    def handle(self, *args, **options):
        csv_name = options.get('csv_name', None)
        locale_code = options.get('locale', None)
        mains = Main.objects.all()
        sections = {}
        with open(csv_name) as sections_images:
            reader = csv.reader(sections_images)
            if mains:
                for row in reader:
                    key = row[0]
                    sections[key] = row[1:]

        for main in mains:
            section_index = SectionIndexPage.objects.child_of(main).first()
            main_lang = Languages.for_site(main.get_site()).languages.filter(
                is_active=True, is_main_language=True).first()
            translated_sections = SectionPage.objects.descendant_of(
                section_index).filter(
                languages__language__is_main_language=False).live()
            for translated_section in translated_sections:
                translated_section.image = None
                translated_section.save_revision().publish()

            if section_index and main_lang:
                if main_lang.locale == locale_code:
                    for section_slug in sections:
                        section = SectionPage.objects.descendant_of(
                            section_index).filter(slug=section_slug).first()
                        if section:
                            for image_title in sections.get(section_slug):
                                image = Image.objects.filter(
                                    title=image_title + ".jpg").first()
                                if image:
                                    section.image = image
                                    section.extra_style_hints = section.slug
                                    section.save_revision().publish()

                                else:
                                    self.stdout.write(self.style.NOTICE(
                                        'Image "%s" does not exist in "%s"'
                                        % (image_title, main)))
                        else:
                            self.stdout.write(self.style.ERROR(
                                'section "%s" does not exist in "%s"'
                                % (section_slug, main.get_site())))
                else:
                    self.stdout.write(self.style.NOTICE(
                        'Main language of "%s" is not "%s".'
                        ' The main language is "%s"'
                        % (main.get_site(), locale_code, main_lang)))
            else:
                if not section_index:
                    self.stdout.write(self.style.NOTICE(
                        'Section Index Page does not exist in "%s"' % main))
                if not main_lang:
                    self.stdout.write(self.style.NOTICE(
                        'Main language does not exist in "%s"' % main))
