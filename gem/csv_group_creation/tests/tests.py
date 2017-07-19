import pytest
import io

from django.core.files.base import ContentFile
from django.test import Client, RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


@pytest.mark.django_db
class TestCSVGroupCreation(TestCase):
    def setUp(self):
        self.client = Client()

        # Create admin user
        self.user = get_user_model().objects.create_superuser(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.client = Client()
        self.client.login(username=self.user.username, password='tester')

        self.users = []
        # Add a few users
        for n in range(10):
            self.users.append(get_user_model().objects.create_user(
                username='tester%d' % n,
                email='tester%d@example.com' % n,
                password='tester'))

    def test_url_works(self):
        response = self.client.get('/admin/csv-group-creation/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Add group via CSV file', response.content)

    def test_group_creation(self):
        # Create string with all usernames from self.users
        csv_file = ''
        for user in self.users:
            csv_file += '%s,\n' % user.username

        # Submit the form
        self.client.post('/admin/csv-group-creation/', {
            'name': 'test group',
            'csv_file': ContentFile(csv_file, 'users.csv')
        })

        # Make sure group of given name has been created
        try:
            group = Group.objects.get(name='test group')
        except Group.DoesNotExist:
            self.fail('Group has not been created.')

        # Make sure users from CSV file has been added to the created group
        self.assertEqual(
            group.user_set.filter(id__in=[u.id for u in self.users]).count(),
            len(self.users))
