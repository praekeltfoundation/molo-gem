from django.core.management.base import BaseCommand
from wagtail_personalisation.models import Segment
from molo.core.models import Main, FooterPage
from molo.surveys.models import (
    MoloSurveyPage, SurveysIndexPage, MoloSurveyFormField,
    MoloSurveyPageView, MoloSurveySubmission,
    PersonalisableSurvey, PersonalisableSurveyFormField,
    SegmentUserGroup, TermsAndConditionsIndexPage
)
from molo.surveys.rules import (
    SurveySubmissionDataRule, SurveyResponseRule, GroupMembershipRule,
    ArticleTagRule, CombinationRule
)
from molo.forms.models import (
    MoloFormPage, FormsIndexPage, MoloFormField,
    MoloFormPageView, MoloFormSubmission,
    PersonalisableForm, PersonalisableFormField,
    FormsSegmentUserGroup, FormsTermsAndConditionsIndexPage,
    FormTermsConditions
)
from molo.forms.rules import (
    FormSubmissionDataRule, FormResponseRule, FormGroupMembershipRule,
    FormsArticleTagRule, FormCombinationRule
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for main in Main.objects.all():
            surveys_index = SurveysIndexPage.objects.child_of(main).first()
            forms_index = FormsIndexPage.objects.child_of(main).first()
            surveys_tc = TermsAndConditionsIndexPage.objects.child_of(
                surveys_index).first()

            # Copy the Survey Ts&Cs to Forms
            if surveys_tc:
                forms_tc = FormsTermsAndConditionsIndexPage(
                    title="Form Terms And Conditions Index Page")
                forms_index.add_child(instance=forms_tc)
                forms_tc.save_revision().publish()
                for footerpage in FooterPage.objects.child_of(surveys_tc):
                    footer_dict = {}
                    exclude = (
                        '_state', 'id', 'path', 'numchild',
                        'page_ptr_id', 'content_type_id',
                        'articlepage_ptr_id', '_language_cache',
                    )
                    for item in footerpage.__dict__.items():
                        if item[0] not in exclude:
                            footer_dict[item[0]] = item[1]

                    footer_page = FooterPage(**footer_dict)
                    forms_tc.add_child(instance=footer_page)
                    if footerpage.status_string == 'draft':
                        footer_page.save_revision().publish()
                        footer_page.specific.unpublish()
                    else:
                        footer_page.save_revision().publish()
            print("Copying of Survey Ts&Cs is Done")

            # Migrate Survey Page to Form Page
            translated_survey = {}
            for survey in MoloSurveyPage.objects.descendant_of(
                    surveys_index).exact_type(MoloSurveyPage):
                if survey.language.is_main_language and\
                     survey.translated_pages.first():
                    translated_survey[survey.slug] = \
                        survey.translated_pages.first().slug

                survey_dict = {}
                exclude = (
                    '_state', 'id', 'path', 'numchild',
                    'page_ptr_id', 'content_type_id',
                    'landing_page_template', '_language_cache'
                )
                for item in survey.__dict__.items():
                    if item[0] not in exclude:
                        survey_dict[item[0]] = item[1]

                survey_id = survey.id
                survey_dict['slug'] = "form-" + survey_dict['slug']
                survey_dict['display_form_directly'] = survey_dict[
                    'display_survey_directly']
                del survey_dict['display_survey_directly']

                form = MoloFormPage(**survey_dict)
                forms_index.add_child(instance=form)
                if survey.status_string == 'draft':
                    form.specific.unpublish()
                else:
                    form.save_revision().publish()

                if survey.terms_and_conditions.first():
                    form_tc = FooterPage.objects.child_of(
                        forms_tc).filter(
                            title=survey.terms_and_conditions.first(
                            ).terms_and_conditions.title)
                    survey.terms_and_conditions.first().terms_and_conditions
                    FormTermsConditions.objects.create(
                        page=form,
                        terms_and_conditions=form_tc.first())

                for form_field in MoloSurveyFormField.objects.filter(
                        page_id=survey_id):
                    form_field_dict = {}
                    for item in form_field.__dict__.items():
                            form_field_dict[item[0]] = item[1]
                    form_field_dict['page_id'] = form.id
                    del form_field_dict['_state']

                    MoloFormField.objects.create(**form_field_dict)

                for submission in MoloSurveySubmission.objects.filter(
                            page_id=survey_id):
                        submission_dict = {}
                        for item in submission.__dict__.items():
                            submission_dict[item[0]] = item[1]

                        del submission_dict['_state']
                        submission_dict['submit_time'] = submission_dict[
                            'created_at']
                        del submission_dict['created_at']
                        submission_dict['page_id'] = form.id
                        MoloFormSubmission.objects.create(**submission_dict)
            for key in translated_survey:
                main_form = MoloFormPage.objects.get(
                    slug="form-%s" % key).specific
                translated_form = MoloFormPage.objects.get(
                    slug="form-%s" % translated_survey[key]).specific
                main_form.translated_pages.add(translated_form)
                translated_form.translated_pages.add(main_form)
            print("Migration of SurveyPage is Done")

            # Migrate Personalisable Survey to Form
            translated_survey = {}
            for personalisable_survey in \
                PersonalisableSurvey.objects.descendant_of(
                    surveys_index).exact_type(PersonalisableSurvey):
                if personalisable_survey.language.is_main_language and \
                     personalisable_survey.translated_pages.first():
                    translated_survey[personalisable_survey.slug] = \
                        personalisable_survey.translated_pages.first().slug

                personalisable_survey_dict = {}
                exclude = (
                    '_state', 'id', 'content_type_id',
                    'molosurveypage_ptr_id', 'numchild',
                    'landing_page_template', 'page_ptr_id',
                    '_language_cache'
                )
                for item in personalisable_survey.__dict__.items():
                    if item[0] not in exclude:
                        personalisable_survey_dict[item[0]] = item[1]

                personalisable_survey_id = personalisable_survey.id
                personalisable_survey_dict['slug'] = \
                    "form-" + personalisable_survey_dict['slug']
                personalisable_survey_dict['display_form_directly'] \
                    = personalisable_survey_dict[
                        'display_survey_directly']
                del personalisable_survey_dict[
                    'display_survey_directly']

                personalisable_form = PersonalisableForm(
                    **personalisable_survey_dict)
                forms_index.add_child(instance=personalisable_form)
                if personalisable_survey.status_string == 'draft':
                    personalisable_form.specific.unpublish()
                else:
                    personalisable_form.save_revision().publish()

                if personalisable_survey.terms_and_conditions.first():
                    form_tc = FooterPage.objects.child_of(forms_tc).filter(
                        title=personalisable_survey.terms_and_conditions.first(
                        ).terms_and_conditions.title)
                    personalisable_survey.terms_and_conditions.first()\
                        .terms_and_conditions
                    FormTermsConditions.objects.create(
                        page=personalisable_form,
                        terms_and_conditions=form_tc.first())

                for personalisable_form_field in \
                    PersonalisableSurveyFormField.objects.filter(
                        page_id=personalisable_survey_id):
                    personalisable_form_field_dict = {}

                    for item in personalisable_form_field.__dict__.items():
                        personalisable_form_field_dict[item[0]] = item[1]
                    personalisable_form_field_dict[
                        'page_id'] = PersonalisableForm.objects.filter(
                            id=personalisable_form.id).first().id
                    del personalisable_form_field_dict['_state']
                    del personalisable_form_field_dict['id']

                    PersonalisableFormField.objects.create(
                        **personalisable_form_field_dict)
                for submission in \
                    MoloSurveySubmission.objects.filter(
                        page_id=personalisable_survey_id):
                        submission_dict = {}
                        for item in submission.__dict__.items():
                            submission_dict[item[0]] = item[1]
                        del submission_dict['_state']
                        submission_dict['submit_time'] = \
                            submission_dict['created_at']
                        del submission_dict['created_at']
                        submission_dict[
                            'page_id'] = personalisable_form.id
                        MoloFormSubmission.objects.create(
                            **submission_dict)
            for key in translated_survey:
                main_form = PersonalisableForm.objects.get(
                    slug="form-%s" % key).specific
                translated_form = PersonalisableForm.objects.get(
                    slug="form-%s" % translated_survey[key]).specific
                main_form.translated_pages.add(translated_form)
                translated_form.translated_pages.add(main_form)
        print("Migration of Personalisable Survey is Done")

        # Migrate Survey User Group to Form
        for segment_user_group in SegmentUserGroup.objects.all():
            segment_user_group_dict = {}
            for item in segment_user_group.__dict__.items():
                    segment_user_group_dict[item[0]] = item[1]
            del segment_user_group_dict['_state']
            del segment_user_group_dict['id']
            segment_user_group_dict['name'] = \
                "form-" + segment_user_group_dict['name']

            FormsSegmentUserGroup.objects.create(
                **segment_user_group_dict)
        print("Migration of User Group is Done")

        # Migrate Survey Page View
        for view in MoloSurveyPageView.objects.all():
            view_dict = {}
            for item in view.__dict__.items():
                if item[0] not in ('_state'):
                    view_dict[item[0]] = item[1]
            form_page_view = MoloFormPageView(**view_dict)
            form_page_view.save()
            form_page_view.visited_at = view_dict["visited_at"]
            form_page_view.save()
        print("Migration of PageView is Done")

        # Migrate Survey Rules to Form
        for segment in Segment.objects.all():
            submission_rule = \
                SurveySubmissionDataRule.objects.filter(
                    segment_id=segment.id).first()
            if submission_rule:
                rule_dict = {}
                for item in submission_rule.__dict__.items():
                    if item[0] not in ('id', '_state'):
                        rule_dict[item[0]] = item[1]
                survey_slug = MoloSurveyPage.objects.filter(
                    id=rule_dict["survey_id"]).first().slug
                form_id = MoloFormPage.objects.filter(
                    slug="form-" + survey_slug).first().id
                rule_dict["form_id"] = form_id
                del rule_dict["survey_id"]
                FormSubmissionDataRule.objects.create(**rule_dict)
                submission_rule.delete()
                segment.save()

            response_rule = SurveyResponseRule.objects.filter(
                segment_id=segment.id).first()
            if response_rule:
                rule_dict = {}
                for item in response_rule.__dict__.items():
                    if item[0] not in ('id', '_state'):
                        rule_dict[item[0]] = item[1]
                survey_slug = MoloSurveyPage.objects.filter(
                    id=rule_dict["survey_id"]).first().slug
                form_id = MoloFormPage.objects.filter(
                    slug="form-" + survey_slug).first().id
                rule_dict["form_id"] = form_id
                del rule_dict["survey_id"]
                FormResponseRule.objects.create(**rule_dict)
                response_rule.delete()
                segment.save()

            article_rule = ArticleTagRule.objects.filter(
                segment_id=segment.id).first()
            if article_rule:
                rule_dict = {}
                for item in article_rule.__dict__.items():
                    if item[0] not in ('id', '_state'):
                        rule_dict[item[0]] = item[1]
                FormsArticleTagRule.objects.create(**rule_dict)
                article_rule.delete()
                segment.save()

            combination_rule = CombinationRule.objects.filter(
                segment_id=segment.id).first()
            if combination_rule:
                rule_dict = {}
                for item in combination_rule.__dict__.items():
                    if item[0] not in ('id', '_state'):
                        rule_dict[item[0]] = item[1]
                FormCombinationRule.objects.create(**rule_dict)
                combination_rule.delete()
                segment.save()

<<<<<<< HEAD
        #     MoloFormSubmission.objects.create(**submission_dict)

        # for segment_user_group in SegmentUserGroup.objects.all():
        #     segment_user_group_dict = segment_user_group.__dict__
        #     del segment_user_group_dict['_state']
        #     FormsSegmentUserGroup.objects.create(**segment_user_group_dict)
=======
            group_rule = GroupMembershipRule.objects.filter(
                segment_id=segment.id).first()
            if group_rule:
                rule_dict = {}
                for item in group_rule.__dict__.items():
                    if item[0] not in ('id', '_state'):
                        rule_dict[item[0]] = item[1]
                survey_group = SegmentUserGroup.objects.filter(
                    id=rule_dict["group_id"]).first()
                form_group = FormsSegmentUserGroup.objects.filter(
                    name="form-" + survey_group.name).first()
                rule_dict["group_id"] = form_group.id
                FormGroupMembershipRule.objects.create(**rule_dict)
                group_rule.delete()
                segment.save()
        print("Migration of Survey Rules to Form is Done")
>>>>>>> ce94b7b472ecb00ff9d0cb42448aebcee3154cd8
