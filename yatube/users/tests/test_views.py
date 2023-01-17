from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_unautorized_users_urls(self):
        """Неавторизованые Users URL."""
        unautorized_urls_templates = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/password_reset_form.html': reverse(
                'users:password_reset_form'),
            'users/password_reset_done.html': reverse(
                'users:password_reset_done'),
            'users/logged_out.html': reverse('users:logout'),
        }
        for template, reverse_name in unautorized_urls_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_autorized_users_urls(self):
        """Авторизованые Users URL."""
        autorized_urls_templates = {
            'users/password_change_form.html': reverse(
                'users:password_change_form'),
            'users/password_change_done.html': reverse(
                'users:password_change_done'),
            'users/password_reset_complete.html': reverse(
                'users:password_reset_confirm'),
        }
        for template, reverse_name in autorized_urls_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
