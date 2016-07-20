from django.contrib import admin
from django.contrib.auth.models import User
from gem.models import GemUserProfile
from molo.profiles.admin import ProfileUserAdmin


class GemUserProfileInlineModelAdmin(admin.StackedInline):
    model = GemUserProfile
    can_delete = False


class GemUserAdmin(ProfileUserAdmin):
    inlines = (GemUserProfileInlineModelAdmin, )
    list_display = ProfileUserAdmin.list_display + ('gender',)

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


admin.site.unregister(User)
admin.site.register(User, GemUserAdmin)
