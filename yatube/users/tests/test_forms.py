from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_form_create_user(self):
        """Create_user_form увеличивает количество пользователей"""
        exists_users_count = User.objects.count()
        self.guest_client.post(
            reverse('users:signup',),
            data={
                'username': 'test',
                'password1': '@_1234-very_diff_password',
                'password2': '@_1234-very_diff_password',
                'first_name': 'tested',
                'last_name': 'user',
                'email': 'user@example.dom',
            },
            follow=True,
        )
        self.assertTrue(User.objects.count() > exists_users_count)
