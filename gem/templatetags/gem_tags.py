from django.template import Library
from django.conf import settings

register = Library()


@register.simple_tag()
def get_site_static_prefix():
    return settings.SITE_STATIC_PREFIX
