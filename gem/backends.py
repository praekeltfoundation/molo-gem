"""
This package contains customisations specific to the Girl Effect project.
The technical background can be found here:
https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#additional-optional-configuration
"""
import logging
from datetime import datetime

from wagtail.core.models import Site
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import FieldError, SuspiciousOperation

from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from molo.profiles.models import UserProfile


USERNAME_FIELD = "username"
EMAIL_FIELD = "email"
SUPERUSER_GROUP = 'product_tech_admin'
LOGGER = logging.getLogger(__name__)


def _update_user_from_claims(user, claims):
    """
    Update the user profile with information from the claims.
    This function is called on registration (new user) as well as login events.
    This function provides the mapping from the OIDC claims fields to the
    internal user profile fields.
    We use the role names as the names for Django
    Groups to which a user belongs.
    :param user: The user profile
    :param claims: The claims for the profile
    """
    LOGGER.debug("Updating user {} with claims: {}".format(user, claims))
    data = {
        'first_name': claims.get("given_name") or claims.get("nickname", ""),
        'last_name': claims.get("family_name", ""),
        'email': claims.get("email", ""),
        'username': user.username,
        'date_joined': user.date_joined,
        'is_active': user.is_active
    }
    form = UserChangeForm(instance=user, data=data)
    if form.is_valid():
        user.first_name = \
            claims.get("given_name") or claims.get("nickname", "")
        user.last_name = claims.get("family_name", "")
        user.email = claims.get("email", "")
        user.save()
    else:
        for e in form.errors:
            raise FieldError(e[0])

    username = claims.get("preferred_username", "")

    # If the user doesn't have a profile for some reason make one
    if not hasattr(user, 'profile'):
        user.profile = UserProfile(user=user)

        # TODO: we should be using a more specific site here?
        user.profile.site = Site.objects.get(is_default_site=True)

    # Ensure the profile is linked to their auth service account using the uuid
    if user.profile.auth_service_uuid is None:
        user.profile.auth_service_uuid = claims.get("sub")

        # If a user already exists with this username
        # change that user's username
        if username:
            for u in User.objects.filter(
                    username=username).exclude(pk=user.pk):
                if u.profile and u.profile.auth_service_uuid is None:
                    u.username = str(u.profile.site.pk) + '_' + username
                    u.save()
                else:
                    raise FieldError(
                        'Desired username clashes with user with pk %s whose'
                        ' profile has auth_service_uuid' % u.pk)
            user.username = username
            user.save()

    # Synchronise a user's profile data
    user.profile.gender = claims.get("gender", "-").lower()[0]
    date_of_birth = claims.get("birthdate", None)
    if date_of_birth:
        date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    user.profile.date_of_birth = date_of_birth
    if user.profile.alias is None or user.profile.alias == "":
        user.profile.alias = user.username
    elif user.profile.alias != user.username:
        user.profile.alias = user.username
    user.profile.save()

    # Synchronise the roles that the user has.
    # The list of roles may contain more or less roles
    # than the previous time the user logged in.
    auth_service_roles = set(claims.get("roles", []))
    wagtail_groups = set(group.name for group in user.groups.all())

    # If the user has any role, add the wagtail group equivalent
    # to that role to the user
    if auth_service_roles:
        groups_to_add = auth_service_roles - wagtail_groups
        groups_to_remove = wagtail_groups - auth_service_roles
        for group_name in groups_to_add:
            if group_name == SUPERUSER_GROUP:
                user.is_staff = True
                user.is_superuser = True
                user.save()
            else:
                try:
                    wagtail_group = Group.objects.get(name=group_name)
                    user.groups.add(wagtail_group)
                except Group.DoesNotExist:
                    LOGGER.debug("Group {} does not exist".format(group_name))
        # Remove the user's revoked role
        if user.is_superuser and SUPERUSER_GROUP not in auth_service_roles:
            user.is_superuser = False
            user.save()

        for group_name in groups_to_remove:
            try:
                wagtail_group = Group.objects.get(name=group_name)
                user.groups.remove(wagtail_group)
            except Group.DoesNotExist:
                LOGGER.debug("Group {} does not exist".format(group_name))

        if not user.is_staff and user.groups.all().exists():
            user.is_staff = True
            user.save()

    else:
        user.groups.clear()
        user.is_staff = False
        user.save()


