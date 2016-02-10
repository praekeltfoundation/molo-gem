from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import ugettext as _

from molo.core.utils import generate_slug
from molo.core.models import PageTranslation, SiteLanguage

from wagtail.wagtailcore.models import Page


def locale_set(request, locale):
    request.session[LANGUAGE_SESSION_KEY] = locale
    return redirect('/')


def health(request):
    return HttpResponse(status=200)


def add_translation(request, page_id, locale):
    def get_translated_page_for(page, locale):
        translated_page = None
        for t in page.translations.all():
            if (hasattr(t.translated_page.specific, 'language') and
                    t.translated_page.specific.language == locale):
                translated_page = t.translated_page.specific
                break
        return translated_page

    _page = get_object_or_404(Page, id=page_id)
    page = _page.specific

    if not hasattr(page, 'translations'):
        messages.add_message(
            request, messages.INFO, _('That page is not translatable.'))
        return redirect(reverse('wagtailadmin_home'))

    # redirect to edit page if translation already exists for this locale
    translated_page = get_translated_page_for(page, locale)
    if translated_page:
        return redirect(
            reverse('wagtailadmin_pages:edit', args=[translated_page.id]))

    # create translation and redirect to edit page
    new_slug = generate_slug(page.title)
    language = get_object_or_404(SiteLanguage, code=locale)
    translation = page.__class__(
        title=page.title, slug=new_slug, language=language)
    page.get_parent().add_child(instance=translation)
    translation.save_revision()
    PageTranslation.objects.create(page=page, translated_page=translation)

    return redirect(
        reverse('wagtailadmin_pages:edit', args=[translation.id]))
