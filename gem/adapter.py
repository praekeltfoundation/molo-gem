from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.signals import social_account_updated

from gem.models import Invite


def get_admin_perms():
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


class StaffUserMixin(object):

    def is_open_for_signup(self, request, sociallogin):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        return Invite.objects.filter(
            email=sociallogin.user.email,
            is_accepted=False).exists()

    def add_perms(self, user, commit=True):
        invite = Invite.objects.\
            get(email=user.email)

        if not user.is_staff:
            user.is_staff = True

        user.groups.add(*invite.groups.all())
        user.user_permissions.add(*invite.permissions.all())

        if not user.has_perm('access_admin'):
            user.user_permissions.add(get_admin_perms())

        if commit:
            user.save()

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


@receiver(social_account_updated)
def my_callback(sender, **kwargs):
    """
    :param sender: SocialLogin
    :param kwargs:
    :return:
    """
    request = kwargs.get('request')
    auth = request.user.is_authenticated

    if auth and not request.user.is_staff:
        request.user.is_staff = True
        request.user.save()

    if auth and not request.user.has_perm('access_admin'):
        request.user.user_permissions.add(get_admin_perms())
