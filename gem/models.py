from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from gem.constants import GENDERS
from django.contrib import admin


class GemUserProfile(models.Model):
    user = models.OneToOneField(
        User, related_name="gem_profile", primary_key=True)

    gender = models.CharField(
        max_length=1, choices=GENDERS, blank=True, null=True)


class GemUserInline(admin.StackedInline):
    model = GemUserProfile
    can_delete = False
    verbose_name_plural = 'Gem User'


@receiver(post_save, sender=User)
def gem_user_profile_handler(sender, instance, created, **kwargs):
    if created:
        profile = GemUserProfile(user=instance)
        profile.save()


class UserAdmin(BaseUserAdmin):
    inlines = (GemUserInline, )
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'gender', 'is_staff')

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
