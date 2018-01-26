from django.core.management.base import BaseCommand
from gem.models import GemUserProfile


class Command(BaseCommand):
    '''
    Copies the migrated username from gem_profiles and adds it to molo profile
    '''
    def handle(self, *args, **options):
        for gem_profile in GemUserProfile.objects.all():
            if hasattr(gem_profile.user, 'profile'):
                profile = gem_profile.user.profile
                profile.migrated_username = gem_profile.migrated_username
                profile.save()
