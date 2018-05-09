from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _


class ReportCommentForm(Form):
    CHOICES = (
        ('Spam', _('Spam')),
        ('Offensive Language', _('Offensive Language')),
        ('Bullying', _('Bullying')),
        ('Other', _('Other'))
    )

    report_reason = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHOICES
    )
