from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from gem.constants import GENDERS
from molo.commenting.models import MoloComment
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel


class GemUserProfile(models.Model):
    user = models.OneToOneField(
        User, related_name="gem_profile", primary_key=True)

    gender = models.CharField(
        max_length=1, choices=GENDERS, blank=True, null=True)

    security_question_1_answer = models.CharField(max_length=128, null=True)
    security_question_2_answer = models.CharField(max_length=128, null=True)

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


@register_setting
class GemSettings(BaseSetting):
    banned_keywords_and_patterns = models.TextField(
        verbose_name='Banned Keywords and Patterns',
        null=True,
        blank=True,
        help_text="Banned keywords and patterns for comments, separated by a"
                  " line a break. Use only lowercase letters for keywords."
    )

    banned_names_with_offensive_language = models.TextField(
        verbose_name='Banned Names With Offensive Language',
        null=True,
        blank=True,
        help_text="Banned names with offensive language, separated by a"
                  " line a break. Use only lowercase letters for keywords."
    )

    show_partner_credit = models.BooleanField(
        default=False,
        help_text='When true, this will show the partner credit on the '
        'homepage.')

    partner_credit_description = models.TextField(
        null=True, blank=True,
        help_text='The text that will be shown for the partner credit '
        ' e.g. "Translated by Sajan"')
    partner_credit_link = models.TextField(
        null=True, blank=True,
        help_text=' The link that the partner credit will redirect to e.g'
        '. https://www.google.co.za/')

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('show_partner_credit'),
                FieldPanel('partner_credit_description'),
                FieldPanel('partner_credit_link'),
            ],
            heading="Partner Credit",
        ),
        FieldPanel('banned_keywords_and_patterns'),
        FieldPanel('banned_names_with_offensive_language'),
    ]


class GemCommentReport(models.Model):
    user = models.ForeignKey(User)

    comment = models.ForeignKey(MoloComment)

    reported_reason = models.CharField(
        max_length=128, blank=False)