class GirlEffectOIDCBackend(OIDCAuthenticationBackend):

    def filter_users_by_claims(self, claims):
        """
        The default behaviour is to look up users based on their email
        address. However, in the Girl Effect ecosystem the email is optional,
        so we prefer to use the UUID associated with the user profile (
        subject identifier)
        :return: A user identified by the claims, else None
        """
        uuid = claims["sub"]
        try:
            kwargs = {'profile__auth_service_uuid': uuid}
            user = self.UserModel.objects.get(**kwargs)
            # Update the user with the latest info
            _update_user_from_claims(user, claims)
            return [user]
        except self.UserModel.DoesNotExist:
            LOGGER.debug("Lookup failed based on {}".format(kwargs))

        """
        Users with an existing account will be migrated on their first login so
        we find these users based on their User.id
        """
        user_id = claims.get("migration_information", {}).get("user_id", None)
        if user_id is not None:
            try:
                kwargs = {'id': user_id}
                user = self.UserModel.objects.get(**kwargs)
                # Update the user with the latest info
                _update_user_from_claims(user, claims)
                return[user]
            except self.UserModel.DoesNotExist:
                LOGGER.debug("Lookup failed based on {}".format(kwargs))

        return self.UserModel.objects.none()

    def create_user(self, claims):
        """Return object for a newly created user account.
        The default OIDC client create_user() function expects an email address
        to be available. This is not the case for Girl Effect accounts, where
        the email field is optional.
        We use the user id (called the subscriber identity in OIDC) as the
        username, since it is always available and guaranteed to be unique.
        """
        # If we don't have a username we should break
        username = claims.get("preferred_username")
        email = claims.get("email", "")  # Email is optional
        # We create the user based on the username and optional email fields.

        # If a user already exists with this username
        # change that user's username
        for user in self.UserModel.objects.filter(username=username):
            new_username = str(user.profile.site.pk) + '_' + username
            exists = self.UserModel.objects.filter(
                username=new_username).exists()

            can_update = user.profile and not user.profile.auth_service_uuid
            if can_update and not exists:
                user.username = new_username
                user.save()
            else:
                raise FieldError(
                        'Desired username clashes with user with pk %s whose'
                        ' profile has an auth_service_uuid' % user.pk)

        if email:
            user = self.UserModel.objects.create_user(username, email)
        else:
            user = self.UserModel.objects.create_user(username)
        _update_user_from_claims(user, claims)
        return user

    def get_or_create_user(self, access_token, id_token, payload):
        """
        Returns a User instance if 1 user is found. Creates a user if not found
        and configured to do so. Returns nothing if multiple users are matched.
        """

        user_info = self.get_userinfo(access_token, id_token, payload)
        username = user_info.get("preferred_username")
        claims_verified = self.verify_claims(user_info)

        if not claims_verified:
            raise SuspiciousOperation('Claims verification failed')

        users = self.filter_users_by_claims(user_info)

        if len(users) == 1:
            return self.update_user(users[0], user_info)

        elif len(users) > 1:
            # In the rare case that two user accounts have the same email,
            # bail. Randomly selecting one seems really wrong.
            raise SuspiciousOperation('Multiple users returned')

        elif self.get_settings('OIDC_CREATE_USER', True):
            user = self.create_user(user_info)
            return user

        else:
            LOGGER.debug('Login failed: No user with username %s found, and '
                         'OIDC_CREATE_USER is False', username)
        return None

    def verify_claims(self, claims):
        """
        Verify the provided claims to decide
        if authentication should be allowed.
        """

        # Verify claims required by default configuration
        scopes = self.get_settings('OIDC_RP_SCOPES', 'openid email')
        if 'preferred_username' in scopes.split():
            return 'preferred_username' in claims

        LOGGER.warning(
            'Custom OIDC_RP_SCOPES defined. You need to override'
            ' `verify_claims` for custom claims verification.'
        )
        return True

    def verify_token(self, token, **kwargs):
        site = self.request.site
        if not hasattr(site, "oidcsettings"):
            raise RuntimeError(
                "Site {} has no settings configured.".format(site))

        self.OIDC_RP_CLIENT_SECRET = site.oidcsettings.oidc_rp_client_secret
        return super(GirlEffectOIDCBackend, self).verify_token(token, **kwargs)

    def authenticate(self, **kwargs):
        if "request" in kwargs:
            site = kwargs["request"].site
            if not hasattr(site, "oidcsettings"):
                raise RuntimeError(
                    "Site {} has no settings configured.".format(site))

            self.OIDC_RP_CLIENT_ID = site.oidcsettings.oidc_rp_client_id
            self.OIDC_RP_CLIENT_SECRET = \
                site.oidcsettings.oidc_rp_client_secret
        return super(GirlEffectOIDCBackend, self).authenticate(**kwargs)
