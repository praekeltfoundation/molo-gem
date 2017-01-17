from django.contrib import admin
from django.contrib.auth.models import User
from gem.models import GemUserProfile, GemCommentReport
from molo.commenting.admin import MoloCommentAdmin
from molo.commenting.models import MoloComment
from molo.profiles.admin import ProfileUserAdmin
from molo.profiles.admin import FrontendUsersModelAdmin
from molo.profiles.admin_import_export import FrontendUsersResource
from django.http import HttpResponse
from import_export.fields import Field
from wagtail.contrib.modeladmin.views import IndexView
from molo.profiles.admin_views import FrontendUsersAdminView
import csv
from gem.tasks import send_export_email_gem


def download_as_csv_gem(GemUserAdmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    writer = csv.writer(response)
    user_model_fields = (
        'username', 'email', 'first_name',
        'last_name', 'is_staff', 'date_joined')
    profile_fields = ('alias', 'mobile_number', 'date_of_birth')
    gem_profile_fields = ('gender',)
    field_names = user_model_fields + profile_fields + gem_profile_fields
    writer.writerow(field_names)
    for obj in queryset:
        if hasattr(obj, 'gem_profile'):
            if obj.profile.alias:
                obj.profile.alias = obj.profile.alias.encode('utf-8')
            obj.username = obj.username.encode('utf-8')
            obj.date_joined = obj.date_joined.strftime("%Y-%m-%d %H:%M")
            writer.writerow(
                [getattr(obj, field) for field in user_model_fields] +
                [getattr(obj.profile, field) for field in profile_fields] +
                [getattr(
                    obj.gem_profile, field) for field in gem_profile_fields])
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
    list_filter = ('gem_profile__gender',)

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemFrontendUsersResource(FrontendUsersResource):
        gender = Field()

        class Meta:
            export_order = FrontendUsersResource.Meta.export_order + (
                'gender',)

        def dehydrate_gender(self, user):
            if hasattr(user, 'gem_profile'):
                return user.gem_profile.get_gender_display() if hasattr(
                    user, 'gem_profile') else ''
            return None


class GemFrontendUsersAdminView(FrontendUsersAdminView):
    def send_export_email_to_celery(self, email, arguments):
        send_export_email_gem.delay(email, arguments)


class GemFrontendUsersModelAdmin(FrontendUsersModelAdmin):
    list_display = FrontendUsersModelAdmin.list_display + ('gender',)
    index_view_class = GemFrontendUsersAdminView

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemCommentReportAdmin(MoloCommentAdmin):
    inlines = (GemCommentReportModelAdmin,)


admin.site.unregister(User)
admin.site.register(User, GemUserAdmin)

admin.site.unregister(MoloComment)
admin.site.register(MoloComment, GemCommentReportAdmin)
