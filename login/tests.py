from django.test import TestCase, Client
from django.db import IntegrityError
from django.urls import reverse
from .models import User


class LoginTest(TestCase):
    """ Test Login App """

    def setUp(self):
        """ Before every test """
        self.client = Client()
        self.login_url = reverse('login:connect')
        self.join_url = reverse('login:join')
        self.mypage_url = reverse('login:mypage')
        self.logout_url = reverse('login:disconnect')
        self.user = User.objects.create(email='user_test@django.test')
        self.user.set_password('@december2019')
        self.user.save()

    def test_login_url_and_template(self):
        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(response.status_code, 200)

    def test_login_valid(self):
        response = self.client.post(self.login_url, {
            'username': 'user_test@django.test',
            'password': '@december2019'
        })
        self.assertRedirects(
            response, '/', status_code=302, target_status_code=200)

    def test_login_invalid(self):
        response = self.client.post(self.login_url, {
            'username': 'user_test@django.test',
            'password': '@december'
        })
        self.assertEqual(response.status_code, 200)

    def test_join_url_and_template(self):
        response = self.client.get(self.join_url)
        self.assertTemplateUsed(response, 'registration/join.html')
        self.assertEqual(response.status_code, 200)

    def test_join_form_valid(self):
        response = self.client.post(self.join_url, {
            'email': 'new_user@django.fr',
            'password1': '@jesuisNouveau',
            'password2': '@jesuisNouveau'
        })
        self.assertRedirects(
            response, '/', status_code=302, target_status_code=200)

    def test_join_form_invalid(self):
        response = self.client.post(self.join_url, {
            'email': 'new_user',
            'password1': '@jesuisNouveau',
            'password2': '@jesuisNouveau200'
        })
        self.assertEqual(response.status_code, 200)

    def test_join_create_user(self):
        new_user = 'new_user@django.fr'
        user = User.objects.create(email=new_user)
        user.set_password('@jesuisNouveau')
        user.save()

        user = User.objects.get(email=new_user)

        self.assertIsInstance(user, User)
        self.assertEqual(str(user), new_user)

    def test_join_user_already_exist(self):
        try:
            user = User.objects.create(email='user_test@django.test')
            user.set_password('@jesuisNouveau')
            user.save()

        except IntegrityError:
            user = False

        self.assertFalse(user)

    def test_mypage_url_and_template(self):
        response = self.client.get(self.mypage_url)
        self.assertTemplateUsed(response, 'registration/mypage.html')
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.get(self.logout_url)
        self.assertRedirects(
            response, '/', status_code=302, target_status_code=200)
