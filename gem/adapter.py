from django.db.models import Q
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from gem.models import Invite


class StaffUserMixin(object):

    def get_admin_perms(self):
        wagtailadmin_content_type, created = ContentType.objects.get_or_create(
            app_label='wagtailadmin',
            model='admin'
        )
        admin_permission, created = Permission.objects.get_or_create(
            content_type=wagtailadmin_content_type,
            codename='access_admin',
            name='Can access Wagtail admin'
        )
        return admin_permission

    def is_open_for_signup(self, request, sociallogin=None):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        email = None

        if sociallogin:
            email = sociallogin.user.email or None

        return Invite.objects.filter(
            email=email, email__isnull=False,
            is_accepted=False).exists()

    def add_perms(self, user, commit=True):
        invite = Invite.objects.\
            filter(email=user.email, is_accepted=False).first()

        if invite and not user.is_staff:
            user.is_staff = True
            if commit:
                user.save()

            user.groups.add(*invite.groups.all())
            user.user_permissions.add(*invite.permissions.all())

            if not user.has_perm('access_admin'):
                user.user_permissions.add(self.get_admin_perms())
            invite.is_accepted = True
            invite.save()


class StaffUserAdapter(StaffUserMixin, DefaultAccountAdapter):
    """ give users an is_staff default of true """

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=commit)
        self.add_perms(user, commit=commit)
        return user


class StaffUserSocialAdapter(StaffUserMixin, DefaultSocialAccountAdapter):
    """ give users an is_staff default of true """

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        self.add_perms(user)
        return user
