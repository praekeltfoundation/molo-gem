import re

from django.core.urlresolvers import reverse
from django.template import Library
from django.conf import settings

from gem.constants import GENDER
from gem.models import GemTextBanner
from molo.core.models import MoloMedia
from molo.core.templatetags.core_tags import get_pages
register = Library()


@register.simple_tag(takes_context=True)
def bbm_share_url(context):
    req = context['request']
    uri = reverse(
        'bbm_redirect',
        kwargs={'redirect_path': req.get_full_path().lstrip('/')},
    )
    return req.build_absolute_uri(uri)


@register.simple_tag()
def get_site_static_prefix():
    return settings.SITE_STATIC_PREFIX


@register.filter('fieldtype')
def fieldtype(field):
    return field.field.widget.__class__.__name__


@register.filter(name='idfromlabel')
def idfromlabel(label):
    '''
    return a string that contains only alphanuumeric characters from
    original string with the prefix 'id_'
    '''
    return "id_{}".format(re.sub(r'([^\w]|_)+', '', label.lower()))


@register.filter
def gender_display(gender):
    if gender in ['m', 'f', '-']:
        return GENDER[gender]
    return None


@register.inclusion_tag('core/tags/bannerpages.html', takes_context=True)
def gembannerpages(context):
    request = context['request']
    locale = context.get('locale_code')
    pages = []
    if request.site:
        pages = request.site.root_page.specific.bannerpages().exact_type(
            GemTextBanner)
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


@register.inclusion_tag(
    'gem/tags/media_listing_homepage.html',
    takes_context=True
)
def media_listing_homepage(context):
    return {
        'media': MoloMedia.objects.filter(feature_in_homepage=True),
        'request': context['request'],
        'is_via_freebasics': context['is_via_freebasics'],

    }


@register.simple_tag()
def main_nav():
    return settings.LOGOUT_URL
