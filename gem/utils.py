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
    site = request.site
    if not hasattr(site, "oidcsettings"):
        raise RuntimeError("Site {} has no settings configured.".format(site))
    parameters = {
        "post_logout_redirect_uri": site.oidc_settings.wagtail_redirect_url
    }
    # The OIDC_STORE_ID_TOKEN setting must be set to true if we want
    # to be able to read
    # it from the session.
    if "oidc_id_token" in request.session:
        parameters["id_token_hint"] = request.session["oidc_id_token"]

    redirect_url = settings.OIDC_OP_LOGOUT_URL + "?" + urlencode(
        parameters, doseq=True)
    return redirect_url
