from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from gem.models import GemSettings
from gem.tests.base import GemTestCaseMixin


@override_settings(SITE_LAYOUT_BASE='springster')
class GemSettingsTest(TestCase, GemTestCaseMixin):
    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.main2 = self.mk_main(
            title='main2', slug='main2', path='00010003', url_path='/main2/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)
        self.gem_setting = GemSettings.objects.create(
            site_id=self.main.get_site().id,
            bbm_ga_account_subdomain='bbm',
            bbm_ga_tracking_code='bbm_tracking_code',
            fb_enable_chat_bot=False,
        )

    def test_enable_fb_chat_bot(self):
        response = self.client.get(reverse('user_register'), follow=True)
        self.assertTemplateUsed(response, 'springster/base.html')
        self.assertContains(response, '<!-- Load Facebook SDK for JavaScript -->')

        self.gem_setting.fb_enable_chat_bot = True
        self.gem_setting.save()

        response = self.client.get(reverse('user_register'), follow=True)
        self.assertTemplateUsed(response, 'springster/base.html')
        self.assertNotContains(response, '<!-- Load Facebook SDK for JavaScript -->')
