import csv
import datetime

from collections import Counter

from daterange_filter.filter import DateRangeFilter
from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from gem.models import GemUserProfile, GemCommentReport
from gem.tasks import send_export_email_gem

from import_export.fields import Field
from import_export.widgets import DateTimeWidget, DateWidget
from import_export.resources import ModelResource
from import_export.results import RowResult

from molo.commenting.admin import MoloCommentAdmin, MoloCommentsModelAdmin
from molo.commenting.models import MoloComment
from molo.profiles.admin import (
    FrontendUsersModelAdmin,
    FrontendUsersDateRangeFilter,
)
from molo.profiles.admin import ProfileUserAdmin
from molo.profiles.admin_views import FrontendUsersAdminView
from molo.profiles.models import UserProfile
from molo.surveys.models import SegmentUserGroup

from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.wagtailadmin import messages
from wagtail.wagtailcore.models import Site

from .admin_forms import FrontEndAgeToDateOfBirthFilter, UserListForm


def download_as_csv_gem(self, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    writer = csv.writer(response)
    user_model_fields = ('id', 'username', 'is_active', 'last_login')
    profile_fields = ('date_of_birth',)
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


class UserProfileInlineModelAdmin(admin.StackedInline):
    model = UserProfile
    can_delete = False


class GemCommentReportModelAdmin(admin.StackedInline):
    model = GemCommentReport
    can_delete = True
    max_num = 0
    actions = None
    readonly_fields = ["user", "reported_reason", ]


class GemFrontendUsersResource(ModelResource):
    gender = Field()
    date_of_birth = Field()

    class Meta:
        model = User
        fields = ('id', 'username', 'date_of_birth',
                  'is_active', 'date_joined', 'last_login', 'gender')

        export_order = fields

    def dehydrate_gender(self, user):
        if hasattr(user, 'gem_profile'):
            return user.gem_profile.get_gender_display() if hasattr(
                user, 'gem_profile') else ''
        return None

    def dehydrate_date_of_birth(self, user):
        return user.profile.date_of_birth if hasattr(user, 'profile') else ''


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


# Remove the non gem user export
ProfileUserAdmin.actions = []


class GemUserAdmin(ProfileUserAdmin):
    resource_class = GemMergedCMSUserResource
    inlines = (GemUserProfileInlineModelAdmin, UserProfileInlineModelAdmin)
    list_display = ('id', 'username', '_date_of_birth', 'is_active',
                    'last_login', 'gem_gender',)
    actions = [download_as_csv_gem]
    list_filter = (
        'gem_profile__gender',
        ('last_login', DateRangeFilter),
        ('profile__date_of_birth', FrontEndAgeToDateOfBirthFilter)
    )

    def gem_gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemFrontendUsersAdminView(FrontendUsersAdminView):
    def send_export_email_to_celery(self, email, arguments):
        send_export_email_gem.delay(email, arguments)

    def get_template_names(self):
        return 'admin/gem_frontend_users_admin_view.html'

    def post(self, request, *args, **kwargs):
        qs = self.get_queryset(request)
        form = UserListForm(qs, data=request.POST)
        if form.is_valid():
            ids = [
                user_id for user_id, checked in form.cleaned_data.items()
                if checked
            ]
            if ids:
                qs = qs.filter(id__in=ids)

        if 'email' in request.POST:
            self.send_export_email_to_celery(
                request.user.email,
                {'id__in': list(qs.values_list('id', flat=True))},
            )
            messages.success(request, _(
                "CSV emailed to '{0}'").format(request.user.email))
            return redirect(request.path)
        else:
            if qs.exists():
                group = SegmentUserGroup.objects.create(
                    name='{} group: {}'.format(
                        request.user.username, datetime.datetime.now()
                    ),
                )
                group.users.add(*qs)
                return redirect(
                    'surveys_segmentusergroup_modeladmin_edit',
                    instance_pk=group.id,
                )
            messages.warning(
                request, _('Cannot create a group with no users.')
            )
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(GemFrontendUsersAdminView, self).get_context_data(
            **kwargs
        )
        context['form'] = UserListForm(context['object_list'])
        return context

    def lookup_allowed(self, lookup, value):
        return (
            super(GemFrontendUsersAdminView, self).lookup_allowed(lookup, value) or  # noqa
            # Bug in wagtail see for more information
            # https://github.com/wagtail/wagtail/issues/3980
            lookup.startswith('profile__date_of_birth')
        )


class SegementUserPermissionHelper(PermissionHelper):
    def __init__(self, model, inspect_view_enabled=False):
        model = SegmentUserGroup
        super(SegementUserPermissionHelper, self).__init__(
            model, inspect_view_enabled
        )


class GemFrontendUsersModelAdmin(FrontendUsersModelAdmin):
    permission_helper_class = SegementUserPermissionHelper
    list_display = ('id', 'username', '_date_of_birth', 'is_active',
                    'last_login', 'gender', 'country')
    index_view_class = GemFrontendUsersAdminView
    index_view_extra_js = ['js/modeladmin/index.js']
    list_filter = FrontendUsersModelAdmin.list_filter + (
        'gem_profile__gender',
        ('last_login', FrontendUsersDateRangeFilter),
        ('profile__date_of_birth', FrontEndAgeToDateOfBirthFilter),
    )

    def country(self, obj):
        return obj.profile.site.root_page.title

    def gender(self, obj):
        return obj.gem_profile.get_gender_display()


class GemCommentModelAdmin(MoloCommentsModelAdmin):
    list_display = (
        'comment', 'parent_comment', 'moderator_reply', 'content', '_user',
        'is_removed', 'is_reported', 'reported_count', 'reported_reason',
        'submit_date', 'country')

    def reported_reason(self, obj):
        all_reported_reasons = list(
            GemCommentReport.objects.filter(comment=obj.pk).values_list(
                'reported_reason', flat=True))
        breakdown_of_reasons = []
        for value, count in Counter(all_reported_reasons).most_common():
            reason = '%s, (%s)' % (value, count)
            breakdown_of_reasons.append(reason)

        return breakdown_of_reasons

    def reported_count(self, obj):
        return GemCommentReport.objects.filter(comment=obj.pk).count()


class GemCommentReportAdmin(MoloCommentAdmin):
    inlines = (GemCommentReportModelAdmin,)


admin.site.unregister(User)
admin.site.register(User, GemUserAdmin)

admin.site.unregister(MoloComment)
admin.site.register(MoloComment, GemCommentReportAdmin)
