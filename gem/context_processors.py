from molo.profiles.forms import RegistrationForm
from molo.profiles.forms import EditProfileForm, ProfilePasswordChangeForm


def default_forms(request):
    return {
        'registration_form': RegistrationForm(),
        'edit_profile_form': EditProfileForm(),
        'password_change_form': ProfilePasswordChangeForm()
    }


def detect_freebasics(request):
    return {
        'is_via_freebasics':
            'internet.org' in request.META['HTTP_VIA'] or
            'InternetOrgApp' in request.META['HTTP_USER_AGENT'] or
            'HTTP_X_IORG_FBS' in request.META,
    }
