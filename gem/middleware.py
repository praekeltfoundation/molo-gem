from bs4 import BeautifulSoup
from django.conf import settings
from google_analytics.utils import build_ga_params, set_cookie
from google_analytics.tasks import send_ga_tracking

from molo.core.models import SiteSettings

from gem.models import GemSettings


class ForceDefaultLanguageMiddleware(object):
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


class LogHeaderInformationMiddleware(object):

    def process_request(self, request):
        print '---------- Header Dump -------------'
        print request.META.items()


class GemMoloGoogleAnalyticsMiddleware(object):
    """Uses GA IDs stored in Wagtail to track pageviews using celery"""
    def submit_tracking(self, account, request, response):
        try:
            title = BeautifulSoup(
                response.content, "html.parser"
            ).html.head.title.text.encode('utf-8')
        except:
            title = None

        path = request.get_full_path()
        referer = request.META.get('HTTP_REFERER', '')
        params = build_ga_params(
            request, account, path=path, referer=referer, title=title)
        response = set_cookie(params, response)
        send_ga_tracking.delay(params)
        return response

    def process_response(self, request, response):
        if hasattr(settings, 'GOOGLE_ANALYTICS_IGNORE_PATH'):
            exclude = [p for p in settings.GOOGLE_ANALYTICS_IGNORE_PATH
                       if request.path.startswith(p)]
            if any(exclude):
                return response

        # Only track 200 and 302 responses for request.site
        if not (response.status_code == 200 or response.status_code == 302):
            return response

        site_settings = SiteSettings.for_site(request.site)
        gem_site_settings = GemSettings.for_site(request.site)

        if (request.get_host().split(".")[0] == 'bbm' and
            gem_site_settings.bbm_ga_account):
            local_ga_account = gem_site_settings.bbm_ga_account
        else:
            local_ga_account = site_settings.local_ga_tracking_code or \
                settings.GOOGLE_ANALYTICS.get('google_analytics_id')

        if local_ga_account:
            response = self.submit_tracking(
                local_ga_account, request, response)

        if site_settings.global_ga_tracking_code:
            response = self.submit_tracking(
                site_settings.global_ga_tracking_code, request, response)

        return response
