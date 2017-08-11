from bs4 import BeautifulSoup
from django.conf import settings
from google_analytics.utils import build_ga_params, set_cookie
from google_analytics.tasks import send_ga_tracking

from molo.core.models import SiteSettings
from molo.core.middleware import MoloGoogleAnalyticsMiddleware

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


class GemMoloGoogleAnalyticsMiddleware(MoloGoogleAnalyticsMiddleware):
    '''
    Submits GA tracking data to a local account or the additional account
    depending on the subdomain in the request.

    TODO: Pull the submit_to_local_account and submit_to_global_account
    into the MoloGoogleAnalyticsMiddleware class and override
    submit_to_local_account
    '''
    def submit_to_local_account(self, request, response, site_settings):
        gem_site_settings = GemSettings.for_site(request.site)
        subdomain = request.get_host().split(".")[0]
        if (subdomain == gem_site_settings.extra_ga_account_subdomain and
                gem_site_settings.extra_ga_account):
                return self.submit_tracking(
                    gem_site_settings.extra_ga_account, request, response)
        else:
            local_ga_account = site_settings.local_ga_tracking_code or \
                settings.GOOGLE_ANALYTICS.get('google_analytics_id')
            if local_ga_account:
                return self.submit_tracking(
                    local_ga_account, request, response)
        return response

    def submit_to_global_account(self, request, response, site_settings):
        if site_settings.global_ga_tracking_code:
            return self.submit_tracking(
                site_settings.global_ga_tracking_code, request, response)
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
        response = self.submit_to_local_account(
            request, response, site_settings)
        response = self.submit_to_global_account(
            request, response, site_settings)

        return response
