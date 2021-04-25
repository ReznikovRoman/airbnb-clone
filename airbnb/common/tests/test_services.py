from django.test import SimpleTestCase

from ..services import create_name_with_prefix


class CommonServicesTests(SimpleTestCase):
    def test_create_name_with_prefix_no_prefix(self):
        result = create_name_with_prefix('name', '')
        self.assertEqual(result, '_name')

    def test_create_name_with_prefix_with_prefix(self):
        result = create_name_with_prefix('name', 'prefix')
        self.assertEqual(result, 'prefix_name')

    def test_create_name_with_prefix_with_underscore_prefix(self):
        result = create_name_with_prefix('name', 'prefix_')
        self.assertEqual(result, 'prefix_name')

    def test_create_name_with_prefix_no_name_no_prefix(self):
        result = create_name_with_prefix('', '')
        self.assertEqual(result, '_')

    def test_create_name_with_prefix_no_name_with_prefix(self):
        result = create_name_with_prefix('', 'prefix')
        self.assertEqual(result, 'prefix_')

    def test_create_name_with_prefix_no_name_with_prefix_with_underscore(self):
        result = create_name_with_prefix('', 'prefix_')
        self.assertEqual(result, 'prefix_')
