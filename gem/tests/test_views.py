from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
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
    UserProfilesSettings,
)


@override_settings(
    SECURITY_QUESTION_1='question_1',
    SECURITY_QUESTION_2='question_2',
)
class GemRegistrationViewTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.client = Client()
        self.mk_main2()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)

        for main in Main.objects.all():
            profile_settings = UserProfilesSettings.for_site(main.get_site())
            profile_settings.show_security_question_fields = True
            profile_settings.security_questions_required = True
            profile_settings.num_security_questions = 2
            profile_settings.activate_gender = True
            profile_settings.capture_gender_on_reg = True
            profile_settings.gender_required = True
            profile_settings.save()

            security_index = SecurityQuestionIndexPage.objects.descendant_of(
                main).first()
            for i in range(1, 3):
                question = SecurityQuestion(title='question_{0}'.format(i))
                security_index.add_child(instance=question)
                question.save_revision().publish()

    def user_registration_data(self):
        return {
            'username': 'testuser',
            'password': '1234',
            'gender': 'f',
            'question_0': 'answer_1',
            'question_1': 'answer_2',
            'terms_and_conditions': 'on',
        }

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
            'question_0': 'answer_1',
            'question_1': 'answer_2',
            'terms_and_conditions': 'on',
        })
        self.assertEqual(UserProfile.objects.all().count(), 1)
        user = User.objects.get(username='testuser')

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
            response, 'form', 'question_0',
            ['This field is required.']
        )
        self.assertFormError(
            response, 'form', 'question_1',
            ['This field is required.']
        )

    def test_email_or_phone_not_allowed_in_username(self):
        response = self.client.post(reverse('user_register'), {
            'username': 'tester@test.com',
            'password': '1234',
            'gender': 'm',
            'question_0': 'cat',
            'question_1': 'dog'
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
            'question_0': 'cat',
            'question_1': 'dog'
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
        self.client.post(
            reverse('user_register'),
            self.user_registration_data(),
        )

        security_questions = SecurityQuestion.objects.descendant_of(
            self.main).all()
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

    def test_security_answer_attached_to_question_from_correct_site(self):
        client = Client(HTTP_HOST=self.site2.hostname)
        client.post(
            reverse('user_register'),
            self.user_registration_data(),
        )
        security_questions = SecurityQuestion.objects.descendant_of(
            self.main2).all()
        security_answers = SecurityAnswer.objects.all()

        for i in range(2):
            self.assertEqual(
                security_answers[i].question,
                security_questions[i],
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
        self.content_type = ContentType.objects.get_for_model(self.user)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.site),
            locale='fr',
            is_active=True)
        self.translated_article = self.mk_article_translation(
            self.article, self.french,
            title=self.article.title + ' in french',
            subtitle=self.article.subtitle + ' in french')

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

    def test_anonymous_comment_translation(self):
        MoloComment.objects.create(
            content_object=self.translated_article,
            object_pk=self.translated_article.id,
            content_type=ContentType.objects.get_for_model(
                self.translated_article),
            site=Site.objects.get_current(), user=self.user,
            comment='This is another comment for French',
            submit_date=timezone.now())
        response = self.client.get('/locale/fr/')
        response = self.client.get(
            reverse('molo.commenting:more-comments', args=(
                self.translated_article.pk,)))
        self.assertContains(response, "This is another comment for French")
        # we test for translation of anonymous in project tests
        self.assertNotContains(response, "Anonymous")

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

    def test_renders_report_response_template(self):
        comment = self.create_comment(self.article, 'report me')
        response = self.client.get(
            reverse('report_response', args=(comment.pk,)))
        self.assertContains(response, 'This comment has been reported.')
