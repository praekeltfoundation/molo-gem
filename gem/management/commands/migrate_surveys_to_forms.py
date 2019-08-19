from django.core.management.base import BaseCommand
from molo.core.models import Main
from molo.surveys.models import (
    MoloSurveyPage, SurveysIndexPage, MoloSurveyFormField,
    MoloSurveyPageView, MoloSurveySubmission, 
    PersonalisableSurvey, PersonalisableSurveyFormField,
    SegmentUserGroup)
from molo.forms.models import (
    MoloFormPage, FormsIndexPage, MoloFormField, 
    MoloFormPageView, MoloFormSubmission,
    PersonalisableForm, PersonalisableFormField,
    FormsSegmentUserGroup)

def remove_keys(entries, the_dict):
        for k in entries:
            del the_dict[k]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for main in Main.objects.all():
            surveys_index = SurveysIndexPage.objects.child_of(main).first()
            forms_index = FormsIndexPage.objects.child_of(main).first()

            for survey in MoloSurveyPage.objects.descendant_of(
                    surveys_index).exact_type(MoloSurveyPage):
                survey_dict = survey.__dict__
                survey_id = survey.id
                survey_dict['slug'] = "form-" + survey_dict['slug']
                survey_dict['display_form_directly'] = survey_dict['display_survey_directly']
                
                entries = (
                    'display_survey_directly', '_state', 'id', 'path',
                    'page_ptr_id', 'content_type_id', 'numchild',
                    'landing_page_template'
                )
                remove_keys(entries,survey_dict)
                
                form = MoloFormPage(**survey_dict)
                forms_index.add_child(instance=form)

                for form_field in MoloSurveyFormField.objects.filter(
                        page_id=survey_id):
                    form_field_dict = form_field.__dict__
                    form_field_dict['page_id'] = form.id
                    del form_field_dict['_state']
                    MoloFormField.objects.create(**form_field_dict)

            for personalisable_survey in PersonalisableSurvey.objects.descendant_of(
                    surveys_index).exact_type(PersonalisableSurvey):
                personalisable_survey_dict = personalisable_survey.__dict__
                personalisable_survey_id = personalisable_survey.id
                personalisable_survey_dict['slug'] = "form-" + personalisable_survey_dict['slug']
                personalisable_survey_dict['display_form_directly'] = personalisable_survey_dict['display_survey_directly']
                
                entries = (
                    'display_survey_directly', '_state', 'id', 'path',
                    'molosurveypage_ptr_id', 'content_type_id', 'numchild',
                    'landing_page_template'
                )
                remove_keys(entries,personalisable_survey_dict)

                personalisable_form = PersonalisableForm(**personalisable_survey_dict)
                forms_index.add_child(instance=personalisable_form)

                for personalisable_form_field in PersonalisableSurveyFormField.objects.filter(
                        page_id=personalisable_survey_id):
                    personalisable_form_field_dict = personalisable_form_field.__dict__
                    personalisable_form_field_dict['page_id'] = personalisable_form.id
                    del personalisable_form_field_dict['_state']

                    PersonalisableFormField.objects.create(**personalisable_form_field_dict)
        
        # TODO: move the survey rules to forms rules
        # TODO: create the terms and conditions and change the forms to use the new ones
        # TODO: Update the forms pages in the forms to use the new ones
        # TODO: Update the forms used in skip logic to use new forms


        # for view in MoloSurveyPageView.objects.all():
        #     view_dict = view.__dict__
        #     del view_dict['_state']

        #     MoloFormPageView.objects.create(**view_dict)

        # for submission in MoloSurveySubmission.objects.all():
        #     submission_dict = submission.__dict__
        #     del submission_dict['_state']
        #     submission_dict['submit_time'] = submission_dict['created_at']
        #     del submission_dict['created_at']

        #     MoloFormSubmission.objects.create(**submission_dict)
        
        # for segment_user_group in SegmentUserGroup.objects.all():
        #     segment_user_group_dict = segment_user_group.__dict__
        #     del segment_user_group_dict['_state']
        #     FormsSegmentUserGroup.objects.create(**segment_user_group_dict)
