from django.template import Context
from django.test import RequestFactory, TestCase

from gem.templatetags.gem_tags import (
    bbm_share_url,
    smart_truncate_chars,
    idfromlabel, seconds_to_time
)


class TestBbmShareUrl(TestCase):
    def test_returns_url_prefixed_with_bbm(self):
        request = RequestFactory().get('/section/one/')
        context = Context({'request': request})
        result = bbm_share_url(context)
        self.assertEqual(result, 'http://testserver/bbm/section/one/')


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


class TestIdFromLabelTag(TestCase):

    def test_returns_expected_value(self):
        self.assertEqual(idfromlabel('I have visited'), 'id_ihavevisited')
        self.assertEqual(idfromlabel('I have visited . . .'),
                         'id_ihavevisited')
        self.assertEqual(idfromlabel('I have visited 1'), 'id_ihavevisited1')


class TestSecondsToTime(TestCase):

    def test_seconds_to_time(self):
        self.assertEqual(seconds_to_time(None), '')
        self.assertEqual(seconds_to_time(121), '02:01')
