import csv

from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.conf import settings
from django.db.models import Q

from gem.models import GemUserProfile, GemCommentReport
from gem.tasks import send_export_email_gem

from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, DateWidget, ForeignKeyWidget
from import_export.resources import ModelResource, Diff
from import_export.results import RowResult

from molo.commenting.admin import MoloCommentAdmin
from molo.commenting.models import MoloComment
from molo.profiles.admin import FrontendUsersModelAdmin
from molo.profiles.admin import ProfileUserAdmin
from molo.profiles.admin_import_export import FrontendUsersResource
from molo.profiles.admin_views import FrontendUsersAdminView
from molo.profiles.models import UserProfile

from wagtail.contrib.modeladmin.views import IndexView
from wagtail.wagtailcore.models import Site


class GemUserProfileInlineModelAdmin(admin.StackedInline):
    model = GemUserProfile
    can_delete = False


class UserProfileInlineModelAdmin(admin.StackedInline):
    model = UserProfile
    can_delete = False


class GemCommentReportModelAdmin(admin.StackedInline):
    model = GemCommentReport
    can_delete = True
    max_num = 0
    actions = None
    readonly_fields = ["user", "reported_reason", ]


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


class TzDateTimeWidget(DateTimeWidget):

    def render(self, value, obj):
        if settings.USE_TZ:
            value = localtime(value)
        return super(TzDateTimeWidget, self).render(value, obj)


class GemMergedCMSUserResource(ModelResource):
    date_of_birth = Field(
        'profile__date_of_birth', 'date_of_birth', widget=DateWidget())
    alias = Field('profile__alias', 'alias')
    mobile_number = Field('profile__mobile_number', 'mobile_number')
    gender = Field('gem_profile__gender', 'gender')
    migrated_username = Field(
        'gem_profile__migrated_username', 'migrated_username')
    security_question_1_answer = Field(
        'gem_profile__security_question_1_answer',
        'security_question_1_answer')
    security_question_2_answer = Field(
        'gem_profile__security_question_2_answer',
        'security_question_2_answer')
    date_joined = Field(
        'date_joined', 'date_joined', widget=TzDateTimeWidget())
    site = Field('profile__site__pk', 'site')

    class Meta:
        model = User
        exclude = ('id', 'is_superuser', 'groups',
                   'user_permissions', 'is_staff', 'last_login')
        export_order = ('username', 'first_name', 'last_name', 'email',
                        'is_active', 'date_joined', 'mobile_number',
                        'alias', 'date_of_birth', 'gender', 'site',
                        'migrated_username')
        import_id_fields = ['username']
        skip_unchanged = True

    def export(self, queryset=None, *args, **kwargs):
        qs = self._meta.model.objects.exclude(
            Q(is_staff=True) | Q(is_superuser=True))
        return super(GemMergedCMSUserResource, self).export(
            qs, *args, **kwargs)

    def dehydrate_migrated_username(self, user):
        return user.username

    def get_prefixed_username(self, data):
        return '%s_%s' % (
            data['site'], data['username']
        ) if data.get('site') else data['username']

    def before_import_row(self, row, **kwargs):
        row['username'] = self.get_prefixed_username(row)

    def import_row(self, row, instance_loader, *args, **kwargs):
        # Disable updating - we don't want to mistakenly override existing data
        if not User.objects.filter(
                username=self.get_prefixed_username(row)).exists():
            return super(GemMergedCMSUserResource, self).import_row(
                row, instance_loader, *args, **kwargs)

        row_result = self.get_row_result_class()()
        row_result.import_type = RowResult.IMPORT_TYPE_SKIP
        return row_result

    def import_obj(self, obj, data, dry_run):
        self.import_field(self.fields['username'], obj, data)
        obj.save()

        if data.get('site'):
            obj.profile.site = Site.objects.get(pk=data.get('site'))
            obj.profile.save()

        super(GemMergedCMSUserResource, self).import_obj(obj, data, dry_run)

    def after_save_instance(self, instance, using_transactions, dry_run):
        # Save related models
        instance.profile.save()
        instance.gem_profile.save()


class GemUserAdmin(ProfileUserAdmin):
    resource_class = GemMergedCMSUserResource
    inlines = (GemUserProfileInlineModelAdmin, UserProfileInlineModelAdmin)
    list_display = ProfileUserAdmin.list_display + ('gem_gender',)
    actions = None
    list_filter = ('gem_profile__gender',)

    def gem_gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemFrontendUsersAdminView(FrontendUsersAdminView):
    def send_export_email_to_celery(self, email, arguments):
        pass

    def get_template_names(self):
        return 'admin/gem_frontend_users_admin_view.html'


class GemFrontendUsersModelAdmin(FrontendUsersModelAdmin):
    list_display = ('id', 'username', '_date_of_birth', 'is_active', 'last_login', 'gender',)
    index_view_class = GemFrontendUsersAdminView

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemCommentReportAdmin(MoloCommentAdmin):
    inlines = (GemCommentReportModelAdmin,)


admin.site.unregister(User)
admin.site.register(User, GemUserAdmin)

admin.site.unregister(MoloComment)
admin.site.register(MoloComment, GemCommentReportAdmin)
