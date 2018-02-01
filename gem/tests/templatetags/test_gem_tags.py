from django.test import RequestFactory, TestCase

from gem.templatetags.gem_tags import (
    is_via_freebasics,
    smart_truncate_chars,
)


class TestIsViaFreebasics(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_returns_true_if_internetorg_in_httpvia(self):
        request = self.request_factory.get('/', HTTP_VIA='Internet.org')
        context = {'request': request}
        self.assertTrue(is_via_freebasics(context))

    def test_returns_true_if_internetorgapp_in_user_agent(self):
        request = self.request_factory.get(
            '/',
            HTTP_USER_AGENT='InternetOrgApp',
        )
        context = {'request': request}
        self.assertTrue(is_via_freebasics(context))

    def test_returns_true_if_true_in_xiorgsfbs(self):
        request = self.request_factory.get('/', HTTP_X_IORG_FBS='true')
        context = {'request': request}
        self.assertTrue(is_via_freebasics(context))


class TestSmartTruncateChars(TestCase):
    def test_returns_original_value_if_less_than_length(self):
        result = smart_truncate_chars('Example string', 99)
        self.assertEqual(result, 'Example string')

    def test_truncates_based_on_spaces(self):
        string = 'This is a test string which is long'
        result = smart_truncate_chars(string, 15)
        self.assertEqual(result, 'This is a test...')

    def test_strips_to_defined_length_when_no_spaces(self):
        string = 'Thisisateststringwhichislong'
        result = smart_truncate_chars(string, 15)
        self.assertEqual(result, 'Thisisateststr...')
