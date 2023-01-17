from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_no_post_author = User.objects.create_user(
            username='auth_no_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост' * 15,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_no_post_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_no_post_author.force_login(
            self.user_no_post_author)
        self.clients = (self.guest_client, self.authorized_client,)

    def test_author_get_create_post_with_edit(self):
        """Автору показывается create_post/edit/"""
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_authorized_no_author_get_redirect(self):
        """Авторизованному но не автору отдается редирект"""
        response = self.authorized_client_no_post_author.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.pk}/')

    def test_create_post(self):
        """Авторизованному пользователю показывается /create/"""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_guest_client_get_redirect_to_login(self):
        """Неавторизованный получает редирект на /auth/login/"""
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/')

    def test_unexisting_url_get_404(self):
        """Несуществующий url получает 404."""
        for client in self.clients:
            with self.subTest(client=client):
                response = client.get('/unexisting_page/')
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_names_templates = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }

        for client in self.clients:
            for address, template in url_names_templates.items():
                with self.subTest(address=address):
                    response = client.get(address)
                    self.assertTemplateUsed(response, template)
