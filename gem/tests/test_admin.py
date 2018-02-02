# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone

from gem.models import GemCommentReport

from molo.commenting.models import MoloComment
from molo.core.models import Languages, SiteLanguageRelation, Main
from molo.core.tests.base import MoloTestCaseMixin


class TestCommentReportingModelAdmin(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.section = self.mk_section(
            self.section_index, title='section')
        self.article = self.mk_article(self.section, title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')
        self.user = User.objects.create_superuser(
            'testadmin', 'testadmin@example.org', 'testadmin')
        self.content_type = ContentType.objects.get_for_model(self.article)
        self.client = Client()
        self.client.login(username='testadmin', password='testadmin')

    def mk_comment(self, comment, parent=None):
        return MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=self.article.pk,
            content_object=self.article,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            parent=parent,
            submit_date=timezone.now())

    def report_comment(self, comment, reason):
        GemCommentReport.objects.create(
            user=comment.user, comment=comment,
            reported_reason=reason)

    def test_comment_report_reasons_displaying_correctly(self):
        comment_1 = self.mk_comment('comment 1 text')
        self.report_comment(comment_1, reason='bad sample text')
        self.report_comment(comment_1, reason='bad sample text')
        self.report_comment(comment_1, reason='lack of humour')

        response = self.client.get('/admin/commenting/molocomment/')
        self.assertContains(
            response, 'bad sample text, (2), lack of humour, (1)')
