from django.db import models
from django.db.models import Q
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import InlinePanel, FieldPanel
from wagtail.wagtailcore.fields import StreamField

from wagtail_personalisation.adapters import get_segment_adapter
from wagtailsurveys.models import AbstractFormField

from molo.surveys.models import MoloSurveyPage, SurveysIndexPage

from .rules import ProfileDataRule, SurveySubmissionDataRule, \
    GroupMembershipRule, CommentDataRule


# Force current index page to display our personalised survey
SurveysIndexPage.subpage_types.append('personalise.PersonalisableSurvey')


def get_personalisable_survey_content_panels():
    """
    Replace panel for "survey_form_fields" with
    panel pointing to the custom form field model.
    """
    panels = [
        FieldPanel('segment')
    ]

    for panel in MoloSurveyPage.content_panels:
        if isinstance(panel, InlinePanel) and \
                panel.relation_name == 'survey_form_fields':
            panel = InlinePanel('personalisable_survey_form_fields',
                                label=_('personalisable form fields'))
        panels.append(panel)

    return panels


class PersonalisableSurvey(MoloSurveyPage):
    """
    Survey page that enables form fields to be segmented with
    wagtail-personalisation.
    """
    segment = models.ForeignKey('wagtail_personalisation.Segment',
                                on_delete=models.SET_NULL, blank=True,
                                null=True,
                                help_text=_(
                                    'Leave it empty to show this survey'
                                    'to every user.'))
    content_panels = get_personalisable_survey_content_panels()
    template = MoloSurveyPage.template

    class Meta:
        verbose_name = _('personalisable survey')

    def get_form_fields(self):
        """Get form fields for particular segments."""
        # Get only segmented form fields if serve() has been called
        # (because the page is being seen by user on the front-end)
        if hasattr(self, 'request'):
            user_segments_ids = [s.id for s in get_segment_adapter(
                self.request).get_segments()]

            return self.personalisable_survey_form_fields.filter(
                Q(segment=None) | Q(segment_id__in=user_segments_ids)
            )

        # Return all form fields if there's no request passed
        # (used on the admin site so serve() will not be called).
        return self.personalisable_survey_form_fields \
                   .select_related('segment')

    def get_data_fields(self):
        """
        Get survey's form field's labels with segment names
        if there's one associated.
        """
        data_fields = [
            ('created_at', _('Submission Date')),
        ]

        # Add segment name to a field label if it is segmented.
        for field in self.get_form_fields():
            label = field.label

            if field.segment:
                label = '%s (%s)' % (label, field.segment.name)

            data_fields.append((field.clean_name, label))

        return data_fields

    def serve(self, request, *args, **kwargs):
        # We need request data in self.get_form_fields() to perform
        # segmentation.
        # TODO(tmkn): This is quite hacky, need to come up with better solution
        self.request = request

        # Check whether it is segmented and raise 404 if segments do not match
        if self.segment_id and get_segment_adapter(request).get_segment_by_id(
                self.segment_id) is None:
            raise Http404("Survey does not match your segments.")

        return super(PersonalisableSurvey, self).serve(
            request, *args, **kwargs)


class PersonalisableSurveyFormField(AbstractFormField):
    """
    Form field that has a segment assigned.
    """
    page = ParentalKey(PersonalisableSurvey, on_delete=models.CASCADE,
                       related_name='personalisable_survey_form_fields')
    segment = models.ForeignKey(
        'wagtail_personalisation.Segment',
        on_delete=models.PROTECT, blank=True, null=True,
        help_text=_('Leave it empty to show this field to every user.'))

    panels = [
        FieldPanel('segment')
    ] + AbstractFormField.panels

    def __str__(self):
        return '%s - %s' % (self.page, self.label)

    class Meta:
        verbose_name = _('personalisable form field')
