from django.core.management.base import BaseCommand
from gem.models import GemUserProfile


class Command(BaseCommand):
    '''
    Copies the gem profile gender to molo profiles gender
    '''
    def handle(self, *args, **options):
        for gem_profile in GemUserProfile.objects.all():
            if hasattr(gem_profile.user, 'profile'):
                profile = gem_profile.user.profile
                profile.gender = gem_profile.gender
                profile.save()
