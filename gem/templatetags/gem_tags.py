from django.template import Library
from django.conf import settings

from gem.models import GemSettings

register = Library()


@register.simple_tag()
def get_site_static_prefix():
    return settings.SITE_STATIC_PREFIX


@register.filter()
def get_bbm_app_id(request):
    return GemSettings.for_site(request.site).bbm_app_id


@register.filter('fieldtype')
def fieldtype(field):
    return field.field.widget.__class__.__name__


@register.filter(name='smarttruncatechars')
def smart_truncate_chars(value, max_length):

    if len(value) > max_length:
        truncd_val = value[:max_length]
        if value[max_length] != ' ':
            truncd_val = truncd_val[:truncd_val.rfind(' ')]

        return truncd_val + '...'

    return value
