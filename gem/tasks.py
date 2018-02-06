import logging

from celery import task
from django.contrib.auth import get_user_model

from molo.profiles.models import (
    SecurityQuestion, SecurityAnswer, SecurityQuestionIndexPage)


@task(ignore_result=True)
def migrate_security_answers_to_profiles(
        question_text, question_number, question_setting):
    for user in get_user_model().objects.all():
        if not hasattr(user, 'profile'):
            logging.warn('User {0} has no profile'.format(user.id))
            continue

        if user.profile.site is None:
            logging.warn('User {0} has no site'.format(user.id))
            continue

        main_page = user.profile.site.root_page
        security_index = SecurityQuestionIndexPage.objects.child_of(
            main_page).first()

        question = SecurityQuestion.objects.filter(
            title=question_text).child_of(security_index).first()

        if not question:
            logging.warn('Unable to migrate "{0}" for {1}'.format(
                question_text, user.id))
            continue

        answer_hashes = [
            user.gem_profile.security_question_1_answer,
            user.gem_profile.security_question_2_answer,
        ]

        answer_hash = answer_hashes[question_number-1]

        if answer_hash is None or len(answer_hash) == 0:
            logging.warn('User {0} has empty hash for {1}'.format(
                user.id,
                question_setting,
            ))
            continue

        security_answer, _ = SecurityAnswer.objects.get_or_create(
            question=question,
            user=user.profile,
        )
        security_answer.answer = answer_hash
        security_answer.save(is_import=True)
