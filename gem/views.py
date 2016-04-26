from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from molo.commenting.models import MoloComment
from molo.core.models import ArticlePage
from wagtail.wagtailsearch.models import Query

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect

from molo.profiles.views import RegistrationView
from forms import GemRegistrationForm


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
    title = "GEM RSS Feed"
    link = "/gem-rss-feed/"
    description = "GEM RSS Feed"

    def items(self):
        return ArticlePage.objects.filter(featured_in_homepage=True)

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.subtitle
