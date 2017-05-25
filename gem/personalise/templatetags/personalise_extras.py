from django import template

register = template.Library()

@register.simple_tag
def filter_surveys_by_segments(surveys, request):
    """Filter out surveys not in user's segments."""
    user_segments_ids = [int(s.get('id')) for s in request.session['segments']]
    filetered_surveys = []

    for survey in surveys:
        if not survey.segment_id:
            filetered_surveys.append(survey)
        elif survey.segment_id in user_segments_ids:
            filetered_surveys.append(survey)

    return filetered_surveys
