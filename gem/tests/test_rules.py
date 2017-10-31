from datetime import datetime

import pytest

from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.sites.models import Site
from django.test import TestCase, RequestFactory

from molo.commenting.models import MoloComment
from molo.core.models import ArticlePage, SectionPage
from molo.core.tests.base import MoloTestCaseMixin
from molo.surveys.models import SurveysIndexPage

from wagtail_personalisation.models import Segment

from molo.surveys.models import (
    PersonalisableSurveyFormField, PersonalisableSurvey)
from ..rules import CommentCountRule, ProfileDataRule


@pytest.mark.django_db
class TestProfileDataRuleSegmentation(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.request_factory = RequestFactory()

        # Fabricate a request with a logged-in user
        # so we can use it to test the segment rule
        user = get_user_model().objects \
                               .create_user(username='tester',
                                            email='tester@example.com',
                                            password='tester')
        self.request = self.request_factory.get('/')
        self.request.user = user

    def set_user_to_male(self):
        # Set user to male
        self.request.user.profile.gender = 'm'
        self.request.user.save()

    def set_user_to_female(self):
        self.request.user.profile.gender = 'f'
        self.request.user.save()

    def set_user_to_unspecified(self):
        self.request.user.profile.gender = '-'
        self.request.user.save()

    def test_unspecified_passes_unspecified_rule(self):
        self.set_user_to_unspecified()
        unspecified_rule = ProfileDataRule(
            field='profiles.userprofile__gender', value='-')

        self.assertTrue(unspecified_rule.test_user(self.request))

    def test_male_passes_male_rule(self):
        self.set_user_to_male()
        male_rule = ProfileDataRule(field='profiles.userprofile__gender',
                                    value='m')

        self.assertTrue(male_rule.test_user(self.request))

    def test_female_passes_female_rule(self):
        self.set_user_to_female()
        female_rule = ProfileDataRule(field='profiles.userprofile__gender',
                                      value='f')

        self.assertTrue(female_rule.test_user(self.request))

    def test_unspecified_fails_female_rule(self):
        self.set_user_to_unspecified()
        female_rule = ProfileDataRule(field='profiles.userprofile__gender',
                                      value='f')

        self.assertFalse(female_rule.test_user(self.request))

    def test_female_fails_unspecified_rule(self):
        self.set_user_to_female()
        unspecified_rule = ProfileDataRule(
            field='profiles.userprofile__gender', value='-')

        self.assertFalse(unspecified_rule.test_user(self.request))

    def test_male_fails_unspecified_rule(self):
        self.set_user_to_male()
        unspecified_rule = ProfileDataRule(
            field='profiles.userprofile__gender', value='-')

        self.assertFalse(unspecified_rule.test_user(self.request))

    def test_unexisting_profile_field_fails(self):
        rule = ProfileDataRule(field='auth.User__non_existing_field',
                               value='l')
        with self.assertRaises(FieldDoesNotExist):
            rule.test_user(self.request)

    def test_not_implemented_model_raises_exception(self):
        rule = ProfileDataRule(field='lel.not_existing_model__date_joined',
                               value='2')

        with self.assertRaises(LookupError):
            rule.test_user(self.request)

    def test_not_logged_in_user_fails(self):
        rule = ProfileDataRule(field='auth.User__date_joined',
                               value='2012-09-23')
        self.request.user = AnonymousUser()

        self.assertFalse(rule.test_user(self.request))

    def test_none_value_on_related_field_fails(self):
        rule = ProfileDataRule(field='auth.User__date_joined',
                               value='2012-09-23')

        self.request.user.date_joined = None

        self.assertFalse(rule.test_user(self.request))

    def test_none_value_with_not_equal_rule_field_passes(self):
        rule = ProfileDataRule(field='auth.User__date_joined',
                               operator=ProfileDataRule.NOT_EQUAL,
                               value='2012-09-23')

        self.request.user.date_joined = None

        self.assertTrue(rule.test_user(self.request))

    def test_not_logged_in_user_fails_last_login(self):
        rule = ProfileDataRule(field='auth.User__last_login',
                               value='2012-09-23')
        self.request.user = AnonymousUser()

        self.assertFalse(rule.test_user(self.request))

    def test_none_value_on_related_field_fails_last_login(self):
        rule = ProfileDataRule(field='auth.User__last_login',
                               value='2012-09-23')

        self.request.user.last_login = None

        self.assertFalse(rule.test_user(self.request))

    def test_none_value_with_not_equal_rule_field_passes_last_login(self):
        rule = ProfileDataRule(field='auth.User__last_login',
                               operator=ProfileDataRule.NOT_EQUAL,
                               value='2012-09-23')

        self.request.user.last_login = None

        self.assertTrue(rule.test_user(self.request))


@pytest.mark.django_db
class TestProfileDataRuleValidation(TestCase):
    def setUp(self):
        self.segment = Segment.objects.create()

    def test_invalid_regex_value_raises_validation_error(self):
        rule = ProfileDataRule(segment=self.segment,
                               operator=ProfileDataRule.REGEX,
                               field='aith.User__date_joined',
                               value='[')

        with self.assertRaises(ValidationError) as context:
            rule.full_clean()

        found = False

        for msg in context.exception.messages:
            if msg.startswith('Regular expression error'):
                found = True
                break

        self.failIf(not found)

    def test_age_operator_on_non_date_field_raises_validation_error(self):
        rule = ProfileDataRule(segment=self.segment,
                               operator=ProfileDataRule.OF_AGE,
                               field='profiles.UserProfile__gender',
                               value='1')

        with self.assertRaises(ValidationError) as context:
            rule.full_clean()

        self.assertIn('You can choose age operators only on date and '
                      'date-time fields.', context.exception.messages)

    def test_age_operator_on_negative_numbers_raises_validation_error(self):
        rule = ProfileDataRule(segment=self.segment,
                               operator=ProfileDataRule.OF_AGE,
                               field='profiles.UserProfile__date_of_birth',
                               value='-1')

        with self.assertRaises(ValidationError) as context:
            rule.full_clean()

        self.assertIn('Value has to be non-negative since it represents age.',
                      context.exception.messages)


class TestCommentCountRuleSegmentation(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get('/')
        self.request.user = get_user_model().objects.create_user(
            username='tester', email='tester@example.com', password='tester')
        self.other_user = get_user_model().objects.create_user(
            username='other', email='other@example.com', password='other')

        self.section = SectionPage(title='test section')
        self.section_index.add_child(instance=self.section)

        self.article = self.add_article('first')
        self.other_article = self.add_article('other')

    def add_article(self, title):
        new_article = ArticlePage(title=title)
        self.section.add_child(instance=new_article)
        new_article.save_revision()
        return new_article

    def add_comment(self, user, article, **kwargs):
        return MoloComment.objects.create(
            comment="test comment",
            user=user,
            site=Site.objects.get_current(),
            content_type=article.content_type,
            object_pk=article.id,
            submit_date=datetime.now(),
            **kwargs
        )

    def test_user_passes_rule_when_they_comment(self):
        rule = CommentCountRule(count=1)
        self.add_comment(self.request.user, self.article)
        self.assertTrue(rule.test_user(self.request))

    def test_other_user_doesnt_get_counted(self):
        rule = CommentCountRule(count=1)
        self.add_comment(self.request.user, self.article)
        self.add_comment(self.other_user, self.article)
        self.assertTrue(rule.test_user(self.request))

    def test_user_fails_rule_when_they_comment_too_much(self):
        rule = CommentCountRule(count=1)
        self.add_comment(self.request.user, self.article)
        self.add_comment(self.request.user, self.article)
        self.assertFalse(rule.test_user(self.request))

    def test_user_fails_rule_when_they_dont_comment_enough(self):
        rule = CommentCountRule(count=2)
        self.add_comment(self.request.user, self.article)
        self.assertFalse(rule.test_user(self.request))

    def test_user_passes_rule_when_they_comment_multiple_articles(self):
        rule = CommentCountRule(count=2)
        self.add_comment(self.request.user, self.article)
        self.add_comment(self.request.user, self.other_article)
        self.assertTrue(rule.test_user(self.request))

    def test_user_fails_rule_when_comment_removed(self):
        rule = CommentCountRule(count=1)
        self.add_comment(self.request.user, self.article, is_removed=True)
        self.assertFalse(rule.test_user(self.request))

    def test_user_passes_lt(self):
        rule = CommentCountRule(count=1, operator=CommentCountRule.LESS_THAN)
        self.assertTrue(rule.test_user(self.request))

    def test_user_fails_lt(self):
        rule = CommentCountRule(count=1, operator=CommentCountRule.LESS_THAN)
        self.add_comment(self.request.user, self.article)
        self.assertFalse(rule.test_user(self.request))

    def test_user_passes_gt(self):
        rule = CommentCountRule(count=1, operator=CommentCountRule.GREATER_THAN)
        self.add_comment(self.request.user, self.article)
        self.add_comment(self.request.user, self.article)
        self.assertTrue(rule.test_user(self.request))

    def test_user_fails_gt(self):
        rule = CommentCountRule(count=1, operator=CommentCountRule.GREATER_THAN)
        self.add_comment(self.request.user, self.article)
        self.assertFalse(rule.test_user(self.request))
