import os

from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django_cas_ng import views as cas_views

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls

from molo.core import views as core_views
from molo.profiles.views import ForgotPasswordView, ResetPasswordView
from wagtail.contrib.sitemaps import views as sitemap_views
from gem.views import (
    report_response, GemRegistrationView,
    GemRssFeed, GemAtomFeed,
    ReportCommentView, GemEditProfileView,
    AlreadyReportedCommentView, GemRegistrationDoneView,
    BbmRedirect, MaintenanceView, RedirectWithQueryStringView,
    KaiOSManifestView
)

urlpatterns = []
if settings.USE_OIDC_AUTHENTICATION:
    urlpatterns += [
        url(r'^admin/login/', RedirectWithQueryStringView.as_view(
            pattern_name="oidc_authentication_init")),
    ]
elif settings.ENABLE_SSO:
    urlpatterns += [
        url(r'^admin/login/', cas_views.login),
        url(r'^admin/logout/', cas_views.logout),
        url(r'^admin/callback/', cas_views.callback),
    ]

urlpatterns += [
    url(r'^oidc/', include('mozilla_django_oidc.urls')),
    url(r'^django-admin/', include(admin.site.urls)),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^robots\.txt$', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain')),
    url(r'^sitemap\.xml$', sitemap_views.sitemap),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^manifest\.webapp$', KaiOSManifestView.as_view(),
        name='kaios_manifest'),
    url(r'^bbm/(?P<redirect_path>.*)$',
        BbmRedirect.as_view(), name='bbm_redirect'),
    url(r'', include('molo.pwa.urls')),
    url(r'^profiles/register/$',
        GemRegistrationView.as_view(), name='user_register'),
    url(r'^profiles/register/done/',
        GemRegistrationDoneView.as_view(), name='registration_done'),
    url(r'^profiles/forgot_password/$',
        ForgotPasswordView.as_view(), name='forgot_password'),
    url(r'^profiles/reset_password/$',
        ResetPasswordView.as_view(), name='reset_password'),
    url(r'^profiles/reset-success/$',
        TemplateView.as_view(
            template_name='profiles/reset_password_success.html'
        ),
        name='reset_password_success'),
    url(r'^profiles/edit/myprofile/$',
        login_required(GemEditProfileView.as_view()),
        name='edit_my_profile'),
    url(r'^profiles/',
        include('molo.profiles.urls',
                namespace='molo.profiles',
                app_name='molo.profiles')),

    url(r'^commenting/',
        include('molo.commenting.urls',
                namespace='molo.commenting',
                app_name='molo.commenting')),

    url(r'^comments/reported/(?P<comment_pk>\d+)/$',
        report_response, name='report_response'),

    url(r'^comments/report_comment/(?P<comment_pk>\d+)/$',
        login_required(ReportCommentView.as_view()), name='report_comment'),

    url(r'^comments/already_reported/(?P<comment_pk>\d+)/$',
        login_required(AlreadyReportedCommentView.as_view()),
        name='already_reported'),

    url(r'', include('django_comments.urls')),
    url(r'^surveys/',
        include('molo.surveys.urls',
                namespace='molo.surveys',
                app_name='molo.surveys')),

    url(r'^yourwords/',
        include('molo.yourwords.urls',
                namespace='molo.yourwords',
                app_name='molo.yourwords')),

    url(r'^feed/rss/$', GemRssFeed(), name='feed_rss'),
    url(r'^feed/atom/$', GemAtomFeed(), name='feed_atom'),

    url(r'^servicedirectory/', include('molo.servicedirectory.urls',
        namespace='molo.servicedirectory')),

    url(r'^polls/', include('molo.polls.urls',
                            namespace='molo.polls',
                            app_name='molo.polls')),

    url(r"^mote/", include("mote.urls", namespace="mote")),
    url(r'', include('molo.core.urls')),
    url(
        r'^home-index/$',
        core_views.home_index,
        name='home_index'
    ),
    url(
        r'^home-more/$',
        core_views.home_more,
        name='home_more'
    ),
    url(
        r'^section-index/$',
        core_views.section_index,
        name='section_index'
    ),
    url(r'^reaction/(?P<article_slug>[0-9A-Za-z_\-]+)/'
        '(?P<question_id>\d+)/vote/$',
        core_views.ReactionQuestionChoiceView.as_view(),
        name='reaction-vote'),
    url(r'', include(wagtail_urls)),
    url(r'', include('django_prometheus.urls')),
]


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL + 'images/',
        document_root=os.path.join(settings.MEDIA_ROOT, 'images'))
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.MAINTENANCE_MODE:
    urlpatterns = [
        url(
            r'^health/$',
            core_views.health,
        ),
        url(r'', MaintenanceView.as_view()),
    ]
