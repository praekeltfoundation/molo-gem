from django.test import TestCase

from gem.wagtailsearch.backends.base import BaseSearchBackend


class TestWagtailSearchBase(TestCase):
    def test_base_search_backend_get_index_for_model_returns_none(self):
        backend = BaseSearchBackend({})
        self.assertEqual(backend.get_index_for_model(None), None)
