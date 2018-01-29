import time

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.utils import timezone

from wagtail.wagtailcore.models import Site as WagtailSite

from gem.forms import GemRegistrationForm, GemEditProfileForm
from gem.models import GemSettings, GemCommentReport

from molo.commenting.forms import MoloCommentForm
from molo.commenting.models import MoloComment
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguageRelation, Main, Languages
from molo.profiles.models import (
    SecurityAnswer,
    SecurityQuestion,
    SecurityQuestionIndexPage,
    UserProfile,
)


@override_settings(
    SECURITY_QUESTION_1='question_1',
    SECURITY_QUESTION_2='question_2',
)
class GemRegistrationViewTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.mk_main2()

        security_index = SecurityQuestionIndexPage.objects.first()
        for i in range(1, 3):
            question = SecurityQuestion(title='question_{0}'.format(i))
            security_index.add_child(instance=question)
            question.save_revision().publish()

    def test_register_view(self):
        response = self.client.get(reverse('user_register'))
        self.assertTrue(isinstance(response.context['form'],
                        GemRegistrationForm))

    def test_register_view_valid_form(self):
        self.assertEqual(UserProfile.objects.all().count(), 0)
        self.client.post(reverse('user_register'), {
            'username': 'testuser',
            'password': '1234',
            'gender': 'f',
            'security_question_1_answer': 'answer_1',
            'security_question_2_answer': 'answer_2',
            'terms_and_conditions': 'on',
        })
        self.assertEqual(UserProfile.objects.all().count(), 1)
        user = User.objects.get(username='testuser')
        self.assertEqual(user.gem_profile.gender, 'f')

        # test thatthe registrationv view writes to both gem and molo profiles
        self.assertEqual(user.profile.gender, 'f')

    def test_register_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse('user_register'), {
        })
        self.assertFormError(
            response, 'form', 'username', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'password', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'gender', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'security_question_1_answer',
            ['This field is required.']
        )
        self.assertFormError(
            response, 'form', 'security_question_2_answer',
            ['This field is required.']
        )

    def test_email_or_phone_not_allowed_in_username(self):
        response = self.client.post(reverse('user_register'), {
            'username': 'tester@test.com',
            'password': '1234',
            'gender': 'm',
            'security_question_1_answer': 'cat',
            'security_question_2_answer': 'dog'
        })

        expected_validation_message = "Sorry, but that is an invalid" \
                                      " username. Please don&#39;t use your" \
                                      " email address or phone number in" \
                                      " your username."

        self.assertContains(response, expected_validation_message)

        response = self.client.post(reverse('user_register'), {
            'username': '0821231234',
            'password': '1234',
            'gender': 'm',
            'security_question_1_answer': 'cat',
            'security_question_2_answer': 'dog'
        })

        self.assertContains(response, expected_validation_message)

    def test_successful_login_for_migrated_users(self):
        user = User.objects.create_user(
            username='1_newuser',
            email='newuser@example.com',
            password='newuser')
        user.profile.migrated_username = 'newuser'
        user.profile.save()

        response = self.client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser',
        })
        self.assertRedirects(response, '/')

        client = Client(HTTP_HOST=self.site2.hostname)

        response = client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser',
        })
        self.assertContains(
            response,
            'Your username and password do not match. Please try again.')

    def test_successful_login_for_migrated_users_in_site_2(self):
        user = User.objects.create_user(
            username='2_newuser',
            email='newuser@example.com',
            password='newuser2')
        user.profile.migrated_username = 'newuser'
        user.profile.save()
        user.profile.site = self.site2
        user.profile.save()

        user3 = User.objects.create_user(
            username='1_newuser',
            email='newuser@example.com',
            password='newuser1')
        user3.profile.migrated_username = 'newuser'
        user3.profile.save()
        user3.profile.site = self.site
        user3.profile.save()

        response = self.client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser2',
        })
        self.assertContains(
            response,
            'Your username and password do not match. Please try again.')

        response = self.client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser1',
        })
        self.assertRedirects(response, '/')

        client = Client(HTTP_HOST=self.site2.hostname)

        response = client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser2',
        })
        self.assertRedirects(response, '/')
        response = client.post('/profiles/login/?next=/', {
            'username': 'newuser',
            'password': 'newuser1',
        })

        self.assertContains(
            response,
            'Your username and password do not match. Please try again.')

    def test_registration_creates_security_answer(self):
        self.client.post(reverse('user_register'), {
            'username': 'testuser',
            'password': '1234',
            'gender': 'f',
            'security_question_1_answer': 'answer_1',
            'security_question_2_answer': 'answer_2',
            'terms_and_conditions': 'on',
        })

        security_questions = SecurityQuestion.objects.all()

        self.assertEqual(security_questions.count(), 2)
        self.assertEqual(security_questions.first().title, 'question_1')
        self.assertEqual(security_questions.last().title, 'question_2')

        security_answers = SecurityAnswer.objects.all()

        self.assertEqual(security_answers.count(), 2)
        self.assertEqual(
            security_answers.first().question,
            security_questions.first(),
        )
        self.assertEqual(
            security_answers.first().user,
            User.objects.get(username='testuser').profile,
        )
        self.assertEqual(
            security_answers.first().check_answer('answer_1'),
            True,
        )
        self.assertEqual(
            security_answers.last().check_answer('answer_2'),
            True,
        )


class GemEditProfileViewTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()

        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.client.login(username='tester', password='tester')

    def test_edit_profile_view_uses_correct_form(self):
        response = self.client.get(reverse('edit_my_profile'))
        self.assertTrue(isinstance(response.context['form'],
                                   GemEditProfileForm))

    def test_email_or_phone_not_allowed_in_display_name(self):
        response = self.client.post(reverse('edit_my_profile'), {
            'alias': 'tester@test.com'
        })
        expected_validation_message = "Sorry, but that is an invalid display" \
                                      " name. Please don&#39;t use your" \
                                      " email address or phone number in" \
                                      " your display name."
        self.assertContains(response, expected_validation_message)

        response = self.client.post(reverse('edit_my_profile'), {
            'alias': '0821231234'
        })

        self.assertContains(response, expected_validation_message)

    def test_offensive_language_not_allowed_in_display_name(self):
        site = Site.objects.get(id=1)
        site.name = 'GEM'
        site.save()
        GemSettings.objects.create(
            site_id=site.id,
            banned_names_with_offensive_language='naughty')
        response = self.client.post(reverse('edit_my_profile'), {
            'alias': 'naughty'
        })
        expected_validation_message = "Sorry, the name you have used is not " \
                                      "allowed. Please, use a different name "\
                                      "for your display name."
        self.assertContains(response, expected_validation_message)


class GemResetPasswordTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()

        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.user.gem_profile.set_security_question_1_answer('dog')
        self.user.gem_profile.set_security_question_2_answer('cat')
        self.user.gem_profile.save()

        # to get the session set up
        response = self.client.get(reverse('forgot_password'))
        response_body = response.content.decode(response.charset)

        if settings.SECURITY_QUESTION_1 in response_body:
            self.question_being_asked = settings.SECURITY_QUESTION_1
        else:
            self.question_being_asked = settings.SECURITY_QUESTION_2

    def post_invalid_username_to_forgot_password_view(self):
        return self.client.post(reverse('forgot_password'), {
            'username': 'invalid',
            'random_security_question_answer': 'something'
        })

    def test_forgot_password_view_invalid_username(self):
        response = self.post_invalid_username_to_forgot_password_view()

        self.assertContains(response, 'The username that you entered appears '
                                      'to be invalid. Please try again.')

    def test_forgot_password_view_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(reverse('forgot_password'), {
            'username': self.user.username,
            'random_security_question_answer': 'something'
        })

        self.assertContains(response, 'This account is inactive.')

    def post_invalid_answer_to_forgot_password_view(self):
        return self.client.post(reverse('forgot_password'), {
            'username': self.user.username,
            'random_security_question_answer': 'invalid'
        })

    def test_forgot_password_view_invalid_answer(self):
        response = self.post_invalid_answer_to_forgot_password_view()

        self.assertContains(response, 'Your answer to the security question '
                                      'was invalid. Please try again.')

    def test_unsuccessful_username_attempts(self):
        response = None
        for x in range(6):
            response = self.post_invalid_username_to_forgot_password_view()

        # on the 6th attempt
        self.assertContains(response, 'Too many attempts. Please try again '
                                      'later.')

    def test_unsuccessful_answer_attempts(self):
        response = None
        for x in range(6):
            response = self.post_invalid_answer_to_forgot_password_view()

        # on the 6th attempt
        self.assertContains(response, 'Too many attempts. Please try again '
                                      'later.')

    def get_expected_token_and_redirect_url(self):
        expected_token = default_token_generator.make_token(self.user)
        expected_query_params = QueryDict(mutable=True)
        expected_query_params['user'] = self.user.username
        expected_query_params['token'] = expected_token
        expected_redirect_url = '{0}?{1}'.format(
            reverse('reset_password'), expected_query_params.urlencode()
        )
        return expected_token, expected_redirect_url

    def proceed_to_reset_password_page(self):
        if self.question_being_asked == settings.SECURITY_QUESTION_1:
            answer = 'dog'
        else:
            answer = 'cat'

        response = self.client.post(reverse('forgot_password'), {
            'username': self.user.username,
            'random_security_question_answer': answer
        })

        expected_token, expected_redirect_url = \
            self.get_expected_token_and_redirect_url()

        self.assertRedirects(response, expected_redirect_url)

        return expected_token, expected_redirect_url

    def test_reset_password_view_pin_mismatch(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            'username': self.user.username,
            'token': expected_token,
            'password': '1234',
            'confirm_password': '4321'
        })

        self.assertContains(response, 'The two PINs that you entered do not '
                                      'match. Please try again.')

    def test_reset_password_view_requires_query_params(self):
        response = self.client.get(reverse('reset_password'))
        self.assertEqual(403, response.status_code)

    def test_reset_password_view_invalid_username(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            'username': 'invalid',
            'token': expected_token,
            'password': '1234',
            'confirm_password': '1234'
        })

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_inactive_user(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        self.user.is_active = False
        self.user.save()

        response = self.client.post(expected_redirect_url, {
            'username': self.user.username,
            'token': expected_token,
            'password': '1234',
            'confirm_password': '1234'
        })

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_invalid_token(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            'username': self.user.username,
            'token': 'invalid',
            'password': '1234',
            'confirm_password': '1234'
        })

        self.assertEqual(403, response.status_code)

    def test_happy_path(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            'username': self.user.username,
            'token': expected_token,
            'password': '1234',
            'confirm_password': '1234'
        })

        self.assertRedirects(response, reverse('reset_password_success'))

        self.assertTrue(
            self.client.login(username='tester', password='1234')
        )

    @override_settings(SESSION_COOKIE_AGE=1)
    def test_session_expiration_allows_subsequent_attempts(self):
        self.test_unsuccessful_username_attempts()

        time.sleep(1)

        response = self.client.post(reverse('forgot_password'), {
            'username': 'invalid',
            'random_security_question_answer': 'something'
        })

        # the view should redirect back to itself to set up a new session
        self.assertRedirects(response, reverse('forgot_password'))

        # follow the redirect
        self.client.get(reverse('forgot_password'))

        # now another attempt should be possible
        self.test_forgot_password_view_invalid_username()


