from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        # This command is referenced in a migration so we cannot delete it
        # but we will never have to run it again
        pass
