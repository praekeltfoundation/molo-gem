import datetime
from collections import OrderedDict

from dateutils import relativedelta
from django import forms
from django.contrib.admin.filters import FieldListFilter
from django.utils.text import slugify
from django.utils.translation import ugettext as _


class UserListForm(forms.Form):
    def __init__(self, qs, *args, **kwargs):
        super(UserListForm, self).__init__(*args, **kwargs)
        for obj in qs:
            self.fields[str(obj.id)] = forms.BooleanField(
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'user'}),
            )


class FrontEndAgeToDateOfBirthFilter(FieldListFilter):
    template = 'admin/frontend_users_age_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_gte = '{}__gte'.format('age')
        self.lookup_kwarg_lte = '{}__lte'.format('age')

        super(FrontEndAgeToDateOfBirthFilter, self).__init__(
            field, request, params, model, model_admin, field_path
        )

        self.title = _('Age')

        self.form = self.get_form(request)

    def choices(self, cl):
        yield {
            'system_name': slugify(self.title),
            'query_string': cl.get_query_string(
                {}, remove=self.expected_parameters()
            )
        }

    def expected_parameters(self):
        return [self.lookup_kwarg_gte, self.lookup_kwarg_lte]

    def queryset(self, request, queryset):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                return queryset.filter(
                    **self._make_query_filter(request, validated_data)
                )
        return queryset

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        today = datetime.date.today()

        age_from = validated_data.get(self.lookup_kwarg_gte, None)
        age_to = validated_data.get(self.lookup_kwarg_lte, None)

        if age_from:
            start = '{0}__lte'.format(self.field_path)
            query_params[start] = today + relativedelta(years=-age_from)
        if age_to:
            end = '{0}__gte'.format(self.field_path)
            query_params[end] = today + relativedelta(years=-age_to)

        return query_params

    def get_form(self, request):
        form_class = self._get_form_class()
        return form_class(self.used_parameters)

    def _get_form_class(self):
        fields = self._get_form_fields()

        form_class = type(
            str('AgeRangeForm'),
            (forms.BaseForm,),
            {'base_fields': fields}
        )

        return form_class

    def _get_form_fields(self):
        return OrderedDict((
            (self.lookup_kwarg_gte, forms.IntegerField(
                label='',
                widget=forms.NumberInput(attrs={'placeholder': _('Age from')}),
                min_value=0,
                localize=True,
                required=False
            )),
            (self.lookup_kwarg_lte, forms.IntegerField(
                label='',
                widget=forms.NumberInput(attrs={'placeholder': _('Age to')}),
                min_value=0,
                localize=True,
                required=False
            )),
        ))
