import logging
import random
import re

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http.request import QueryDict
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from django_comments.forms import CommentDetailsForm

from forms import GemRegistrationForm, GemForgotPasswordForm, \
    GemResetPasswordForm

from gem.models import GemSettings
from gem.settings import REGEX_PHONE, REGEX_EMAIL

from molo.commenting.models import MoloComment
from molo.core.models import ArticlePage
from molo.profiles.views import RegistrationView

from wagtail.wagtailcore.models import Site
from wagtail.wagtailsearch.models import Query


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
        security_question_1_answer = form.cleaned_data[
            'security_question_1_answer'
        ]
        security_question_2_answer = form.cleaned_data[
            'security_question_2_answer'
        ]
        user = User.objects.create_user(username=username, password=password)
        user.gem_profile.gender = gender
        user.gem_profile.set_security_question_1_answer(
            security_question_1_answer
        )
        user.gem_profile.set_security_question_2_answer(
            security_question_2_answer
        )
        user.gem_profile.save()

        authed_user = authenticate(username=username, password=password)
        login(self.request, authed_user)
        return HttpResponseRedirect(form.cleaned_data.get('next', '/'))

    def render_to_response(self, context, **response_kwargs):
        context.update({
            'security_question_1': settings.SECURITY_QUESTION_1,
            'security_question_2': settings.SECURITY_QUESTION_2
        })
        return super(GemRegistrationView, self).render_to_response(
            context, **response_kwargs
        )


class GemForgotPasswordView(FormView):
    form_class = GemForgotPasswordForm
    template_name = 'forgot_password.html'

    security_questions = [
        settings.SECURITY_QUESTION_1, settings.SECURITY_QUESTION_2
    ]

    def form_valid(self, form):
        if 'random_security_question_idx' not in self.request.session:
            # the session expired between the time that the form was loaded
            # and submitted, restart the process
            return HttpResponseRedirect(reverse('forgot_password'))

        if 'forgot_password_attempts' not in self.request.session:
            self.request.session['forgot_password_attempts'] = 0

        if self.request.session['forgot_password_attempts'] >= 5:
            # GEM-195 implemented a 10 min session timeout, so effectively
            # the user can only try again once their anonymous session expires.
            # If they make another request within the 10 min time window the
            # expiration will be reset to 10 mins in the future.
            # This is obviously not bulletproof as an attacker could simply
            # not send the session cookie to circumvent this.
            form.add_error(None,
                           _('Too many attempts. Please try again later.'))
            return self.render_to_response({'form': form})

        username = form.cleaned_data['username']
        random_security_question_idx = self.request.session[
            'random_security_question_idx'
        ]
        random_security_question_answer = form.cleaned_data[
            'random_security_question_answer'
        ]

        # TODO: consider moving these checks to GemForgotPasswordForm.clean()
        # see django.contrib.auth.forms.AuthenticationForm for reference
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            self.request.session['forgot_password_attempts'] += 1
            form.add_error('username',
                           _('The username that you entered appears to be '
                             'invalid. Please try again.'))
            return self.render_to_response({'form': form})

        if not user.is_active:
            form.add_error('username', 'This account is inactive.')
            return self.render_to_response({'form': form})

        is_answer_correct = False
        if random_security_question_idx == 0:
            is_answer_correct = \
                user.gem_profile.check_security_question_1_answer(
                    random_security_question_answer
                )
        elif random_security_question_idx == 1:
            is_answer_correct = \
                user.gem_profile.check_security_question_2_answer(
                    random_security_question_answer
                )
        else:
            logging.warn('Unhandled security question index')

        if not is_answer_correct:
            self.request.session['forgot_password_attempts'] += 1
            form.add_error('random_security_question_answer',
                           _('Your answer to the security question was '
                             'invalid. Please try again.'))
            return self.render_to_response({'form': form})

        token = default_token_generator.make_token(user)
        q = QueryDict(mutable=True)
        q['user'] = username
        q['token'] = token
        reset_password_url = '{0}?{1}'.format(
            reverse('reset_password'), q.urlencode()
        )

        return HttpResponseRedirect(reset_password_url)

    def render_to_response(self, context, **response_kwargs):
        random_security_question_idx = random.randint(
            0, len(self.security_questions) - 1
        )
        random_security_question = self.security_questions[
            random_security_question_idx
        ]

        context.update({
            'random_security_question': random_security_question
        })

        self.request.session['random_security_question_idx'] = \
            random_security_question_idx

        return super(GemForgotPasswordView, self).render_to_response(
            context, **response_kwargs
        )


class GemResetPasswordView(FormView):
    form_class = GemResetPasswordForm
    template_name = 'reset_password.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        token = form.cleaned_data['token']

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return HttpResponseForbidden()

        if not user.is_active:
            return HttpResponseForbidden()

        if not default_token_generator.check_token(user, token):
            return HttpResponseForbidden()

        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']

        if password != confirm_password:
            form.add_error('password',
                           _('The two PINs that you entered do not match. '
                             'Please try again.'))
            return self.render_to_response({'form': form})

        user.set_password(password)
        user.save()
        self.request.session.flush()

        return HttpResponseRedirect(reverse('reset_password_success'))

    def render_to_response(self, context, **response_kwargs):
        username = self.request.GET.get('user')
        token = self.request.GET.get('token')

        if not username or not token:
            return HttpResponseForbidden()

        context['form'].initial.update({
            'username': username,
            'token': token
        })

        return super(GemResetPasswordView, self).render_to_response(
            context, **response_kwargs
        )


class GemResetPasswordSuccessView(TemplateView):
    template_name = 'reset_password_success.html'


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
