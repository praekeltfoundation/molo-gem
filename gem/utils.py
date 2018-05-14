from django.utils.http import urlencode

from django.conf import settings


def provider_logout_url(request):
    """
    This function is used to construct a logout URL that can be used to
    log the user out of
    the Identity Provider (Authentication Service).
    :param request:
    :return:
    """
    parameters = {
        "post_logout_redirect_uri": settings.WAGTAIL_REDIRECT_URL
    }
    # The OIDC_STORE_ID_TOKEN setting must be set to true if we want
    # to be able to read
    # it from the session.
    if "oidc_id_token" in request.session:
        parameters["id_token_hint"] = request.session["oidc_id_token"]

    redirect_url = settings.OIDC_OP_LOGOUT_URL + "?" + urlencode(
        parameters, doseq=True)
    return redirect_url


def provider_login_url(USE_OIDC_AUTHENTICATION):
    if USE_OIDC_AUTHENTICATION:
        return 'oidc_authentication_init'
    return 'molo.profiles:auth_login'


def provider_registration_url(USE_OIDC_AUTHENTICATION):
    if USE_OIDC_AUTHENTICATION:
        return "%s/registration/?theme=%s&hide=end-user&redirect_url=%s" % (
                settings.OIDC_OP,
                settings.THEME, settings.WAGTAIL_REDIRECT_URL)
    return 'molo.profiles:user_register'
