import os

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

from molo.core.views import ReactionQuestionChoiceView

from gem.views import report_response, GemRegistrationView, \
    GemRssFeed, GemAtomFeed, GemForgotPasswordView, GemResetPasswordView, \
    GemResetPasswordSuccessView, ReportCommentView, GemEditProfileView, \
    AlreadyReportedCommentView

# implement CAS URLs in a production setting
if settings.ENABLE_SSO:
    urlpatterns = patterns(
        '',
        url(r'^admin/login/', 'django_cas_ng.views.login'),
        url(r'^admin/logout/', 'django_cas_ng.views.logout'),
        url(r'^admin/callback/', 'django_cas_ng.views.callback'),
    )
else:
    urlpatterns = patterns('', )

urlpatterns += patterns(
    '',
    url(r'^django-admin/', include(admin.site.urls)),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^robots\.txt$', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain')),
    url(r'^sitemap\.xml$', 'wagtail.contrib.wagtailsitemaps.views.sitemap'),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'', include('molo.pwa.urls')),
    url(r'^profiles/register/$',
        GemRegistrationView.as_view(), name='user_register'),
    url(r'^profiles/forgot_password/$',
        GemForgotPasswordView.as_view(), name='forgot_password'),
    url(r'^profiles/reset_password/$',
        GemResetPasswordView.as_view(), name='reset_password'),
    url(r'^profiles/reset_password_success/$',
        GemResetPasswordSuccessView.as_view(), name='reset_password_success'),
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
        'molo.core.views.home_index',
        name='home_index'
    ),
    url(
        r'^home-more/$',
        'molo.core.views.home_more',
        name='home_more'
    ),
    url(
        r'^section-index/$',
        'molo.core.views.section_index',
        name='section_index'
    ),
    url(r'^reaction/(?P<article_slug>[0-9A-Za-z_\-]+)/'
        '(?P<question_id>\d+)/vote/$',
        ReactionQuestionChoiceView.as_view(),
        name='reaction-vote'),
    url(r'', include(wagtail_urls)),
    
)


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL + 'images/',
        document_root=os.path.join(settings.MEDIA_ROOT, 'images'))
