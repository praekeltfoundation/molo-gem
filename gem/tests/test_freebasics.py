import json
from six import b
from django.test import TestCase, Client

from gem.tests.base import GemTestCaseMixin
from molo.core.models import SectionIndexPage, MoloMedia
from django.core.files.base import ContentFile


class FreebasicsContentTest(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

        self.yourmind = self.mk_section(
            SectionIndexPage.objects.child_of(self.main).first(),
            title='Your mind')
        self.article = self.mk_article(self.yourmind)

    def test_detect_freebasics(self):
        fake_file = ContentFile(b("media"))
        fake_file.name = 'media.mp3'
        self.media = MoloMedia.objects.create(
            title="Test Media", file=fake_file, duration=100, type="audio")
        self.article.body = json.dumps([{
            'type': 'media',
            'value': self.media.id,
        }])
        self.article.save_revision().publish()
        response = self.client.get(self.article.url)
        self.assertContains(response, 'Download Audio')

        client = Client(
            HTTP_VIA='Internet.org', HTTP_HOST=self.main.get_site().hostname)
        response = client.get(self.article.url)
        self.assertNotContains(response, 'Download Audio')

        client = Client(
            HTTP_X_IORG_FBS='true', HTTP_HOST=self.main.get_site().hostname)
        response = client.get(self.article.url)

        self.assertNotContains(response, 'Download Audio')

        client = Client(
            HTTP_USER_AGENT='Mozilla/5.0 (Linux; Android 5.1;'
            ' VFD 100 Build/LMY47I; wv) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Version/4.0 Chrome/50.0.2661.86'
            ' Mobile Safari/537[FBAN/InternetOrgApp; FBAV/7.0;]',
            HTTP_HOST=self.main.get_site().hostname)
        response = client.get(self.article.url)

        self.assertNotContains(response, 'Download Audio')

        client = Client(
            HTTP_VIA='Internet.org',
            HTTP_X_IORG_FBS='true',
            HTTP_USER_AGENT='Mozilla/5.0 (Linux; Android 5.1;'
            ' VFD 100 Build/LMY47I; wv) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Version/4.0 Chrome/50.0.2661.86'
            ' Mobile Safari/537[FBAN/InternetOrgApp; FBAV/7.0;]',
            HTTP_HOST=self.main.get_site().hostname)
        response = client.get(self.article.url)

        self.assertNotContains(response, 'Download Audio')
