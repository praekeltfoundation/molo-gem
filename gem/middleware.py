import re
import uuid
import urllib
import structlog

from django.conf import settings
from django.http.response import Http404
from django.contrib.messages import warning
from django.utils.deprecation import MiddlewareMixin
from django.middleware.locale import LocaleMiddleware
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.utils.translation import get_language_from_request

from molo.core.utils import get_locale_code
from molo.core.middleware import MoloGoogleAnalyticsMiddleware
from molo.core.models import SiteSettings, ArticlePage, Languages, MoloPage
from molo.core.templatetags.core_tags import load_tags_for_article


class ForceDefaultLanguageMiddleware(MiddlewareMixin):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or
    cookies

    Should be installed *before* any middleware that
    checks request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
    """
    def process_request(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']


class GemLocaleMiddleware(LocaleMiddleware):
    def process_response(self, request, response):
        has_slug = len(request.path.split('/')) > 1
        slug = request.path.split('/')[-1]

        if has_slug and request.path[-1] == '/':
            slug = request.path.split('/')[-2]
        session_exists = request.COOKIES.get('django_language')
        if not session_exists and (has_slug and slug):
            page = MoloPage.objects.filter(slug=slug).first()
            if page:
                specific = getattr(page, 'specific', None)
                specific_language = specific and getattr(
                    page.specific, 'language', None)

                if specific_language:
                    response.set_cookie(
                        'django_language', page.specific.language.locale)

                elif hasattr(page, 'language'):
                    response.set_cookie(
                        'django_language', page.language.locale)
        return response


class LogHeaderInformationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        log = structlog.get_logger()
        log.msg(str(request.META))


class GemMoloGoogleAnalyticsMiddleware(MoloGoogleAnalyticsMiddleware):
    '''
    Submits GA tracking data to a local account or the additional account
    depending on the subdomain in the request

    TODO: Pull the submit_to_local_account and submit_to_global_account
    into the MoloGoogleAnalyticsMiddleware class and override
    submit_to_local_account
    '''

    def load_article_info(self, request):
        """get the tags in an article if the request is for an article page"""
        path = request.get_full_path()
        path_components = [component for component in path.split('/')
                           if component]
        site = request._wagtail_site
        article_info = {}
        try:
            page, args, kwargs = site.root_page.route(
                request,
                path_components)
            if issubclass(type(page.specific), ArticlePage):
                tags_str = ""
                main_lang = Languages.for_site(site).languages.filter(
                    is_main_language=True).first()
                locale_code = get_locale_code(
                    get_language_from_request(request))
                if main_lang.locale == locale_code:
                    article_info['cd5'] = page.specific.title
                else:
                    article_info['cd5'] = page.specific.get_main_language_page(
                    ).title
                qs = load_tags_for_article(
                    {'locale_code': 'en', 'request': request}, page)
                if qs:
                    for q in qs:
                        tags_str += "|" + q.title
                    article_info .update({'cd6': tags_str[1:]})
                    return article_info
        except Http404:
            return article_info
        return article_info

    def get_visitor_id(self, request):
        """Generate a visitor id for this hit.
        If there is a visitor id in the cookie, use that, otherwise
        use the guid if we have one, otherwise use a random number.
        """
        guid = request.META.get('HTTP_X_DCMGUID', '')
        cookie = request.COOKIES.get('__utmmobile')
        if cookie:
            return cookie
        if guid:
            # create the visitor id using the guid.
            cid = guid
        else:
            # otherwise this is a new user, create a new random id.
            cid = str(uuid.uuid4())
        return cid

    def submit_to_local_account(self, request, response, site_settings):
        custom_params = {}

        cd1 = self.get_visitor_id(request)
        custom_params.update({'cd1': cd1})
        if hasattr(request, 'user') and hasattr(request.user, 'profile')\
                and request.user.profile.uuid:
            custom_params.update({'cd2': request.user.profile.uuid})

        if hasattr(request, 'user') and request.user.is_authenticated:
            custom_params.update({'cd3': 'Registered'})
        else:
            custom_params.update({'cd3': 'Visitor'})

        article_info = self.load_article_info(request)
        custom_params.update(article_info)

        local_ga_account = site_settings.local_ga_tracking_code or \
            settings.GOOGLE_ANALYTICS.get('google_analytics_id')
        if local_ga_account:
            return self.submit_tracking(
                local_ga_account,
                request,
                response,
                custom_params)
        return response

    def submit_to_global_account(self, request, response, site_settings):
        custom_params = {}
        cd1 = self.get_visitor_id(request)
        custom_params.update({'cd1': cd1})
        if hasattr(request, 'user') and request.user.is_authenticated:
            custom_params.update({'cd3': 'Registered'})
        else:
            custom_params.update({'cd3': 'Visitor'})

        article_info = self.load_article_info(request)
        custom_params.update(article_info)

        if site_settings.global_ga_tracking_code:
            if hasattr(request, 'user') and hasattr(request.user, 'profile')\
                    and request.user.profile.uuid:
                custom_params.update({'cd2': request.user.profile.uuid})
            return self.submit_tracking(
                site_settings.global_ga_tracking_code,
                request,
                response,
                custom_params)
        return response

    def process_response(self, request, response):
        if hasattr(settings, 'GOOGLE_ANALYTICS_IGNORE_PATH'):
            exclude = [p for p in settings.GOOGLE_ANALYTICS_IGNORE_PATH
                       if request.path.startswith(p)]
            if any(exclude):
                return response
        # Only track 200 and 302 responses for current_site
        if not (response.status_code == 200 or response.status_code == 302):
            return response

        # exclude requests that contain sensitive sensitive information(email)
        if(request.get_full_path().find('/search/?q=') > -1):
            try:
                search_string = urllib.parse.unquote(
                    request.get_full_path().replace('/search/?q=', ''))
            except AttributeError:
                search_string = urllib.unquote(
                    request.get_full_path().replace('/search/?q=', ''))

            if re.match(r'[^@]+@[^@]+\.[^@]+', search_string):
                return response

        site = request._wagtail_site
        site_settings = SiteSettings.for_site(site)
        if site_settings.local_ga_tracking_code or \
                settings.GOOGLE_ANALYTICS.get('google_analytics_id'):
            response = self.submit_to_local_account(
                request, response, site_settings)
        if site_settings.global_ga_tracking_code:
            response = self.submit_to_global_account(
                request, response, site_settings)
        return response


class AdminSiteAdminMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated:
            is_superuser = request.user.is_superuser
            if not is_superuser and '/admin' in request.path:
                # determine user user.profile.admin_sites
                # perm denied if user is not related to admin_sites
                # redirect to default admin site (first) or home
                site = request._wagtail_site
                if site not in request.user.profile.admin_sites.all():
                    warning(
                        request,
                        _("You do not have the permissions to access {}."
                          .format(site)))
                    site = request.user.profile.admin_sites.first()
                    if site:
                        return HttpResponseRedirect(
                            redirect_to=site.hostname+'/admin/')
                    return HttpResponseRedirect(redirect_to='/')
