import time
import re
import urllib
from django.utils.http import urlencode

from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.crypto import get_random_string

from mozilla_django_oidc.middleware import SessionRefresh
from mozilla_django_oidc.utils import import_from_settings, absolutify


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

        # exclude requests that contain sensitive sensitive information(email)
        if(request.get_full_path().find('/search/?q=') > -1):
            search_string = urllib.unquote(
                request.get_full_path().replace('/search/?q=', ''))
            if re.match(r'[^@]+@[^@]+\.[^@]+', search_string):
                return response

        site_settings = SiteSettings.for_site(request.site)
        response = self.submit_to_local_account(
            request, response, site_settings)
        response = self.submit_to_global_account(
            request, response, site_settings)
        return response


class CustomSessionRefresh(SessionRefresh):
    """
    Customised version of mozilla_django_oidc.middleware.SessionRefresh
    Allows for reading site-specific configuration based on the request.
    """

    def process_request(self, request):
        site = request.site
        if not hasattr(site, "oidcsettings"):
            raise RuntimeError(
                "Site {} has no settings configured.".format(site))

        if not self.is_refreshable_url(request):
            return

        expiration = request.session.get('oidc_id_token_expiration', 0)
        now = time.time()
        if expiration > now:
            # The id_token is still valid, so we don't have to do anything.
            return

        # The id_token has expired, so we have to re-authenticate silently.
        auth_url = import_from_settings('OIDC_OP_AUTHORIZATION_ENDPOINT')
        client_id = site.oidcsettings.oidc_rp_client_id
        state = get_random_string(import_from_settings('OIDC_STATE_SIZE', 32))

        # Build the parameters as if we were doing a real auth handoff, except
        # we also include prompt=none.
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': absolutify(
                request,
                reverse('oidc_authentication_callback')
            ),
            'state': state,
            'scope': site.oidcsettings.oidc_rp_scopes,
            'prompt': 'none',
        }

        if import_from_settings('OIDC_USE_NONCE', True):
            nonce = get_random_string(import_from_settings(
                'OIDC_NONCE_SIZE', 32))
            params.update({
                'nonce': nonce
            })
            request.session['oidc_nonce'] = nonce

        request.session['oidc_state'] = state
        request.session['oidc_login_next'] = request.get_full_path()

        query = urlencode(params)
        redirect_url = '{url}?{query}'.format(url=auth_url, query=query)
        if request.is_ajax():
            # Almost all XHR request handling in client-side code struggles
            # with redirects since redirecting to a page where the user
            # is supposed to do something is extremely unlikely to work
            # in an XHR request. Make a special response for these kinds
            # of requests.
            # The use of 403 Forbidden is to match the fact that this
            # middleware doesn't really want the user in if they don't
            # refresh their session.
            response = JsonResponse({'refresh_url': redirect_url}, status=403)
            response['refresh_url'] = redirect_url
            return response
        return HttpResponseRedirect(redirect_url)
