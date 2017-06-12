from django import template

from wagtail_personalisation.adapters import get_segment_adapter

register = template.Library()

@register.simple_tag
def filter_surveys_by_segments(surveys, request):
    """Filter out surveys not in user's segments."""
    user_segments = get_segment_adapter(request).get_segments()
    user_segments_ids = [s.id for s in user_segments]
    filetered_surveys = []

    for survey in surveys:
        if not survey.segment_id:
            filetered_surveys.append(survey)
        elif survey.segment_id in user_segments_ids:
            filetered_surveys.append(survey)

    return filetered_surveys
