from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django_comments.forms import CommentDetailsForm
from gem.models import GemSettings
from gem.settings import REGEX_PHONE, REGEX_EMAIL
from django.utils.feedgenerator import Atom1Feed

from molo.commenting.models import MoloComment
from molo.core.models import ArticlePage
from wagtail.wagtailcore.models import Site
from wagtail.wagtailsearch.models import Query

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.syndication.views import Feed
from django.http import HttpResponseRedirect

from molo.profiles.views import RegistrationView
from forms import GemRegistrationForm
from django import forms

import re


def search(request, results_per_page=10):
    search_query = request.GET.get('q', None)
    page = request.GET.get('p', 1)

    if search_query:
        results = ArticlePage.objects.live().search(search_query)
        Query.get(search_query).add_hit()
    else:
        results = ArticlePage.objects.none()

    paginator = Paginator(results, results_per_page)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search_results.html', {
        'search_query': search_query,
        'search_results': search_results,
        'results': results,
    })


def report_response(request, comment_pk):
    comment = MoloComment.objects.get(pk=comment_pk)

    return render(request, 'comments/report_response.html', {
        'article': comment.content_object,
    })


class GemRegistrationView(RegistrationView):
    form_class = GemRegistrationForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        gender = form.cleaned_data['gender']
        user = User.objects.create_user(username=username, password=password)
        user.gem_profile.gender = gender
        user.gem_profile.save()

        authed_user = authenticate(username=username, password=password)
        login(self.request, authed_user)
        return HttpResponseRedirect(form.cleaned_data.get('next', '/'))


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
    Check for email addresses and telephone numbers
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
        match = re.search(keyword.lower(), comment.lower())
        if match:
            raise forms.ValidationError(
                _(
                    'This comment has been removed as it contains profanity, '
                    'contact information or other inappropriate content. '
                )
            )

    return comment


CommentDetailsForm.clean_comment = clean_comment
