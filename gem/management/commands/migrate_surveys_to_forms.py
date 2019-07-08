from django.core.management.base import BaseCommand
from molo.surveys.models import (
    MoloSurveyPage, SurveyIndexPage, MoloSurveyFormField,
    MoloSurveyView, MoloSurveyPageSubmission)
from molo.forms.models import (
    MoloFormPage, FormIndexPage, MoloFormView,
    MoloFormsFormField, MoloFormPageSubmission)
from molo.core.models import Main


class Command(BaseCommand):
    def handle(self, *args, **options):
        for main in Main.objects.all():
            surveys_index = SurveyIndexPage.objects.child_of(main).first()
            forms_index = FormIndexPage.objects.child_of(main).first()
            for survey in MoloSurveyPage.objecs.descendent_of(surveys_index):
                survey_dict = survey.__dict__
                del survey_dict['_state']
                form = MoloFormPage.objects.create(**survey_dict)
                forms_index.add_child(form)

                for form_field in MoloSurveyFormField.objects.filter(
                        page__pk=survey.pk):
                    form_field_dict = form_field.__dict__
                    del form_field_dict['_state']
                    MoloFormsFormField.objects.create(**form_field_dict)

        for view in MoloSurveyView.objects.all():
            view_dict = view.__dict__
            del view_dict['_state']
            MoloFormView.objects.create(**view_dict)

        for submission in MoloSurveyPageSubmission.objects.all():
            submission_dict = submission.__dict__
            del submission_dict['_state']
            MoloFormPageSubmission.objects.create(**submission_dict)
