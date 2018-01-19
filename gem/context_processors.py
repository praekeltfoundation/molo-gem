from django.conf import settings

from molo.profiles.forms import ProfilePasswordChangeForm


# TODO: this context processor generates the HTML for the password
# change form on every single request which is hugely inefficient.
# Once password_change_form is available for the viewprofile.html
# view we can remove this context processor.
def default_forms(request):
    return {
        'password_change_form': ProfilePasswordChangeForm()
    }


# TODO: remove this context processor
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
        'ENV': settings.ENV
    }
