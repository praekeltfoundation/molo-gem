from django.contrib import admin
from django.contrib.auth.models import User
from gem.models import GemUserProfile, GemReportComment
from molo.commenting.admin import MoloCommentAdmin
from molo.commenting.models import MoloComment
from molo.profiles.admin import ProfileUserAdmin
from gem.models import GemUserProfile
from molo.profiles.admin import ProfileUserAdmin


class GemUserProfileInlineModelAdmin(admin.StackedInline):
    model = GemUserProfile
    can_delete = False


class GemReportCommentModelAdmin(admin.StackedInline):
    model = GemReportComment
    can_delete = True
    max_num = 0


class GemUserAdmin(ProfileUserAdmin):
    inlines = (GemUserProfileInlineModelAdmin, )
    list_display = ProfileUserAdmin.list_display + ('gender',)

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemReportCommentAdmin(MoloCommentAdmin):
    inlines = (GemReportCommentModelAdmin,)
    list_display = MoloCommentAdmin.list_display + ('reported_reason', )

    def reported_reason(self, obj):
        reported_for = GemReportComment.objects.filter(
            comment=self.id
        )
        return reported_for


admin.site.unregister(User)
admin.site.register(User, GemUserAdmin)

admin.site.unregister(MoloComment)
admin.site.register(MoloComment, GemReportCommentAdmin)
