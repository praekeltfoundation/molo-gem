import re
from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from gem.constants import GENDERS
from gem.settings import REGEX_EMAIL, REGEX_PHONE
from molo.profiles.forms import RegistrationForm, EditProfileForm


def validate_no_email_or_phone(input):
    regexes = [REGEX_EMAIL, REGEX_PHONE]
    for regex in regexes:
        match = re.search(regex, input)
        if match:
            return False

    return True


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

    def clean_username(self):
        username = super(GemRegistrationForm, self).clean_username()

        if not validate_no_email_or_phone(username):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid username. Please don't use"
                    " your email address or phone number in your username."
                )
            )

        return username


class GemEditProfileForm(EditProfileForm):
    def clean_alias(self):
        alias = self.cleaned_data['alias']

        if not validate_no_email_or_phone(alias):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid display name. Please don't"
                    " use your email address or phone number in your display"
                    " name."
                )
            )

        return alias


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
