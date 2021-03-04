from django.conf import settings


def detect_kaios(request):
    '''
    Detect whether a request has come from KaiOS.

    KaiOS requests will come from a subdomain prefix of kaios
    '''

    is_via_kaios = False

    if 'kaios.' in request.get_host():
        is_via_kaios = True
    return{
        'is_via_kaios': is_via_kaios
    }


def detect_freebasics(request):
    return {
        'is_via_freebasics':
            'Internet.org' in request.META.get('HTTP_VIA', '') or
            'InternetOrgApp' in request.META.get('HTTP_USER_AGENT', '') or
            'true' in request.META.get('HTTP_X_IORG_FBS', '')
    }


def compress_settings(request):
    return {
        'STATIC_URL': settings.STATIC_URL,
        'ENV': settings.ENV,
        'REGISTRATION_URL': settings.REGISTRATION_URL,
        'EDIT_PROFILE_URL': settings.EDIT_PROFILE_URL,
        'VIEW_PROFILE_URL': settings.VIEW_PROFILE_URL,
        'LOGIN_URL': settings.LOGIN_URL,
        'LOGOUT_URL': settings.LOGOUT_URL,
    }
