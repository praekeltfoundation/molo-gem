from django import forms
from django.utils.translation import ugettext_lazy as _
from gem.constants import GENDERS
from molo.profiles.forms import RegistrationForm


class GemRegistrationForm(RegistrationForm):
    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=GENDERS,
        required=True
    )
