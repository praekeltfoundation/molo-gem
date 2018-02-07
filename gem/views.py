import re

from django import forms
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from django_comments.forms import CommentDetailsForm

from gem.forms import (
    GemEditProfileForm,
    GemRegistrationForm,
    ReportCommentForm,
)
from gem.models import GemSettings, GemCommentReport
from gem.settings import REGEX_PHONE, REGEX_EMAIL

from molo.commenting.models import MoloComment

from molo.core.models import ArticlePage
from molo.profiles.views import RegistrationView, MyProfileEdit

from wagtail.wagtailcore.models import Site


def report_response(request, comment_pk):
    comment = MoloComment.objects.get(pk=comment_pk)

    return render(request, 'comments/report_response.html', {
        'article': comment.content_object,
    })


class GemRegistrationView(RegistrationView):
    form_class = GemRegistrationForm


class GemResetPasswordSuccessView(TemplateView):
    template_name = 'reset_password_success.html'


class GemEditProfileView(MyProfileEdit):
    form_class = GemEditProfileForm


class GemRssFeed(Feed):
    title = 'GEM Feed'
    description = 'GEM Feed'
    description_template = 'feed_description.html'

    def __call__(self, request, *args, **kwargs):
        self.base_url = '{0}://{1}'.format(request.scheme, request.get_host())
        return super(GemRssFeed, self).__call__(request, *args, **kwargs)

    def get_feed(self, obj, request):
        feed = super(GemRssFeed, self).get_feed(obj, request)
        # override the automatically discovered feed_url
        # TODO: consider overriding django.contrib.sites.get_current_site to
        # work with Wagtail sites - could remove the need for all the URL
        # overrides
        feed.feed['feed_url'] = self.base_url + request.path
        return feed

    def link(self):
        """
        Returns the URL of the HTML version of the feed as a normal Python
        string.
        """
        return self.base_url + '/'

    def items(self):
        return ArticlePage.objects.live().order_by(
            '-first_published_at'
        )[:20]

    def item_title(self, article_page):
        return article_page.title

    def item_link(self, article_page):
        return self.base_url + article_page.url

    def item_pubdate(self, article_page):
        return article_page.first_published_at

    def item_updateddate(self, article_page):
        return article_page.latest_revision_created_at

    def item_author_name(self, article_page):
        return article_page.owner.first_name if \
            article_page.owner and article_page.owner.first_name else 'Staff'


class GemAtomFeed(GemRssFeed):
    feed_type = Atom1Feed
    subtitle = GemRssFeed.description


# https://github.com/praekelt/yal-merge/blob/develop/yal/views.py#L711-L751
def clean_comment(self):
    """
    Check for email addresses, telephone numbers and any other keywords or
    patterns defined through GemSettings.
    """
    comment = self.cleaned_data['comment']

    site = Site.objects.get(is_default_site=True)
    settings = GemSettings.for_site(site)

    banned_list = [REGEX_EMAIL, REGEX_PHONE]

    banned_keywords_and_patterns = \
        settings.banned_keywords_and_patterns.split('\n') \
        if settings.banned_keywords_and_patterns else []

    banned_list += banned_keywords_and_patterns

    for keyword in banned_list:
        keyword = keyword.replace('\r', '')
        match = re.search(keyword, comment.lower())
        if match:
            raise forms.ValidationError(
                _(
                    'This comment has been removed as it contains profanity, '
                    'contact information or other inappropriate content. '
                )
            )

    return comment


CommentDetailsForm.clean_comment = clean_comment


class ReportCommentView(FormView):
    template_name = 'comments/report_comment.html'
    form_class = ReportCommentForm

    def render_to_response(self, context, **response_kwargs):
        comment = MoloComment.objects.get(pk=self.kwargs['comment_pk'])

        if comment.gemcommentreport_set.filter(
                user_id=self.request.user.id):
            return HttpResponseRedirect(
                reverse('already_reported',
                        args=(self.kwargs['comment_pk'],)
                        ))

        context.update({
            'article': comment.content_object,
        })

        return super(ReportCommentView, self).render_to_response(
            context, **response_kwargs
        )

    def form_valid(self, form):
        try:
            comment = MoloComment.objects.get(pk=self.kwargs['comment_pk'])
        except MoloComment.DoesNotExist:
            return HttpResponseForbidden()

        GemCommentReport.objects.create(
            comment=comment,
            user=self.request.user,
            reported_reason=form.cleaned_data['report_reason']
        )

        return HttpResponseRedirect(
            "{0}?next={1}".format(
                reverse(
                    'molo.commenting:molo-comments-report',
                    args=(self.kwargs['comment_pk'],)
                ),
                reverse(
                    'report_response', args=(self.kwargs['comment_pk'],))
            )
        )


class AlreadyReportedCommentView(TemplateView):
    template_name = 'comments/user_has_already_reported.html'

    def get(self, request, comment_pk):
        comment = MoloComment.objects.get(pk=self.kwargs['comment_pk'])

        return self.render_to_response({
            'article': comment.content_object
        })
