from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from molo.core.models import SiteSettings
from molo.core.middleware import MoloGoogleAnalyticsMiddleware

from gem.models import GemSettings


class GemMoloGoogleAnalyticsMiddleware(MoloGoogleAnalyticsMiddleware):
    '''
    Submits GA tracking data to a local account or the additional account
    depending on the subdomain in the request or the bbm cookie.

    TODO: Pull the submit_to_local_account and submit_to_global_account
    into the MoloGoogleAnalyticsMiddleware class and override
    submit_to_local_account
    '''
    def submit_to_local_account(self, request, response, site_settings):
        gem_site_settings = GemSettings.for_site(request.site)
        bbm_ga_code = gem_site_settings.bbm_ga_tracking_code
        bbm_subdomain = gem_site_settings.bbm_ga_account_subdomain
        current_subdomain = request.get_host().split(".")[0]
        should_submit_to_bbm_account = False

        if current_subdomain == bbm_subdomain:
            should_submit_to_bbm_account = True

        if request.COOKIES.get('bbm', 'false') == 'true':
            should_submit_to_bbm_account = True

        if bbm_ga_code and should_submit_to_bbm_account:
            return self.submit_tracking(bbm_ga_code, request, response)
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


class AdminRedirectHTTPS(MiddlewareMixin):
    def process_request(self, request):
        if settings.ADMIN_REDIRECT_HTTPS is False:
            return None

        if request.scheme != 'http':
            return None

        host = request.get_host()
        path = request.path
        redirect_uri = 'https://{0}{1}'.format(host, path)

        if path.startswith('/admin') or path.startswith('/django-admin'):
            return redirect(redirect_uri)

        return None
