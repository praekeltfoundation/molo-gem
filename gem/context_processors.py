from django.conf import settings
from django.core.urlresolvers import reverse


def detect_bbm(request):
    '''
    Detect whether a request has come from BBM. BBM directs users to a /bbm/
    endpoint which sets a cookie that we can check. Previously we did this
    using a bbm subdomain, but that is complex to maintain.

    FIXME: Remove hostname check when bbm subdomains for South Africa
    and Nigeria are no longer used.
    '''
    is_via_bbm = False

    if request.COOKIES.get('bbm', 'false') == 'true':
        is_via_bbm = True

    if 'bbm.' in request.get_host():
        is_via_bbm = True

    return {
        'is_via_bbm': is_via_bbm,
    }


def detect_freebasics(request):
    return {
        'is_via_freebasics':
            'Internet.org' in request.META.get('HTTP_VIA', '') or
            'InternetOrgApp' in request.META.get('HTTP_USER_AGENT', '') or
            'true' in request.META.get('HTTP_X_IORG_FBS', '')
    }


def compress_settings(request):
    REGISTRATION_URL = settings.REGISTRATION_URL
    EDIT_PROFILE_URL = settings.EDIT_PROFILE_URL
    VIEW_PROFILE_URL = settings.VIEW_PROFILE_URL

    if settings.USE_OIDC_AUTHENTICATION:
        site = request.site
        language = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
        if not hasattr(site, "oidcsettings"):
            raise RuntimeError(
                "Site {} has no settings configured.".format(site))

        oidc_settings = site.oidcsettings
        if oidc_settings:
            REGISTRATION_URL = (
                "%s/registration/?theme=%s&hide=end-user&redirect_uri=%s"
                "&client_id=%s&language=%s" % (
                    settings.OIDC_OP, settings.THEME,
                    request.site.root_url
                    + reverse('oidc_authentication_init'),
                    oidc_settings.oidc_rp_client_id, language))
            VIEW_PROFILE_URL = (
                "%s/profile/edit/?theme=%s&redirect_uri=%s&client_id=%s"
                "&language=%s" % (
                    settings.OIDC_OP, settings.THEME,
                    oidc_settings.wagtail_redirect_url,
                    oidc_settings.oidc_rp_client_id, language))
            EDIT_PROFILE_URL = (
                "%s/profile/edit/?theme=%s&redirect_uri=%s&client_id=%s"
                "&language=%s" % (
                    settings.OIDC_OP, settings.THEME,
                    oidc_settings.wagtail_redirect_url,
                    oidc_settings.oidc_rp_client_id, language))

    return {
        'STATIC_URL': settings.STATIC_URL,
        'ENV': settings.ENV,
        'REGISTRATION_URL': REGISTRATION_URL,
        'EDIT_PROFILE_URL': EDIT_PROFILE_URL,
        'VIEW_PROFILE_URL': VIEW_PROFILE_URL,
        'LOGIN_URL': settings.LOGIN_URL,
        'LOGOUT_URL': settings.LOGOUT_URL,
    }
