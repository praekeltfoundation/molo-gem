from django.template import Library
from django.conf import settings

from gem.models import GemTextBanner
from molo.core.templatetags.core_tags import get_pages
register = Library()


@register.simple_tag()
def get_site_static_prefix():
    return settings.SITE_STATIC_PREFIX


@register.filter('fieldtype')
def fieldtype(field):
    return field.field.widget.__class__.__name__


@register.simple_tag(takes_context=True)
def is_via_freebasics(context):
    request = context['request']
    return ('Internet.org' in request.META.get('HTTP_VIA', '') or
            'InternetOrgApp' in request.META.get('HTTP_USER_AGENT', '') or
            'true' in request.META.get('HTTP_X_IORG_FBS', ''))


@register.inclusion_tag('core/tags/bannerpages.html', takes_context=True)
def gembannerpages(context):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        pages = request.site.root_page.specific.bannerpages().exact_type(
            GemTextBanner)
    else:
        pages = []
    return {
        'bannerpages': get_pages(context, pages, locale),
        'request': context['request'],
        'locale_code': locale,
    }


@register.filter(name='smarttruncatechars')
def smart_truncate_chars(value, max_length):

    if len(value) > max_length:
        truncd_val = value[:max_length]
        if value[max_length] != ' ':
            truncd_val = truncd_val[:truncd_val.rfind(' ')]

        return truncd_val + '...'

    return value
