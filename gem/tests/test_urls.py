from django.test import TestCase
from django.test.client import Client

from gem.tests.base import GemTestCaseMixin


class TestSitemapsUrls(TestCase, GemTestCaseMixin):

    def setUp(self):
        self.main = self.mk_main(
            title='main2', slug='main2', path='00010002', url_path='/main2/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

    def test_sitemaps(self):
        response = self.client.get('/sitemap.xml')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.main.get_site().hostname)

    def test_robots(self):
        response = self.client.get('/robots.txt')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.main.get_site().hostname)
