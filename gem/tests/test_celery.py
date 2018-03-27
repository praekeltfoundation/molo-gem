from django.test import TestCase

from mock import patch


class TestCelery(TestCase):
    @patch('django.core.management.call_command')
    def test_ensure_search_index_doesnt_call_command(self, call_command_patch):
        from gem.celery import ensure_search_index_updated
        ensure_search_index_updated('sender', 'instance')

        call_command_patch.assert_not_called()
