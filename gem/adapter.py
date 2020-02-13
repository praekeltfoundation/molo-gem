from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class StaffUserAdapter(DefaultAccountAdapter):
    """ give users an is_staff default of true """

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=commit)
        user.is_staff = True
        wagtailadmin_content_type, created = ContentType.objects.get_or_create(
            app_label='wagtailadmin',
            model='admin'
        )
        admin_permission, created = Permission.objects.get_or_create(
            content_type=wagtailadmin_content_type,
            codename='access_admin',
            name='Can access Wagtail admin'
        )
        user.user_permissions.add(admin_permission)
        if commit:
            user.save()
        return user


class StaffUserSocialAdapter(DefaultSocialAccountAdapter):
    """ give users an is_staff default of true """

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        user.is_staff = True
        wagtailadmin_content_type, created = ContentType.objects.get_or_create(
            app_label='wagtailadmin',
            model='admin'
        )
        admin_permission, created = Permission.objects.get_or_create(
            content_type=wagtailadmin_content_type,
            codename='access_admin',
            name='Can access Wagtail admin'
        )
        user.user_permissions.add(admin_permission)
        user.save()
        return user
