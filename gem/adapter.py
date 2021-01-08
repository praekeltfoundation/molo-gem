from django.db.models import Q
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from gem.models import Invite
from wagtail.core.models import Site

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
        site = Site.find_for_request(request)
        return Invite.objects.filter(
            email=email, email__isnull=False,
            site=site, is_accepted=False
        ).exists()

    def add_perms(self, user, commit=True):
        invite = Invite.objects.\
            filter(email=user.email, is_accepted=False).first()

        if invite:
            if not user.is_staff:
                user.is_staff = True
                if commit:
                    user.save()

            user.groups.add(*[
                g for g in invite.groups.all()
                if g not in user.groups.all()
            ])
            user.user_permissions.add(*[
                i for i in invite.permissions.all()
                if i not in user.user_permissions.all()
            ])

            if not user.has_perm('wagtailadmin.access_admin'):
                user.user_permissions.add(self.get_admin_perms())

            admin_sites = user.profile.admin_sites
            if not admin_sites.filter(pk=invite.site.pk).exists():
                admin_sites.add(invite.site)

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

    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if not user.id and user.email:
            db_user = User.objects.filter(
                Q(is_superuser=True) | Q(is_staff=True),
                email=user.email).first()
            if db_user:
                self.add_perms(db_user)
                sociallogin.connect(request, db_user)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        self.add_perms(user)
        return user
