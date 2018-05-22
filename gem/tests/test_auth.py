from django.test import TestCase
from django.contrib.auth import get_user_model
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import Main, Languages, SiteLanguageRelation
from gem.backends import GirlEffectOIDCBackend, _update_user_from_claims


class TestOIDCAuthIntegration(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

    def test_filter_users_by_claims(self):
        claims = {'sub': 'this1234is5678uuid'}
        user = get_user_model().objects.create(
            username='test_user', password='pass')
        user.profile.auth_service_uuid = claims['sub']
        user.profile.save()
        backend = GirlEffectOIDCBackend()
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEqual(returned_user[0].pk, user.pk)

        # it should return none if user does not DoesNotExist
        claims["sub"] = 'thisisnotavaliduuid'
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEquals(returned_user.count(), 0)

    def test_filter_users_by_claims_migrated_user(self):
        claims = {'sub': 'this1234is5678uuid'}
        user = get_user_model().objects.create(
            username='test_user', password='pass')
        claims['migration_information'] = {'user_id': user.id}
        backend = GirlEffectOIDCBackend()
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEqual(returned_user[0].pk, user.pk)

        # it should return none if user does not DoesNotExist
        claims['migration_information'] = {'user_id': -2}
        returned_user = backend.filter_users_by_claims(claims)
        self.assertEquals(returned_user.count(), 0)

    def test_update_user_from_claims(self):
        roles = ['example role', ]
        claims = {
            'roles': roles,
            'given_name': 'testgivenname',
            'family_name': 'testfamilyname',
            'email': 'test@email.com',
            'sub': 'this1234is5678uuid'}
        user = get_user_model().objects.create(
            username='testuser', password='password')
        self.assertFalse(user.is_staff)
        _update_user_from_claims(user, claims)
        user = user.refresh_from_db()
        self.assertTrue(user.is_superuser)
        self.assertEquals(user.first_name, 'testgivenname')
        self.assertEquals(user.last_name, 'testfamilyname')
        self.assertEquals(user.email, 'test@email.com')
        self.assertEquals(user.profile.auth_service_uuid, 'this1234is5678uuid')
