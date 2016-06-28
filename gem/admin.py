from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from gem.models import GemUserProfile, GemReportComment
from molo.commenting.admin import MoloCommentAdmin
from molo.commenting.models import MoloComment


class GemUserProfileInlineModelAdmin(admin.StackedInline):
    model = GemUserProfile
    can_delete = False


class GemReportCommentModelAdmin(admin.StackedInline):
    model = GemReportComment
    can_delete = False


class GemUserAdmin(UserAdmin):
    inlines = (GemUserProfileInlineModelAdmin, )
    list_display = UserAdmin.list_display + ('gender',)

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemReportCommentAdmin(MoloCommentAdmin):
    inlines = (GemReportCommentModelAdmin,)
    list_display = MoloCommentAdmin.list_display + ('reported_for', )

    def reported_for(self, obj):
        return obj.gem_comment.get_reported_reason_display()


admin.site.unregister(User)
admin.site.register(User, GemUserAdmin)

admin.site.unregister(MoloComment)
admin.site.register(MoloComment, GemReportCommentAdmin)
