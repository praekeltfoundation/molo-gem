from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from gem.models import GemUserProfile


class GemUserProfileInlineModelAdmin(admin.StackedInline):
    model = GemUserProfile
    can_delete = False


class GemUserAdmin(UserAdmin):
    inlines = (GemUserProfileInlineModelAdmin, )
    list_display = UserAdmin.list_display + ('gender',)

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


admin.site.unregister(User)
admin.site.register(User, GemUserAdmin)
