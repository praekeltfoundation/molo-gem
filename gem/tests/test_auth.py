from django.core import mail
from django.urls import reverse
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import Group, Permission

from allauth.socialaccount.models import SocialLogin, SocialAccount
from wagtail.core import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

from gem.models import Invite
from gem.tests.base import GemTestCaseMixin
from gem.adapter import StaffUserSocialAdapter, StaffUserAdapter


urlpatterns = [
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'', include(wagtail_urls)),

]


class TestAllAuth(GemTestCaseMixin, TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='superuser', email='superuser@email.com', password='pass')
        self.main = self.mk_main(
            title='main1', slug='main1',
            path='00010002', url_path='/main1/'
        )
        self.site = self.main.get_site()
        self.user.profile.admin_sites.add(self.site)
        self.client = Client(SERVER_NAME=self.site.hostname)
        self.factory = RequestFactory()

    @override_settings(ENABLE_ALL_AUTH=True)
    def test_admin_login_view(self):
        res = self.client.get(reverse('wagtailadmin_login'))
        self.assertEqual(res.status_code, 200)
        # toDo: find a better way to handle conditional urls patterns,
        #  because django only loads them once on server instantiation
        # self.assertTemplateUsed(res, 'wagtailadmin/social_login.html')

    @override_settings(ENABLE_ALL_AUTH=True)
    def test_admin_views_authed_user(self):
        self.client.force_login(self.user)

        res = self.client.get(reverse('wagtailadmin_login'))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(settings.ENABLE_ALL_AUTH, True)
        self.assertEqual(res.url, '/admin/')

        res = self.client.get(res.url)
        self.assertEqual(res.status_code, 200)

    @override_settings(ENABLE_ALL_AUTH=True)
    def test_invite_create_view(self):
        req = self.factory.get("/")
        req.user = self.user

        self.client.force_login(self.user)
        url = '/admin/gem/invite/create/'
        data = {
            'email': 'testinvite@test.com'
        }
        res = self.client.post(url, data=data, request=req)

        subject = '{}: Admin site invitation'.format(self.site)
        self.assertEqual(res.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertEqual(mail.outbox[0].from_email, 'no-reply@gehosting.org')

        self.assertTrue(
            Invite.objects.filter(user=self.user).exists())

    @override_settings(ENABLE_ALL_AUTH=True)
    def test_invite_edit_view(self):
        data = {
            'email': 'testinvite@test.com'
        }
        req = self.factory.get("/")
        req.user = self.user

        invite = Invite.objects.create(
            email=data['email'], user=self.user, site=self.site)
        self.client.force_login(self.user)

        url = '/admin/gem/invite/edit/{}/'.format(invite.pk)
        res = self.client.post(url, request=req)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, data['email'])
        res = self.client.post(url, data=data, request=req)

        self.assertEqual(res.status_code, 302)
        # Note: email sent on creation of invite object by signal
        # testing that a duplicate email was not sent on update
        self.assertEqual(len(mail.outbox), 1)

    def test_staff_social_adaptor(self):
        """
        Test a front-end user getting an invite to admin site
        """
        request = self.factory.get("/")

        adaptor = StaffUserSocialAdapter(request=request)
        user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='pass'
        )
        sociallogin = SocialLogin(user=user)
        group = Group.objects.filter().first()
        perm = Permission.objects.filter().first()

        self.assertFalse(adaptor.is_open_for_signup(request, sociallogin))

        invite = Invite.objects.create(
            email=user.email, user=self.user, site=self.site)
        invite.groups.add(group)
        invite.permissions.add(perm)

        self.assertFalse(user.groups.all().exists())
        self.assertFalse(user.user_permissions.all().exists())

        adaptor.add_perms(user)
        invite.refresh_from_db()
        self.assertTrue(invite.is_accepted)
        self.assertTrue(user.groups.all().exists())
        self.assertTrue(user.user_permissions.all().exists())

        user.delete()
        invite.delete()

    def test_staff_social_adaptor_new_user(self):
        """
        Test a new user getting an invite to admin site
        """
        request = self.factory.get("/")

        adaptor = StaffUserSocialAdapter(request=request)
        user = get_user_model()(
            username='testuser',
            email='testuser@email.com',
            password='pass'
        )
        sociallogin = SocialLogin(user=user)
        group = Group.objects.filter().first()
        perm = Permission.objects.filter().first()

        self.assertFalse(user.pk)
        self.assertFalse(adaptor.is_open_for_signup(request, sociallogin))

        invite = Invite.objects.create(
            email=user.email, user=self.user, site=self.site)
        invite.groups.add(group)
        invite.permissions.add(perm)

        adaptor.add_perms(user)
        invite.refresh_from_db()
        self.assertTrue(invite.is_accepted)
        self.assertTrue(user.groups.all().exists())
        self.assertTrue(user.user_permissions.all().exists())

        user.delete()
        invite.delete()

    def test_staff_social_adaptor_staff(self):
        """
        Test a regular staff login
        """
        request = self.factory.get("/")
        adaptor = StaffUserSocialAdapter(request=request)
        user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='pass',
            is_staff=True,
        )
        sociallogin = SocialLogin(user=user)
        group = Group.objects.filter().first()
        perm = Permission.objects.filter().first()

        user.groups.add(group)
        user.user_permissions.add(perm)
        self.assertFalse(adaptor.is_open_for_signup(request, sociallogin))

        adaptor.add_perms(user)
        self.assertTrue(user.groups.all().exists())
        self.assertTrue(user.user_permissions.all().exists())

        user.delete()

    def test_staff_social_adaptor_superuser(self):
        """
        Test a superuser login
        """
        request = self.factory.get("/")
        adaptor = StaffUserSocialAdapter(request=request)
        user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            is_superuser=True,
            password='pass'
        )
        sociallogin = SocialLogin(user=user)
        self.assertFalse(adaptor.is_open_for_signup(request, sociallogin))
        self.assertFalse(user.groups.all().exists())
        self.assertFalse(user.user_permissions.all().exists())

        adaptor.add_perms(user)
        self.assertFalse(user.groups.all().exists())
        self.assertFalse(user.user_permissions.all().exists())

        user.delete()

    def test_staff_user_adapter_new_user(self):
        adaptor = StaffUserAdapter()
        user = get_user_model()(
            username='testuser',
            email='testuser@email.com',
            password='pass'
        )
        request = RequestFactory().post(
            data={
                'username': user.username,
                'password': user.password
            }, path=reverse('wagtailadmin_login'))
        self.assertFalse(adaptor.is_open_for_signup(request, None))

    def test_staff_user_adapter_front_end_user(self):
        adaptor = StaffUserAdapter()
        user = get_user_model().objects.create(
            username='testuser',
            email='testuser@email.com',
            password='pass'
        )
        request = RequestFactory().post(
            data={
                'username': user.username,
                'password': user.password
            }, path=reverse('wagtailadmin_login'))
        self.assertFalse(adaptor.is_open_for_signup(request, None))

    def test_staff_user_adapter_staff_user(self):
        adaptor = StaffUserAdapter()
        user = get_user_model().objects.create(
            username='testuser',
            email='testuser@email.com',
            is_staff=True,
            password='pass'
        )
        request = RequestFactory().post(
            data={
                'username': user.username,
                'password': user.password
            }, path=reverse('wagtailadmin_login'))
        self.assertFalse(adaptor.is_open_for_signup(request, None))

    def test_staff_user_adapter_staff_user_perms(self):
        adaptor = StaffUserAdapter()
        group = Group.objects.filter().first()
        perm = Permission.objects.filter().first()
        user = get_user_model().objects.create(
            username='testuser',
            email='testuser@email.com',
            is_staff=True,
            password='pass'
        )
        user.groups.add(group)
        user.user_permissions.add(perm)
        request = RequestFactory().post(
            data={
                'username': user.username,
                'password': user.password
            }, path=reverse('wagtailadmin_login'))
        self.assertFalse(adaptor.is_open_for_signup(request, None))

    def test_user_delete(self):
        user = get_user_model().objects.create(
            username='testuser',
            email='testuser@email.com',
            is_staff=True,
            password='pass'
        )
        SocialAccount.objects.create(
            user=user, provider='google', uid='1')
        user.delete()
        self.assertFalse(
            SocialAccount.objects.filter(user=user)
        )


class TestAllAuthDisabled(GemTestCaseMixin, TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='superuser', email='superuser@email.com', password='pass')
        self.main = self.mk_main(
            title='main1', slug='main1',
            path='00010002', url_path='/main1/'
        )
        self.site = self.main.get_site()
        self.user.profile.admin_sites.add(self.site)
        self.factory = RequestFactory()

    @override_settings(ENABLE_ALL_AUTH=False)
    def test_login_all_auth_disabled(self):
        res = self.client.get(reverse('wagtailadmin_login'))
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, '<span class="fa fa-google"></span>Google')
