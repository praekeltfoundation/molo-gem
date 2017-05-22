import datetime
import re

from django.conf import settings
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

from wagtail.wagtailadmin.edit_handlers import FieldPanel

from personalisation.rules import AbstractBaseRule


PERSONALISATION_PROFILE_DATA_FIELDS = [
    '{}__date_joined'.format(settings.AUTH_USER_MODEL),
    'profiles.UserProfile__date_of_birth',
    'gem.GemUserProfile__gender'
]


def get_field_choices_for_profile_data_personalisation(fields):
    """
    Get a tuple of choices for profile fields personaliastion out of
    a list of specified fields in the "app.Model__field" format,
    e.g. "auth.User__date_joined".
    """
    choices = []

    for model in set([apps.get_model(f.split(LOOKUP_SEP, 1)[0]) for f in fields]):
        model_verbose = capfirst(model._meta.verbose_name)
        base_accessor = model._meta.label + LOOKUP_SEP
        for field in model._meta.get_fields():
            accessor = base_accessor + field.name
            if accessor in fields:
                choices.append((accessor, '%s - %s' % (model_verbose,
                                                       capfirst(field.verbose_name))))

    return choices

class ProfileDataRule(AbstractBaseRule):
    """
    Segmentation rule for wagtail-personalisation that evaluates data associated
    with user profile and related models.
    """
    LESS_THAN = 'lt'
    LESS_THAN_OR_EQUAL = 'lte'
    GREATER_THAN = 'gt'
    GREATER_THAN_OR_EQUAL = 'gte'
    EQUAL = 'eq'
    NOT_EQUAL = 'neq'

    OLDER_THAN = 'ol'
    OLDER_THAN_OR_EQUAL = 'ole'
    YOUNGER_THAN = 'yg'
    YOUNGER_THAN_OR_EQUAL = 'yge'
    OF_AGE = 'eqa'

    REGEX = 'reg'

    AGE_OPERATORS = (OLDER_THAN, OLDER_THAN_OR_EQUAL, YOUNGER_THAN,
                     YOUNGER_THAN_OR_EQUAL, OF_AGE)

    OPERATOR_CHOICES = (
        (LESS_THAN, _('Less than')),
        (LESS_THAN_OR_EQUAL, _('Less than or equal')),
        (GREATER_THAN, _('Greater than')),
        (GREATER_THAN_OR_EQUAL, _('Greater than or equal')),
        (EQUAL, _('Equal')),
        (NOT_EQUAL, _('Not equal')),
        (OLDER_THAN, _('Older than')),
        (OLDER_THAN_OR_EQUAL, _('Older than or equal')),
        (YOUNGER_THAN, _('Younger than')),
        (YOUNGER_THAN_OR_EQUAL, _('Younger than or equal')),
        (OF_AGE, _('Of age')),
        (REGEX, _('Regex')),
    )

    field = models.CharField(max_length=255)
    operator = models.CharField(max_length=3, choices=OPERATOR_CHOICES,
                                default=EQUAL)
    value = models.CharField(max_length=255)

    panels = [
        FieldPanel('field'),
        FieldPanel('operator'),
        FieldPanel('value'),
    ]

    class Meta:
        verbose_name = _('Profile Data Rule')

    def __init__(self, *args, **kwargs):
        # Get field names for personalisation in the constructor since
        # they require the app registry to be ready.
        choices = get_field_choices_for_profile_data_personalisation(
            PERSONALISATION_PROFILE_DATA_FIELDS)
        self._meta.get_field('field').choices = choices

        super(ProfileDataRule, self).__init__(*args, **kwargs)

    def clean(self):
        # Deal with regular expression operator.
        if self.operator == self.REGEX:
            # Make sure value is a valid regular expression string.
            try:
                re.compile(self.value)
            except re.error as error:
                raise ValidationError({
                    'value': _('Regular expression error: %s') % (error,)
                })


        # Deal with age opeartors.
        elif self.operator in self.AGE_OPERATORS:
            # Works only on DateField.
            if not isinstance(self.get_related_field(), models.DateField):
                raise ValidationError({
                    'operator': _('You can choose age operators only on date '
                                  'and date-time fields.')
                })

            try:
                self.value = int(self.value)
            except ValueError:
                raise ValidationError({
                    'value': _('Value has to be a whole integer when using '
                               'age operators.')
                })
            else:
                if self.value < 0:
                    raise ValidationError({
                        'value': _('Value has to be non-negative since it '
                                   'represents age.')
                    })


        # Deal with normal operators.
        else:
            # Reassign all errors to the "value" field.
            try:
                self.get_related_field().clean(self.value, None)
            except ValidationError as error:
                raise ValidationError({'value': error})

    def get_related_model_and_field(self):
        """Get model and field instances from self.field."""
        model_name, field_name = self.field.split(LOOKUP_SEP, 1)
        model = apps.get_model(model_name)
        field = model._meta.get_field(field_name)

        return model, field

    def get_related_model(self):
        """Get model instance from self.field."""
        return self.get_related_model_and_field()[0]

    def get_related_field(self):
        """Get field instance from self.field."""
        return self.get_related_model_and_field()[1]

    def get_related_field_name(self):
        """Get field name from self.field."""
        return self.get_related_field().name

    def get_python_value(self):
        """Return self.value in its Python format."""
        # Treat self.value as age and return a whole integer.
        if self.operator in self.AGE_OPERATORS:
            return int(self.value)

        # Treat self.value as regex and return regex instance.
        if self.operator == self.REGEX:
            return re.compile(self.value)

        # Treat self.value as anything and return value in format specific
        # to the field in self.field.
        return self.get_related_field().to_python(self.value)

    def get_related_field_value(self, user):
        """
        Get value of a field in self.field. Any model in self.field has to have
        a direct relationship to the user model.
        """
        # Check whether we try to access the main user model, as opposed to
        # related models.
        if user._meta.model is self.get_related_model():
            return getattr(user, self.get_related_field_name())


        # Obtain user model's field name with relation to the related model
        # we need to access, e.g. GemUserProfile would be 'gem_profile'.
        for f in user._meta.get_fields():
            if f.related_model is self.get_related_model():
                instance = getattr(user, f.name)
                return getattr(instance, self.get_related_field_name())

        raise LookupError('Cannot find related model on user\'s model')

    def description(self):
        return {
            'title': _('Based on profile data'),
            'value': _('"%s" %s "%s"') % (
                self._get_FIELD_display(self._meta.get_field('field')),
                self.get_operator_display(),
                self.value
            )
        }

    def test_user(self, request):
        # Fail segmentation if user is not logged-in.
        if not request.user.is_authenticated():
            return False


        # Handy variables for comparisons.
        python_value = self.get_python_value()
        related_field_value = self.get_related_field_value(user=request.user)


        # Handle null (None) values in the related field
        if related_field_value is None:
            # If that value is None, we should fail it unless "not equals"
            # operator is set
            return self.operator == self.NOT_EQUAL


        # Deal with regex operator.
        if self.operator == self.REGEX:
            return python_value.match(str(related_field_value)) is not None


        # Deal with age operators.
        if self.operator in self.AGE_OPERATORS:
            # Convert datetime to date if it is a datetime.
            dob = related_field_value.date() if isinstance(related_field_value,
                                                           datetime.datetime) \
                                             else related_field_value

            # Field has to be a date.
            if not isinstance(dob, datetime.date):
                raise RuntimeError('{} is not a date or datetime instance.')

            # Calculate age.
            today = timezone.now().date()
            age = int((today - dob).days / 365.25)

            # Compare age.
            if self.operator == self.OF_AGE:
                return age == python_value

            if self.operator == self.YOUNGER_THAN:
                return age < python_value

            if self.operator == self.YOUNGER_THAN_OR_EQUAL:
                return age <= python_value

            if self.operator == self.OLDER_THAN:
                return age > python_value

            if self.operator == self.OLDER_THAN_OR_EQUAL:
                return age >= python_value


        # Deal with comparison operators.
        if self.operator == self.LESS_THAN:
            return related_field_value < python_value

        if self.operator == self.LESS_THAN_OR_EQUAL:
            return related_field_value <= python_value

        if self.operator == self.GREATER_THAN:
            return related_field_value > python_value

        if self.operator == self.GREATER_THAN_OR_EQUAL:
            return related_field_value >= python_value

        if self.operator == self.EQUAL:
            return related_field_value == python_value

        if self.operator == self.NOT_EQUAL:
            return related_field_value != python_value


        raise NotImplementedError('Operator "{}" not implemented on {}.'
                                  'test_user.'.format(self.operator,
                                                      type(self).__name__))
