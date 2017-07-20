import pytest

from django.contrib.sites.models import Site
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.utils import timezone

from molo.commenting.models import MoloComment
from molo.core.models import SectionIndexPage
from molo.core.tests.base import MoloTestCaseMixin
from molo.surveys.models import SurveysIndexPage

from wagtail_personalisation.models import Segment

from ..models import PersonalisableSurveyFormField, PersonalisableSurvey
from ..rules import ProfileDataRule, SurveySubmissionDataRule, \
    GroupMembershipRule, CommentDataRule


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
                               field='gem.GemUserProfile__gender',
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


@pytest.mark.django_db
class TestSurveyDataRuleSegmentation(TestCase, MoloTestCaseMixin):
    def setUp(self):
        # Fabricate a request with a logged-in user
        # so we can use it to test the segment rule
        self.mk_main()
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get('/')
        self.request.user = get_user_model().objects.create_user(
            username='tester', email='tester@example.com', password='tester')

        # Create survey
        self.survey = PersonalisableSurvey(title='Test Survey')
        SurveysIndexPage.objects.first().add_child(instance=self.survey)

        # Create survey form fields
        self.singleline_text = PersonalisableSurveyFormField.objects.create(
            field_type='singleline', label='Singleline Text', page=self.survey)
        self.checkboxes = PersonalisableSurveyFormField.objects.create(
            field_type='checkboxes', label='Checboxes Field', page=self.survey,
            choices='choice 1, choice 2, choice 3')
        self.checkbox = PersonalisableSurveyFormField.objects.create(
            field_type='checkbox', label='Checbox Field', page=self.survey)
        self.number = PersonalisableSurveyFormField.objects.create(
            field_type='number', label='Number Field', page=self.survey)

        # Create survey submission
        data = {
            self.singleline_text.clean_name: 'super random text',
            self.checkboxes.clean_name: ['choice 3', 'choice 1'],
            self.checkbox.clean_name: True,
            self.number.clean_name: 5
        }
        form = self.survey.get_form(
            data, page=self.survey, user=self.request.user)

        assert form.is_valid(), \
            'Could not validate submission form. %s' % repr(form.errors)

        self.survey.process_form_submission(form)

        self.survey.refresh_from_db()

    def test_passing_string_rule_with_equal_operator(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.EQUALS,
            expected_response='super random text',
            field_name=self.singleline_text.clean_name)

        self.assertTrue(rule.test_user(self.request))

    def test_failing_string_rule_with_equal_operator(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.EQUALS,
            expected_response='super random textt',
            field_name=self.singleline_text.clean_name)

        self.assertFalse(rule.test_user(self.request))

    def test_passing_string_rule_with_contain_operator(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='text',
            field_name=self.singleline_text.clean_name)

        self.assertTrue(rule.test_user(self.request))

    def test_failing_string_rule_with_contain_operator(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='word',
            field_name=self.singleline_text.clean_name)

        self.assertFalse(rule.test_user(self.request))

    def test_padding_checkboxes_rule_with_equal_operator(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response=' choice 3 , choice 1 ',
            field_name=self.checkboxes.clean_name)

        self.assertTrue(rule.test_user(self.request))

    def test_failing_checkboxes_rule_with_equal_operator(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='choice2,choice1',
            field_name=self.checkboxes.clean_name)

        self.assertFalse(rule.test_user(self.request))

    def test_passing_checkboxes_rule_with_contain_operator(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='choice 3',
            field_name=self.checkboxes.clean_name)

        self.assertTrue(rule.test_user(self.request))

    def test_failing_checkboxes_rule_with_contain_operator(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='choice 2, choice 3',
            field_name=self.checkboxes.clean_name)

        self.assertFalse(rule.test_user(self.request))

    def test_passing_checkbox_rule(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='1',
            field_name=self.checkbox.clean_name)

        self.assertTrue(rule.test_user(self.request))

    def test_failing_checkbox_rule(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='0',
            field_name=self.checkbox.clean_name)

        self.assertFalse(rule.test_user(self.request))

    def test_passing_number_rule(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='5',
            field_name=self.number.clean_name)

        self.assertTrue(rule.test_user(self.request))

    def test_failing_number_rule(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='4',
            field_name=self.number.clean_name)

        self.assertFalse(rule.test_user(self.request))

    def test_not_logged_in_user_fails(self):
        rule = SurveySubmissionDataRule(
            survey=self.survey, operator=SurveySubmissionDataRule.CONTAINS,
            expected_response='er ra',
            field_name=self.singleline_text.clean_name)

        # Passes for logged-in user
        self.assertTrue(rule.test_user(self.request))

        # Fails for logged-out user
        self.request.user = AnonymousUser()
        self.assertFalse(rule.test_user(self.request))


class TestCommentDataRuleSegmentation(TestCase, MoloTestCaseMixin):
    def setUp(self):
        # Create an article
        self.mk_main()
        self.section = SectionIndexPage.objects.first()

        self.article = self.mk_article(self.section, title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')
        self.content_type = ContentType.objects.get_for_model(self.article)

        # Fabricate a request with a logged-in user
        # so we can use it to test the segment rule
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get('/')
        self.request.user = get_user_model().objects.create_user(
            username='tester', email='tester@example.com', password='tester')

    def _create_comment(self, comment, parent=None):
        return MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=self.article.pk,
            content_object=self.article,
            site=Site.objects.get_current(),
            user=self.request.user,
            comment=comment,
            parent=parent,
            submit_date=timezone.now())

    def test_comment_data_exact_rule(self):
        self._create_comment('that is some random content.')
        rule = CommentDataRule(expected_content='that is some random content.',
                               operator=CommentDataRule.EQUALS)

        self.assertTrue(rule.test_user(self.request))

    def test_comment_data_exact_rule_fails(self):
        self._create_comment('that is some random content.')
        rule = CommentDataRule(expected_content='that is some other content',
                               operator=CommentDataRule.EQUALS)

        self.assertFalse(rule.test_user(self.request))

    def test_comment_data_contains_rule(self):
        self._create_comment('that is some random content.')
        rule = CommentDataRule(expected_content='some random',
                               operator=CommentDataRule.CONTAINS)

        self.assertTrue(rule.test_user(self.request))

    def test_comment_data_contains_rule_fails(self):
        self._create_comment('that is some random content.')
        rule = CommentDataRule(expected_content='somerandom',
                               operator=CommentDataRule.CONTAINS)

        self.assertFalse(rule.test_user(self.request))


class TestGroupMembershipRuleSegmentation(TestCase, MoloTestCaseMixin):
    def setUp(self):
        # Fabricate a request with a logged-in user
        # so we can use it to test the segment rule
        self.mk_main()
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get('/')
        self.request.user = get_user_model().objects.create_user(
            username='tester', email='tester@example.com', password='tester')

        self.group = Group.objects.create(name='Super Test Group!')

        self.request.user.groups.add(self.group)

    def test_user_membership_rule_when_they_are_member(self):
        rule = GroupMembershipRule(group=self.group)

        self.assertTrue(rule.test_user(self.request))

    def test_user_membership_rule_when_they_are_not_member(self):
        group = Group.objects.create(name='Wagtail-like creatures')
        rule = GroupMembershipRule(group=group)

        self.assertFalse(rule.test_user(self.request))

    def test_user_membership_rule_on_not_logged_in_user(self):
        self.request.user = AnonymousUser()
        rule = GroupMembershipRule(group=self.group)

        self.assertFalse(rule.test_user(self.request))
