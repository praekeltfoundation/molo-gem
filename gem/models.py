from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from gem.constants import GENDERS


class GemUserProfile(models.Model):
    user = models.OneToOneField(
        User, related_name="gem_profile", primary_key=True)

    gender = models.CharField(
        max_length=1, choices=GENDERS, blank=True, null=True)


@receiver(post_save, sender=User)
def gem_user_profile_handler(sender, instance, created, **kwargs):
    if created:
        profile = GemUserProfile(user=instance)
        profile.save()
