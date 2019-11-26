import mock

from django.core.files import File
from django.template import Context
from django.test import RequestFactory, TestCase

from wagtail.core.rich_text import RichText

from molo.core.models import MoloMedia
from gem.tests.base import GemTestCaseMixin
from gem.templatetags.gem_tags import (
    mimetype,
    is_content,
    idfromlabel,
    bbm_share_url,
    seconds_to_time,
    parent_section_depth,
    smart_truncate_chars,
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

    def test_truncates_richtext(self):
        max_length = 15
        string = RichText('This is a test string which is long')
        result = smart_truncate_chars(string, max_length)
        self.assertTrue(len(result) <= max_length)

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


class TestIsContentTemplateFilter(GemTestCaseMixin, TestCase):
    def test_filter(self):
        page = self.mk_main(
            title='main1',
            slug='main1',
            path='00010002',
            url_path='/main1/'
        )
        self.assertTrue(is_content(page, "main1"))
        self.assertFalse(is_content(page, "NotWatch"))


class TestParentSectionDepth(GemTestCaseMixin, TestCase):
    def test_filter(self):
        depth = 2
        main_page = self.mk_main(
            title='main1',
            slug='main1',
            path='00010002',
            url_path='/main1/'
        )
        article = self.mk_article(main_page)

        self.assertEqual(
            parent_section_depth(article, depth=depth).pk,
            main_page.pk
        )

        self.assertEqual(
            parent_section_depth(article, depth=depth).depth,
            depth
        )


class TestSecondsToTime(TestCase):

    def test_seconds_to_time(self):
        self.assertEqual(seconds_to_time(None), '')
        self.assertEqual(seconds_to_time(121), '02:01')
        self.assertEqual(seconds_to_time(3601), '1:00:01')


class TestMimeType(TestCase):

    def test_mimetype(self):
        file_mock = mock.MagicMock(spec=File)
        file_mock.name = 'test.txt'
        file_model = MoloMedia.objects.create(
            file=file_mock, title=file_mock.name,
            duration=200
        )
        self.assertEqual(mimetype(file_model.file), 'text/plain')

        file_model.file = None
        self.assertEqual(mimetype(file_model.file), '')
