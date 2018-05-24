"""
This package contains customisations specific to the Girl Effect project.
The technical background can be found here:
https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#additional-optional-configuration
"""
import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth.models import Permission
from molo.profiles.models import UserProfile
from wagtail.wagtailcore.models import Site


USERNAME_FIELD = "username"
EMAIL_FIELD = "email"

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

    user.first_name = claims.get("given_name") or claims.get("nickname", "")
    user.last_name = claims.get("family_name", "")
    user.email = claims.get("email", "")
    user.save()

    # Ensure the profile is linked to their auth service account using the uuid
    # If, for some reason, the user doesn't have a profile for some reason
    if not hasattr(user, 'profile'):
        user.profile = UserProfile(user=user)
        user.profile.site = Site.objects.get(is_default_site=True)
        user.profile.save()

    if user.profile.auth_service_uuid is None:
        user.profile.auth_service_uuid = claims.get("sub")
        user.profile.save()

    # Synchronise the roles that the user has.
    # The list of roles may contain more or less roles
    # than the previous time the user logged in.
    roles = set(claims.get("roles", []))

    # If the user has any role, we assume that it is a superuser while
    # the permissions are being integrated with the Auth Service
    # (Currently all admin users are superusers)
    # This is to get logging in working on Core QA site and will change
    if roles:
        wagtail_permission = Permission.objects.get(
            content_type__app_label='wagtailadmin', codename='access_admin')
        user.user_permissions.add(wagtail_permission)
        user.is_superuser = True
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
        if email:
            user = self.UserModel.objects.create_user(username, email)
        else:
            user = self.UserModel.objects.create_user(username)
        _update_user_from_claims(user, claims)
        return user

    def verify_claims(self, claims):
        """
        This function can be used to prevent authorisation of users based
        on claims information.
        """
        verified = super(GirlEffectOIDCBackend, self).verify_claims(claims)
        return verified
