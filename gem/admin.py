from django.contrib import admin
from django.contrib.auth.models import User
from gem.models import GemUserProfile, GemCommentReport
from molo.commenting.admin import MoloCommentAdmin
from molo.commenting.models import MoloComment
from molo.profiles.admin import ProfileUserAdmin
from django.http import HttpResponse
import csv


def download_as_csv_gem(GemUserAdmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    writer = csv.writer(response)
    user_model_fields = (
        'username', 'email', 'first_name',
        'last_name', 'is_staff', 'date_joined')
    profile_fields = ('alias', 'mobile_number', 'date_of_birth')
    gem_profile_fields = ('gender',)
    writer.writerow([user_model_fields, profile_fields, gem_profile_fields])
    for obj in queryset:
        if obj.profile.alias:
            obj.profile.alias = obj.profile.alias.encode('utf-8')
        obj.username = obj.username.encode('utf-8')
        obj.date_joined = obj.date_joined.strftime("%Y-%m-%d %H:%M")
        writer.writerow(
            [getattr(obj, field) for field in user_model_fields] +
            [getattr(obj.profile, field) for field in profile_fields] +
            [getattr(obj.gem_profile, field) for field in gem_profile_fields])
    return response
download_as_csv_gem.short_description = "Download selected as csv gem"


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
    actions = ProfileUserAdmin.actions + [download_as_csv_gem]

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemCommentReportAdmin(MoloCommentAdmin):
    inlines = (GemCommentReportModelAdmin,)


admin.site.unregister(User)
admin.site.register(User, GemUserAdmin)

admin.site.unregister(MoloComment)
admin.site.register(MoloComment, GemCommentReportAdmin)
