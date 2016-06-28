from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from gem.constants import GENDERS
from molo.profiles.forms import RegistrationForm, EditProfileForm
from molo.profiles.models import UserProfile


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


class GemForgotPasswordForm(Form):
    username = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Username"),
        error_messages={
            'invalid': _("This value must contain only letters, "
                         "numbers and underscores."),
        }
    )

    random_security_question_answer = forms.CharField(
        label=_("Answer to Security Question"),
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=128,
            )
        ),
    )


class GemResetPasswordForm(Form):
    username = forms.CharField(
        widget=forms.HiddenInput()
    )

    token = forms.CharField(
        widget=forms.HiddenInput()
    )

    password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("PIN")
    )

    confirm_password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("Confirm PIN")
    )


class GemEditProfileForm(EditProfileForm):
    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=GENDERS,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['alias', 'date_of_birth', 'mobile_number', 'gender']
