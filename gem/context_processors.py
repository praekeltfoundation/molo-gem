from django.conf import settings


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
    if settings.USE_OIDC_AUTHENTICATION:
        settings.REGISTRATION_URL = "%s/registration/?",
        "theme=%s}&hide=end-user&redirect_url=%s" % (
            settings.OIDC_OP, settings.THEME, settings.WAGTAIL_REDIRECT_URL)
    return {
        'STATIC_URL': settings.STATIC_URL,
        'ENV': settings.ENV,
        'REGISTRATION_URL': settings.REGISTRATION_URL,
        'LOGIN_URL': settings.LOGIN_URL,
    }
