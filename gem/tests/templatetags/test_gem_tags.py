from django.test import TestCase

from gem.templatetags.gem_tags import (
    smart_truncate_chars,
)


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
