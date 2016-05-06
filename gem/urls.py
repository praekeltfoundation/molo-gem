import os

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

from gem.views import search, report_response, GemRegistrationView, \
    GemRssFeed, GemAtomFeed, GemForgotPasswordView, GemResetPasswordView

urlpatterns = patterns(
    '',
    url(r'^django-admin/', include(admin.site.urls)),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^profiles/register/$',
        GemRegistrationView.as_view(), name='user_register'),
    url(r'^profiles/forgot_password/$',
        GemForgotPasswordView.as_view(), name='forgot_password'),
    url(r'^profiles/reset_password/$',
        GemResetPasswordView.as_view(), name='reset_password'),

    url(r'^profiles/',
        include('molo.profiles.urls',
                namespace='molo.profiles',
                app_name='molo.profiles')),

    url(r'^comments/', include('molo.commenting.urls')),

    url(r'^commenting/',
        include('molo.commenting.urls',
                namespace='molo.commenting',
                app_name='molo.commenting')),

    url(r'^comments/reported/(?P<comment_pk>\d+)/$',
        report_response, name='report_response'),

    url(r'^yourwords/',
        include('molo.yourwords.urls',
                namespace='molo.yourwords',
                app_name='molo.yourwords')),

    url(r'^feed/rss/$', GemRssFeed(), name='feed_rss'),
    url(r'^feed/atom/$', GemAtomFeed(), name='feed_atom'),

    url(r'^servicedirectory/', include('molo.servicedirectory.urls')),

    url(r'search/$', search, name='search'),

    url(r'^polls/', include('molo.polls.urls',
                            namespace='molo.polls',
                            app_name='molo.polls')),

    url(r'', include('molo.core.urls')),
    url(r'', include(wagtail_urls)),
)


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL + 'images/',
        document_root=os.path.join(settings.MEDIA_ROOT, 'images'))
