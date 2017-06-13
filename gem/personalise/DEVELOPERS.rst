Personalisation Module - Developer Guide
========================================
``gem.personalise`` is a module that uses `wagtail-personalisation`_ package to provide GEM with content personalisation capabilities. Please refer to its `documentation`_ for more explanation.

.. contents::

.. _wagtail-personalisation: https://github.com/LabD/wagtail-personalisation/
.. _documentation: https://wagtail-personalisation.readthedocs.io/en/latest/

Module Contents
---------------

Personalised Surveys - models.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``PersonalisableSurvey`` model is a page that is a standard Molo survey page with additional personalisation. It allows personalising surveys in two ways:

#. By a specific question
#. By a survey instance

By a Specific Question
**********************
Personalisation by specific questions is implemented by having a relation to ``wagtail_personalisation.Segment`` on ``PersonalisableSurveyFormField.segment``. That way the segment can be set in the admin for each of the form fields/questions. It can be filtered by segment in ``PersonalisableSurvey.get_form_fields``. i.e. when page is served on the frontend the page obtains request object and on that basis we can match segments of survey fields to the user's segments.

By a Survey Instance
**********************
The ``PersonalisableSurvey`` model also supports personalising by a survey instance, i.e. the ``PersonalisableSurvey.segment`` field.

#. When the user is accessing the survey directly by the URL that is not part of their segment they will get a 404 error.
#. The list of surveys displayed on the front page has been edited at the template level in order to filter out surveys that are not supposed to be seen by a user.

Personalisation Rules - rules.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This file contains custom personalisation rules created for GEM that define criteria used to segment content on the website. Rules included in the module are as follows.

#. ``ProfileDataRule`` - Based on user's profile information.
#. ``SurveySubmissionDataRule`` - Based on user's answers to selected surveys.
#. ``GroupMembershipRule`` - Based on user's membership of a group.
#. ``CommentDataRule`` - Based on user's comment data.

ProfileDataRule
***************
``ProfileDataRule`` works with profile fields completed by users. To change a list of fields available for personalisation please edit the ``PERSONALISATION_PROFILE_DATA_RULES`` constant in ``rules.py``.

.. code:: python

    PERSONALISATION_PROFILE_DATA_FIELDS = [
        '{}__date_joined'.format(settings.AUTH_USER_MODEL),
        'profiles.UserProfile__date_of_birth',
        'gem.GemUserProfile__gender'
    ]

The field must be on the user model or model related to the user model directly by a singular relation such as one-to-one so it can be accessed directly on the model as a property. Please note that referencing models that span further does not work.

Please use format ``app.model__field`` when adding a new field to the list.

SurveySubmissionDataRule
************************

``SurveySubmissionDataRule`` works only with surveys that are ``gem.personalise.models.PersonalisableSurvey``. Any other model can be used by reusing/modifying ``SurveySubmissionDataRule`` and making sure that:

#. ``survey`` is a ForeignKey that points at the survey model we want to use.
#. ``field_model`` property returns FormField model used by that survey.
#. ``survey_submission_model`` property returns survey submission class that is used by the new survey type.

Please remember that surveys have to use `wagtailsurveys<https://github.com/torchbox/wagtailsurveys>`_ to be compatible (that is what is currently used on GEM).

How to Create Personalisation Rules?
************************************
Creating new rules is covered in detail wagtail-personalisation documentation in `this section <https://wagtail-personalisation.readthedocs.io/en/latest/implementation.html#creating-custom-rules>`_.

The main steps to create our own custom personalisation rules are as follows.

#. Extend ``wagtail_personalisation.models.AbstractBaseRule``. It is a Django model so we will need to create migrations for it.
#. Rule's name is returned from ``Meta.verbose_name``.
#. Since it is a Django model, you need to define normal Django fields on it, e.g. data entered by user in the admin to define rule's settings.
#. Rules are used based on client's request in ``test_user(request)`` method that should be defined on the rule's class.
#. To modify how the form is displayed in the admin site please set ``panels`` as for any other model displayed in Wagtail admin.

Other Personalisation Rules Visible in Wagtail Admin
****************************************************
The rest of the rules available in the admin are defined in wagtail-personalisation itself. Please read `documentation covering that subject <https://wagtail-personalisation.readthedocs.io/en/latest/default_rules.html>`_ in order to get familiar with them.
