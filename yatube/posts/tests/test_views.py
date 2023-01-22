from django import forms
from django.conf import settings as s
from django.test import Client, TestCase

from mixer.backend.django import mixer

from posts.forms import PostForm
from posts.models import Group, Post, User

from .config_tests import (PAGES_SHOW_SINGLE_POST,
                           PAGES_USES_CREATE_TEMPLATE,
                           PAGE_SHOW_CORRECT_CONTEXT,
                           PAGINATOR_TEST_PAGES,
                           POST_APPEAR_ON_PAGES,)
from .utils import create_posts, get_obj_test_urls


class PostContextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.group = mixer.blend(Group)
        cls.test_urls = get_obj_test_urls(cls, POST_APPEAR_ON_PAGES)
        posts = create_posts(s.PAGE_POSTS_COUNT, cls)
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.last()

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        pages = PAGE_SHOW_CORRECT_CONTEXT
        urls = get_obj_test_urls(self, pages)
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(urls[page].url)
            page_obj_list = response.context.get('page_obj')
            for post in page_obj_list:
                self.assertEqual(post.group, self.group)
                self.assertEqual(post.author, self.user)
                self.assertIsInstance(post, Post)

    def test_pages_show_single_post(self):
        """Страницы создания и редактирования"""
        pages = PAGES_USES_CREATE_TEMPLATE
        urls = get_obj_test_urls(self, pages)
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(urls[page].url)
            context = response.context
            self.assertIsInstance(context.get('form'), PostForm)
        self.assertEqual(context.get('post_id'), self.post.pk)
        self.assertEqual(context.get('is_edit'), True)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_pages_only_show_single_post(self):
        """Один пост отфильтрованный по id - detail."""
        pages = PAGES_SHOW_SINGLE_POST
        urls = get_obj_test_urls(self, pages)
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(urls[page].url)
        page_obj_list = response.context.get('post'),
        self.assertEqual(len(page_obj_list), 1)
        self.assertIsInstance(page_obj_list[0], Post)
        self.assertEqual(page_obj_list[0].pk, self.post.pk)

    def test_appear_greated_post(self):
        """Созданный пост появляется на страницах"""
        pages = POST_APPEAR_ON_PAGES
        self.post = create_posts(1, self)[0]
        Post.save(self.post)
        urls = get_obj_test_urls(self, pages)
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(urls[page].url)
            page_obj_list = response.context.get('page_obj')
            contains = self.post in page_obj_list
            self.assertTrue(contains)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.group = mixer.blend(Group)
        cls.test_urls = get_obj_test_urls(cls, PAGINATOR_TEST_PAGES)
        posts = create_posts(s.PAGE_POSTS_COUNT * 2, cls)
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Проверяем paginator на всех страницах"""
        for page in PAGINATOR_TEST_PAGES:
            with self.subTest(page=page):
                response = self.authorized_client.get(self.test_urls[page].url)
                self.assertEqual(
                    len(response.context['page_obj']), s.PAGE_POSTS_COUNT)
                response = self.authorized_client.get(
                    self.test_urls[page].url + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), s.PAGE_POSTS_COUNT)
