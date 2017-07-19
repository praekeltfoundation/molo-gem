import datetime
import json
import re

from django import forms
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.utils import six, timezone
from django.utils.functional import cached_property
from django.utils.text import capfirst, Truncator
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel

from molo.surveys.models import MoloSurveySubmission
from wagtail_personalisation.rules import AbstractBaseRule

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

    for model in set(
            [apps.get_model(f.split(LOOKUP_SEP, 1)[0]) for f in fields]):
        model_verbose = capfirst(model._meta.verbose_name)
        base_accessor = model._meta.label + LOOKUP_SEP
        for field in model._meta.get_fields():
            accessor = base_accessor + field.name
            if accessor in fields:
                choices.append((
                    accessor, '%s - %s' % (
                        model_verbose, capfirst(field.verbose_name))))

    return choices


class ProfileDataRule(AbstractBaseRule):
    """
    Segmentation rule for wagtail-personalisation that evaluates data
    associated with user profile and related models.
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
    operator = models.CharField(
        max_length=3, choices=OPERATOR_CHOICES,
        default=EQUAL,
        help_text=_('Age operators work only on dates, '
                    'please input the age you want to '
                    'compare in "value". '
                    'When using greater/less than on '
                    'text field, it would compare it by'
                    ' alphabetical order, where '
                    'dates are '
                    'compared to the specified date '
                    'by chronological order.'))
    value = models.CharField(
        max_length=255,
        help_text=_('If the selected field is a text field'
                    ' you can just input text. In '
                    'case of dates, please use format '
                    '"YYYY-MM-DD" and "YYYY-MM-DD HH:MM'
                    '" for date-times. For regex please '
                    'refer to the usage docs. If it is a '
                    'choice field, please input anything, '
                    'save and the error message displayed '
                    'below this field should guide '
                    'you with possible values.'))

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

        # If values are datetimes, make sure they are timezone aware
        # since it is not possible to compare naive and aware datetimes.
        if isinstance(python_value, datetime.datetime) \
                and timezone.is_naive(python_value):
            python_value = timezone.make_aware(python_value)

        if isinstance(related_field_value, datetime.datetime) \
                and timezone.is_naive(related_field_value):
            related_field_value = timezone.make_aware(related_field_value)

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
            dob = related_field_value.date() \
                if isinstance(related_field_value, datetime.datetime) \
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


class SurveySubmissionDataRule(AbstractBaseRule):
    EQUALS = 'eq'
    CONTAINS = 'in'

    OPERATOR_CHOICES = (
        (EQUALS, _('equals')),
        (CONTAINS, _('contains')),
    )

    survey = models.ForeignKey('PersonalisableSurvey',
                               verbose_name=_('survey'),
                               on_delete=models.CASCADE)
    field_name = models.CharField(
        _('field name'), max_length=255,
        help_text=_('Field\'s label in a lower-case '
                    'format with spaces replaced by '
                    'dashes. For possible choices '
                    'please input any text and save, '
                    'so it will be displayed in the '
                    'error messages below the '
                    'field.'))
    expected_response = models.CharField(
        _('expected response'), max_length=255,
        help_text=_('When comparing text values, please input text. Comparison'
                    ' on text is always case-insensitive. Multiple choice '
                    'values must be separated with commas.'))
    operator = models.CharField(
        _('operator'), max_length=3,
        choices=OPERATOR_CHOICES, default=CONTAINS,
        help_text=_('When using the "contains" operator'
                    ', "expected response" can '
                    'contain a small part of user\'s '
                    'response and it will be matched. '
                    '"Exact" would match responses '
                    'that are exactly the same as the '
                    '"expected response".'))

    panels = [
        PageChooserPanel('survey'),
        FieldPanel('field_name'),
        FieldPanel('operator'),
        FieldPanel('expected_response')
    ]

    class Meta:
        verbose_name = _('Survey submission rule')

    @cached_property
    def field_model(self):
        return apps.get_model('personalise', 'PersonalisableSurveyFormField')

    @property
    def survey_submission_model(self):
        return MoloSurveySubmission

    def get_expected_field(self):
        try:
            return self.survey.get_form().fields[self.field_name]
        except KeyError:
            raise self.field_model.DoesNotExist

    def get_expected_field_python_value(self, raise_exceptions=True):
        try:
            field = self.get_expected_field()
            self.expected_response = self.expected_response.strip()
            python_value = self.expected_response

            if isinstance(field, forms.MultipleChoiceField):
                # Eliminate duplicates, strip whitespaces,
                # eliminate empty values
                python_value = [v for v in {v.strip() for v in
                                            self.expected_response.split(',')}
                                if v]
                self.expected_response = ','.join(python_value)

                return python_value

            if isinstance(field, forms.BooleanField):
                if self.expected_response not in '01':
                    raise ValidationError({
                        'expected_response': [
                            _('Please use "0" or "1" on this field.')
                        ]
                    })
                return self.expected_response == '1'

            return python_value

        except (ValidationError, self.field_model.DoesNotExist):
            if raise_exceptions:
                raise

    def get_survey_submission_of_user(self, user):
        return self.survey_submission_model.objects.get(
            user=user, page_id=self.survey_id)

    def clean(self):
        # Do not call clean() if we have no survey set.
        if not self.survey_id:
            return

        # Make sure field name is a valid name
        field_names = [f.clean_name for f in self.survey.get_form_fields()]

        if self.field_name not in field_names:
            raise ValidationError({
                'field_name': [_('You need to choose valid field name out '
                                 'of: "%s".') % '", "'.join(field_names)]
            })

        # Convert value from the rule into Python value.
        python_value = self.get_expected_field_python_value()

        # Get this particular's field instance from the survey's form
        # so we can do validation on the value.
        try:
            self.get_expected_field().clean(python_value)
        except ValidationError as error:
            raise ValidationError({
                'expected_response': error
            })

    def test_user(self, request):
        # Must be logged-in to use this rule
        if not request.user.is_authenticated():
            return False

        try:
            survey_submission = self.get_survey_submission_of_user(
                request.user)
        except self.survey_submission_model.DoesNotExist:
            # No survey found so return false
            return False
        except self.survey_submission_model.MultipleObjectsReturned:
            # There should not be two survey submissions, but just in case
            # let's return false since we don't want to be guessing what user
            # meant in their response.
            return False

        # Get dict with user's survey submission to a particular question
        user_response = survey_submission.get_data().get(self.field_name)

        if not user_response:
            return False

        python_value = self.get_expected_field_python_value()

        # Compare user's response
        try:
            # Convert lists to sets for easy comparison
            if isinstance(python_value, list) \
                    and isinstance(user_response, list):
                if self.operator == self.CONTAINS:
                    return set(python_value).issubset(user_response)

                if self.operator == self.EQUALS:
                    return set(python_value) == set(user_response)

            if isinstance(python_value, six.string_types) \
                    and isinstance(user_response, six.string_types):
                if self.operator == self.CONTAINS:
                    return python_value.lower() in user_response.lower()

                return python_value.lower() == user_response.lower()

            return python_value == user_response
        except ValidationError:
            # In case survey has been modified and we cannot obtain Python
            # value, we want to return false.
            return False
        except self.field_model.DoesNotExist:
            # In case field does not longer exist on the survey
            # return false. We cannot compare its value if
            # we do not know its type (hence it needs to be on the survey).
            return False

    def description(self):
        try:
            field_name = self.get_expected_field().label
        except self.field_model.DoesNotExist:
            field_name = self.field_name

        return {
            'title': _('Based on survey submission of users'),
            'value': _('%s - %s  "%s"') % (
                self.survey,
                field_name,
                self.expected_response
            )
        }


class GroupMembershipRule(AbstractBaseRule):
    """wagtail-personalisation rule based on user's group membership."""
    group = models.ForeignKey('auth.Group', on_delete=models.PROTECT,
                              help_text=_('User must be part of this group to '
                                          'activate the rule.'))

    panels = [
        FieldPanel('group')
    ]

    class Meta:
        verbose_name = _('Group membership rule')

    def description(self):
        return {
            'title': _('Based on survey group memberships of users'),
            'value': _('Member of: "%s"') % self.group
        }

    def test_user(self, request):
        # Ignore not-logged in users
        if not request.user.is_authenticated():
            return False

        # Check whether user is part of a group
        return request.user.groups.filter(id=self.group_id).exists()


