import os

from django.conf.urls import include, re_path
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
        re_path(r'^admin/login/', RedirectWithQueryStringView.as_view(
            pattern_name="oidc_authentication_init")),
    ]
elif settings.ENABLE_SSO:
    urlpatterns += [
        re_path(
            r'^admin/login/',
            cas_views.LoginView.as_view(), name='cas_ng_login'),

        re_path(
            r'^admin/logout/',
            cas_views.LogoutView.as_view(), name='cas_ng_logout'),

        re_path(
            r'^admin/callback/',
            cas_views.CallbackView.as_view(), name='cas_ng_callback'),
    ]

urlpatterns += [
    re_path(r'^oidc/', include('mozilla_django_oidc.urls')),
    re_path(r'^django-admin/', admin.site.urls),
    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'^robots\.txt$', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain')),
    re_path(r'^sitemap\.xml$', core_views.sitemap),
    re_path(r'^documents/', include(wagtaildocs_urls)),
    re_path(
        r'^manifest\.webapp$',
        KaiOSManifestView.as_view(), name='kaios_manifest'),

    re_path(
        r'^bbm/(?P<redirect_path>.*)$',
        BbmRedirect.as_view(), name='bbm_redirect'),

    re_path(r'', include('molo.pwa.urls')),
    re_path(
        r'^profiles/register/$',
        GemRegistrationView.as_view(), name='user_register'),

    re_path(
        r'^profiles/register/done/',
        GemRegistrationDoneView.as_view(), name='registration_done'),

    re_path(
        r'^profiles/forgot_password/$',
        ForgotPasswordView.as_view(), name='forgot_password'),

    re_path(
        r'^profiles/reset_password/$',
        ResetPasswordView.as_view(), name='reset_password'),

    re_path(
        r'^profiles/reset-success/$',
        TemplateView.as_view(
            template_name='profiles/reset_password_success.html'),
        name='reset_password_success'),

    re_path(
        r'^profiles/edit/myprofile/$',
        login_required(GemEditProfileView.as_view()),
        name='edit_my_profile'),

    re_path(
        r'^profiles/',
        include(
            ('molo.profiles.urls', 'molo.profiles'),
        )),

    re_path(
        r'^commenting/',
        include(
            ('molo.commenting.urls', 'molo.commenting'),
        )),

    re_path(
        r'^comments/reported/(?P<comment_pk>\d+)/$',
        report_response, name='report_response'),

    re_path(
        r'^comments/report_comment/(?P<comment_pk>\d+)/$',
        login_required(ReportCommentView.as_view()), name='report_comment'),

    re_path(
        r'^comments/already_reported/(?P<comment_pk>\d+)/$',
        login_required(AlreadyReportedCommentView.as_view()),
        name='already_reported'),

    re_path(r'', include('django_comments.urls')),

    re_path(
        r'^forms/',
        include(
            ('molo.forms.urls', 'molo.forms'),
        )),

    re_path(r'^feed/rss/$', GemRssFeed(), name='feed_rss'),
    re_path(r'^feed/atom/$', GemAtomFeed(), name='feed_atom'),

    re_path(r'^servicedirectory/', include('molo.servicedirectory.urls')),

    re_path(r"^mote/", include(("mote.urls", "mote"))),
    re_path(r'', include('molo.core.urls')),
    re_path(
        r'^home-index/$',
        core_views.home_index,
        name='home_index'
    ),
    re_path(
        r'^home-more/$',
        core_views.home_more,
        name='home_more'
    ),
    re_path(
        r'^section-index/$',
        core_views.section_index,
        name='section_index'
    ),
    re_path(
        r'^reaction/(?P<article_slug>[0-9A-Za-z_\-]+)/'
        '(?P<question_id>\d+)/vote/$',
        core_views.ReactionQuestionChoiceView.as_view(),
        name='reaction-vote'),

    re_path(r'', include(wagtail_urls)),
    re_path(r'', include('django_prometheus.urls')),
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
        re_path(
            r'^health/$',
            core_views.health,
        ),
        re_path(r'', MaintenanceView.as_view()),
    ]
