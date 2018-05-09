from django.contrib.auth.models import User
from django.db import models

from molo.commenting.models import MoloComment
from molo.core.models import BannerPage, BannerIndexPage

from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class GemTextBanner(BannerPage):
    parent_page_types = ['core.BannerIndexPage']
    hide_on_freebasics = models.BooleanField(default=False)


GemTextBanner.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('subtitle'),
    ImageChooserPanel('banner'),
    PageChooserPanel('banner_link_page'),
    FieldPanel('external_link'),
    FieldPanel('hide_on_freebasics')
]


BannerIndexPage.subpage_types = ['core.BannerPage', 'gem.GemTextBanner']


@register_setting
class GemSettings(BaseSetting):
    banned_keywords_and_patterns = models.TextField(
        verbose_name='Banned Keywords and Patterns',
        null=True,
        blank=True,
        help_text="Banned keywords and patterns for comments, separated by a"
                  " line a break. Use only lowercase letters for keywords."
    )

    moderator_name = models.TextField(
        verbose_name='Moderator Name',
        null=True,
        blank=True,
        help_text="This is the name that will appear on the front end"
                  " when a moderator responds to a user"
    )

    banned_names_with_offensive_language = models.TextField(
        verbose_name='Banned Names With Offensive Language',
        null=True,
        blank=True,
        help_text="Banned names with offensive language, separated by a"
                  " line a break. Use only lowercase letters for keywords."
    )

    show_join_banner = models.BooleanField(
        default=False,
        help_text='When true, this will show the join banner on the '
        'homepage.')

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
    bbm_ga_tracking_code = models.TextField(
        null=True, blank=True,
        help_text='Tracking code for additional Google Analytics account '
                  'to divert traffic that matches a specific subdomain.')
    # FIXME: Remove bbm_ga_account_subdomain and its uses in middleware once
    # BBM South Africa and Nigeria are changed to use `/bbm/` cookie endpoint.
    bbm_ga_account_subdomain = models.TextField(
        default='bbm',
        help_text=('Subdomain prefix to seperate traffics data for Google '
                   'Analytics. Defaults to "bbm"'))

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('show_partner_credit'),
                FieldPanel('partner_credit_description'),
                FieldPanel('partner_credit_link'),
            ],
            heading="Partner Credit",
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_join_banner'),
            ],
            heading="Join Banner",
        ),
        FieldPanel('moderator_name'),
        FieldPanel('banned_keywords_and_patterns'),
        FieldPanel('banned_names_with_offensive_language'),
        MultiFieldPanel(
            [
                FieldPanel('bbm_ga_tracking_code'),
                FieldPanel('bbm_ga_account_subdomain'),
            ],
            heading="BBM",
        ),
    ]


class GemCommentReport(models.Model):
    user = models.ForeignKey(User)

    comment = models.ForeignKey(MoloComment)

    reported_reason = models.CharField(
        max_length=128, blank=False)
