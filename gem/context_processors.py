from django.conf import settings
from molo.profiles.forms import RegistrationForm
from molo.profiles.forms import EditProfileForm, ProfilePasswordChangeForm


def default_forms(request):
    return {
        'registration_form': RegistrationForm(),
        'edit_profile_form': EditProfileForm(),
        'password_change_form': ProfilePasswordChangeForm()
    }


def add_tag_manager_account(request):
    return {
        'GOOGLE_TAG_MANAGER_ACCOUNT': settings.GOOGLE_TAG_MANAGER_ACCOUNT
    }
