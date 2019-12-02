import re
import mimetypes
from copy import copy

from django.urls import reverse
from django.utils.timezone import timedelta
from django.template import Library
from django.conf import settings

from wagtail.core.rich_text import RichText

from gem.constants import GENDER
from gem.models import GemTextBanner

from molo.forms.models import FormsIndexPage, MoloFormPage
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
def content_is(page, title):
    if page.title.lower() == title.lower():
        return True
    else:
        if hasattr(page.specific, 'translated_pages'):
            for translation in page.specific.translated_pages.all():
                if translation.title.lower() == title.lower():
                    return True
    return False


@register.filter
def is_content(page, content):
    return page.is_content_page(content)


@register.filter()
def parent_section_depth(page, depth):
    return page.get_top_level_parent(depth=depth)


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
    is_str = isinstance(value, str) and len(value) > max_length
    is_rt = isinstance(
        value, RichText) and len(value.__str__()) > max_length

    if is_rt:
        value = value.__str__()

    if is_str or is_rt:
        truncd_val = value[:max_length]
        if value[max_length] != ' ':
            truncd_val = truncd_val[:truncd_val.rfind(' ')]

        return truncd_val + '...'
    return value


@register.inclusion_tag(
    'core/tags/media_listing_homepage.html',
    takes_context=True
)
def media_listing_homepage(context):
    return {
        'media': MoloMedia.objects.filter(feature_in_homepage=True),
        'request': context['request'],
        'is_via_freebasics': context['is_via_freebasics'],

    }


@register.simple_tag()
def oidc_logout_url():
    return settings.LOGOUT_URL


@register.filter
def seconds_to_time(val):
    """val is in seconds should return hh:mm:ss"""
    if isinstance(val, int):
        time = str(timedelta(seconds=val))
        for zero in re.findall(r'^0:', time):
            time = time.replace(zero, '')
        return time
    return ''


@register.filter
def mimetype(file):
    """ return mime type of file else a blank string"""
    if file and file.url:
        return mimetypes.guess_type(file.url, strict=True)[0]
    return ''


@register.inclusion_tag('forms/contact_forms_list.html', takes_context=True)
def contact_forms_list(context):
    context = copy(context)
    locale_code = context.get('locale_code')
    main = context['request'].site.root_page
    page = FormsIndexPage.objects.child_of(main).live().first()
    if page:
        forms = (
            MoloFormPage.objects.descendant_of(page).filter(
                language__is_main_language=True,
                contact_form=True).specific())
    else:
        forms = MoloFormPage.objects.none()
    context.update({
        'forms': get_pages(context, forms, locale_code)
    })
    return context
