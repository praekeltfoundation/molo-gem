from django import template

from wagtail_personalisation.adapters import get_segment_adapter

register = template.Library()


@register.simple_tag
def filter_surveys_by_segments(surveys, request):
    """Filter out surveys not in user's segments."""
    user_segments = get_segment_adapter(request).get_segments()
    user_segments_ids = [s.id for s in user_segments]
    filtered_surveys = []

    for survey in surveys:
        if not hasattr(survey, 'segment_id') or not survey.segment_id \
                or survey.segment_id in user_segments_ids:
            filtered_surveys.append(survey)

    return filtered_surveys