class CommentDataRule(AbstractBaseRule):
    EQUALS = 'eq'
    CONTAINS = 'in'

    OPERATOR_CHOICES = (
        (EQUALS, _('equals')),
        (CONTAINS, _('contains')),
    )
    expected_content = models.TextField(_('expected content'),
                                        help_text=_('Content that we want to '
                                                    'match in user\'s comment '
                                                    'data.'))
    operator = models.CharField(
        _('operator'), max_length=3,
        choices=OPERATOR_CHOICES, default=CONTAINS,
        help_text=_('"Equals" operator will match only '
                    'the exact content. "Contains" '
                    'operator matches a part of a '
                    'comment.'))

    panels = [
        FieldPanel('operator'),
        FieldPanel('expected_content')
    ]

    class Meta:
        verbose_name = _('comment data rule')

    def test_user(self, request):
        # Must be logged-in to use this rule
        if not request.user.is_authenticated():
            return False

        # Construct a queryset with user comments
        comments = request.user.comment_comments

        return comments.filter(
            **{'comment__i' + (
                'exact' if self.operator == self.EQUALS
                else 'contains'): self.expected_content}).exists()

    def description(self):
        return {
            'title': _('Based on comment submissions of users'),
            'value': _('"%s"') % (
                Truncator(self.expected_content).chars(20)
            )
        }
