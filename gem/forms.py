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

    security_question_1_answer = forms.CharField(
        label=_("Answer to Security Question 1"),
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=128,
            )
        ),
    )

    security_question_2_answer = forms.CharField(
        label=_("Answer to Security Question 2"),
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=128,
            )
        ),
    )
