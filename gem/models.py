from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from gem.constants import GENDERS


class GemUserProfile(models.Model):
    user = models.OneToOneField(
        User, related_name="gem_profile", primary_key=True)

    gender = models.CharField(
        max_length=1, choices=GENDERS, blank=True, null=True)

    security_question_1_answer = models.CharField(max_length=128)
    security_question_2_answer = models.CharField(max_length=128)

    # based on django.contrib.auth.models.AbstractBaseUser set_password &
    # check_password functions
    def set_security_question_1_answer(self, raw_answer):
        self.security_question_1_answer = make_password(
            raw_answer.strip().lower()
        )

    def set_security_question_2_answer(self, raw_answer):
        self.security_question_2_answer = make_password(
            raw_answer.strip().lower()
        )

    def check_security_question_1_answer(self, raw_answer):
        def setter(raw_answer):
            self.set_security_question_1_answer(raw_answer)
            self.save(update_fields=["security_question_1_answer"])

        return check_password(
            raw_answer.strip().lower(), self.security_question_1_answer, setter
        )

    def check_security_question_2_answer(self, raw_answer):
        def setter(raw_answer):
            self.set_security_question_2_answer(raw_answer)
            self.save(update_fields=["security_question_2_answer"])

        return check_password(
            raw_answer.strip().lower(), self.security_question_2_answer, setter
        )


@receiver(post_save, sender=User)
def gem_user_profile_handler(sender, instance, created, **kwargs):
    if created:
        profile = GemUserProfile(user=instance)
        profile.save()
