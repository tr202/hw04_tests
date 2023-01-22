from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from mixer.backend.django import mixer

from posts.models import Group, Post, User

from .config_tests import (AUTHORISATION_PAGES_CASES,
                           UNEXISTING_URL)
from .utils import get_obj_test_urls


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.user_no_post_author = mixer.blend(User)
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, author=cls.user, group=cls.group)
        cls.test_urls = get_obj_test_urls(cls)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_no_post_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_no_post_author.force_login(
            self.user_no_post_author)
        self.clients = (
            self.guest_client, self.authorized_client_no_post_author,)

    def test_unexisting_page_get_404(self):
        """Несуществующая страница"""
        response = self.guest_client.get(UNEXISTING_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_authorisation_cases(self):
        """Запросы правильно переадресуются"""
        pages = AUTHORISATION_PAGES_CASES
        for client, page in zip(self.clients, pages):
            with self.subTest():
                response = client.get(self.test_urls[page].url)
                self.assertRedirects(
                    response, self.test_urls[page].redirect_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, item in self.test_urls.items():
            with self.subTest(name=name, address=item.url):
                response = self.authorized_client.get(item.url)
            self.assertTemplateUsed(response, item.template)

    def test_namespase_template(self):
        """Проверка reverse namespase."""
        for name, item in self.test_urls.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(
                    reverse(
                        f'{item.app_name}:{item.page_name}',
                        kwargs=item.kwargs))
                self.assertTemplateUsed(response, item.template)
