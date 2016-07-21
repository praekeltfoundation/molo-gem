from django.contrib import admin
from django.contrib.auth.models import User
from gem.models import GemUserProfile, GemCommentReport
from molo.commenting.admin import MoloCommentAdmin
from molo.commenting.models import MoloComment
from molo.profiles.admin import ProfileUserAdmin


class GemUserProfileInlineModelAdmin(admin.StackedInline):
    model = GemUserProfile
    can_delete = False


class GemCommentReportModelAdmin(admin.StackedInline):
    model = GemCommentReport
    can_delete = True
    max_num = 0
    actions = None
    readonly_fields = ["user", "reported_reason", ]


class GemUserAdmin(ProfileUserAdmin):
    inlines = (GemUserProfileInlineModelAdmin, )
    list_display = ProfileUserAdmin.list_display + ('gender',)

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemCommentReportAdmin(MoloCommentAdmin):
    inlines = (GemCommentReportModelAdmin,)


admin.site.unregister(User)
admin.site.register(User, GemUserAdmin)

admin.site.unregister(MoloComment)
admin.site.register(MoloComment, GemCommentReportAdmin)
