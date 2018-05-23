# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone

from gem.models import GemCommentReport
from gem.tests.base import GemTestCaseMixin
from molo.commenting.models import MoloComment
from molo.core.models import SectionIndexPage


class TestCommentReportingModelAdmin(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.section = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='section')
        self.article = self.mk_article(self.section, title='article 1',
                                       subtitle='article 1 subtitle',
                                       slug='article-1')
        self.user = User.objects.create_superuser(
            'testadmin', 'testadmin@example.org', 'testadmin')
        self.content_type = ContentType.objects.get_for_model(self.article)
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
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
