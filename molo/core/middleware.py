import uuid

from django.http import HttpResponseForbidden
from django.views.defaults import permission_denied

from django_cas_ng.middleware import CASMiddleware
from django_cas_ng.views import login as cas_login, logout as cas_logout
from django.contrib.auth.views import login, logout
from django.conf import settings
# test
from django.contrib.messages import get_messages
from django.utils.translation import activate

from google_analytics.utils import build_ga_params, set_cookie
from google_analytics.tasks import send_ga_tracking

from molo.core.models import SiteSettings


class MoloCASMiddleware(CASMiddleware):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func == login or view_func == logout:
            return None

        if view_func == cas_login:
            return cas_login(request, *view_args, **view_kwargs)
        elif view_func == cas_logout:
            return cas_logout(request, *view_args, **view_kwargs)

        if settings.CAS_ADMIN_PREFIX:
            if not request.path.startswith(settings.CAS_ADMIN_PREFIX):
                return None
        elif not view_func.__module__.startswith('django.contrib.admin.'):
            return None

        if request.user.is_authenticated():
            if request.user.is_staff:
                return None
            else:
                return permission_denied(request, 'error')
        return super(MoloCASMiddleware, self).process_view(
            request, view_func, view_args, view_kwargs)


class Custom403Middleware(object):
    """Catches 403 responses and raises 403 which allows for custom 403.html"""
    def process_response(self, request, response):
        storage = get_messages(request)
        for message in storage:
            pass
        if isinstance(response, HttpResponseForbidden):
            return permission_denied(request, 'error')
        return response


class ForceDefaultLanguageMiddleware(object):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via
    sessions or cookies

    Should be installed *before* any middleware that checks
    request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
    """
    def process_request(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']


class AdminLocaleMiddleware(object):
    """Ensures that the admin locale doesn't change with user selection"""
    def process_request(self, request):
        if request.path.startswith('/admin/') or \
           request.path.startswith('/django-admin/'):
            activate(settings.ADMIN_LANGUAGE_CODE)


class NoScriptGASessionMiddleware(object):
    """Store a unique session key for use with GTM"""
    def process_request(self, request):
        if 'MOLO_GA_SESSION_FOR_NOSCRIPT' not in request.session:
            request.session[
                'MOLO_GA_SESSION_FOR_NOSCRIPT'] = uuid.uuid4().hex


class MoloGoogleAnalyticsMiddleware(object):
    """Uses GA IDs stored in Wagtail to track pageviews using celery"""
    def submit_tracking(self, account, request, response):
        path = request.path
        referer = request.META.get('HTTP_REFERER', '')
        params = build_ga_params(request, account, path=path, referer=referer)
        response = set_cookie(params, response)
        send_ga_tracking.delay(params)
        return response

    def process_response(self, request, response):
        if hasattr(settings, 'GOOGLE_ANALYTICS_IGNORE_PATH'):
            exclude = [p for p in settings.GOOGLE_ANALYTICS_IGNORE_PATH
                       if request.path.startswith(p)]
            if any(exclude):
                return response

        site_settings = SiteSettings.for_site(request.site)
        local_ga_account = site_settings.local_ga_tracking_code or \
            settings.GOOGLE_ANALYTICS.get('google_analytics_id')

        if local_ga_account:
            response = self.submit_tracking(
                local_ga_account, request, response)

        if site_settings.global_ga_tracking_code:
            response = self.submit_tracking(
                site_settings.global_ga_tracking_code, request, response)

        return response