class CommentingTestCase(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.client = ()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin')

        self.client = Client()

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article = self.mk_article(self.yourmind,
                                       title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')

    def create_comment(self, article, comment, user, parent=None):
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(article),
            object_pk=article.pk,
            content_object=article,
            site=Site.objects.get_current(),
            user=user,
            comment=comment,
            parent=parent,
            submit_date=timezone.now())

    def getData(self):
        return {
            'name': self.user.username,
            'email': self.user.email
        }

    def test_comment_shows_user_display_name(self):
        # check when user doesn't have an alias
        self.create_comment(self.article, 'test comment1 text', self.user)
        response = self.client.get('/sections-main-1/your-mind/article-1/')
        self.assertContains(response, "Anonymous")

        # check when user have an alias
        self.user.profile.alias = 'this is my alias'
        self.user.profile.save()
        self.create_comment(self.article, 'test comment2 text', self.user)
        response = self.client.get('/sections-main-1/your-mind/article-1/')
        self.assertContains(response, "this is my alias")
        self.assertNotContains(response, "tester")

    def test_comment_distinguishes_moderator_user(self):
        self.user = User.objects.create_user(
            username='foo',
            email='foo@example.com',
            password='foo',
            is_staff=True)

        self.client.login(username='admin', password='admin')

        response = self.client.get('/sections-main-1/your-mind/article-1/')
        self.assertNotContains(response, "Big Sister")
        self.assertNotContains(response, "Gabi")

        self.create_comment(self.article, 'test comment1 text', self.superuser)
        response = self.client.get('/sections-main-1/your-mind/article-1/')
        self.assertContains(response, "Big Sister")
        self.assertNotContains(response, "Gabi")

        default_site = WagtailSite.objects.get(is_default_site=True)
        setting = GemSettings.objects.get(site=default_site)
        setting.moderator_name = 'Gabi'
        setting.save()
        response = self.client.get('/sections-main-1/your-mind/article-1/')
        self.assertNotContains(response, "Big Sister")
        self.assertContains(response, "Gabi")

    def getValidData(self, obj):
        form = MoloCommentForm(obj)
        form_data = self.getData()
        form_data.update(form.initial)
        return form_data

    def test_comment_filters(self):
        site = Site.objects.get(id=1)
        site.name = 'GEM'
        site.save()
        GemSettings.objects.create(site_id=site.id,
                                   banned_keywords_and_patterns='naughty')

        form_data = self.getValidData(self.article)

        # check if user has typed in a number
        comment_form = MoloCommentForm(
            self.article, data=dict(form_data, comment="0821111111")
        )

        self.assertFalse(comment_form.is_valid())

        # check if user has typed in an email address
        comment_form = MoloCommentForm(
            self.article, data=dict(form_data, comment="test@test.com")
        )

        self.assertFalse(comment_form.is_valid())

        # check if user has used a banned keyword
        comment_form = MoloCommentForm(
            self.article, data=dict(form_data, comment="naughty")
        )

        self.assertFalse(comment_form.is_valid())


class GemFeedViewsTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()

        section = self.mk_section(self.section_index, title='Test Section')

        self.article_page = self.mk_article(
            section, title='Test Article',
            subtitle='This should appear in the feed')

    def test_rss_feed_view(self):
        response = self.client.get(reverse('feed_rss'))

        self.assertContains(response, self.article_page.title)
        self.assertContains(response, self.article_page.subtitle)
        self.assertNotContains(response, 'example.com')

    def test_atom_feed_view(self):
        response = self.client.get(reverse('feed_atom'))

        self.assertContains(response, self.article_page.title)
        self.assertContains(response, self.article_page.subtitle)
        self.assertNotContains(response, 'example.com')


class GemReportCommentViewTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.client.login(username='tester', password='tester')

        self.content_type = ContentType.objects.get_for_model(self.user)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article = self.mk_article(self.yourmind,
                                       title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')

    def create_comment(self, article, comment, parent=None):
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(article),
            object_pk=article.pk,
            content_object=article,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            parent=parent,
            submit_date=timezone.now())

    def create_reported_comment(self, comment, report_reason):
        return GemCommentReport.objects.create(
            comment=comment,
            user=self.user,
            reported_reason=report_reason
        )

    def test_report_view(self):
        comment = self.create_comment(self.article, 'report me')
        response = self.client.get(
            reverse('report_comment', args=(comment.pk,))
        )

        self.assertContains(response, 'Please let us know why you are '
                                      'reporting this comment?')

    def test_user_has_already_reported_comment(self):
        comment = self.create_comment(self.article, 'report me')

        self.create_reported_comment(comment, 'Spam')

        response = self.client.get(
            reverse('report_comment', args=(comment.pk,)), follow=True
        )

        self.assertContains(response, 'You have already reported this comment')
