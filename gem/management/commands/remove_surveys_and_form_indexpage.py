from django.core.management.base import BaseCommand
from wagtail.core.models import Page


class Command(BaseCommand):
    def handle(self, *args, **options):
        Page.objects.filter(slug='forms').delete()
        Page.objects.filter(slug='surveys').delete()
        Page.objects.filter(slug='poll').delete()
        Page.objects.filter(slug='Your-words-competitions').delete()
