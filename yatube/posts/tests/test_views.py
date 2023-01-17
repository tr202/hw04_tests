from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostContextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for _ in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост' + str(_),
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index',))
        page_obj_list = response.context.get('page_obj')
        for post in page_obj_list:
            self.assertIsInstance(post, Post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'},),)
        page_obj_list = response.context.get('page_obj')
        for post in page_obj_list:
            self.assertIsInstance(post, Post)
            self.assertIsInstance(post.group, Group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user},),)
        page_obj_list = response.context.get('page_obj')
        for post in page_obj_list:
            self.assertIsInstance(post, Post)
            self.assertEqual(post.author, self.user)

    def test_post_detail_show_correct_context(self):
        """Один пост отфильтрованный по id - detail."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk},),)
        page_obj_list = response.context.get('post'),
        self.assertEqual(len(page_obj_list), 1)
        self.assertIsInstance(page_obj_list[0], Post)
        self.assertEqual(page_obj_list[0].pk, self.post.pk)

    def test_post_edit_post_show_correct_context(self):
        """Форма редактирования поcта отфильтрованного по id."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk},),)
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

    def test_post_create_post_show_correct_context(self):
        """Форма создания поcта."""
        response = self.authorized_client.get(reverse('posts:post_create',),)
        context = response.context
        self.assertIsInstance(context.get('form'), PostForm)
        self.assertEqual(context.get('is_edit'), False)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_appear_greated_post_index(self):
        """Созданный пост появляется в index"""
        self.post = Post.objects.create(
            author=self.user,
            text='Пост проверки появления после создания',
            group=Group.objects.get(title='Тестовая группа'),
        )
        post_id = self.post.pk
        response = self.authorized_client.get(reverse('posts:index',),)
        page_obj_list = response.context.get('page_obj')
        contains = Post.objects.get(pk=post_id) in page_obj_list
        self.assertTrue(contains)

    def test_appear_greated_post_group(self):
        """Созданный пост появляется в group_list"""
        group = Group.objects.get(title='Тестовая группа')
        slug = group.slug
        self.post = Post.objects.create(
            author=self.user,
            text='Пост проверки появления после создания',
            group=group,
        )
        post_id = self.post.pk
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': slug},),)
        page_obj_list = response.context.get('page_obj')
        contains = Post.objects.get(pk=post_id) in page_obj_list
        self.assertTrue(contains)

    def test_appear_greated_post_profile(self):
        """Созданный пост появляется в profile"""
        group = Group.objects.get(title='Тестовая группа')
        self.post = Post.objects.create(
            author=self.user,
            text='Пост проверки появления после создания',
            group=group,
        )
        post_id = self.post.pk
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author},),)
        page_obj_list = response.context.get('page_obj')
        contains = Post.objects.get(pk=post_id) in page_obj_list
        self.assertTrue(contains)

    def test_greated_post_has_expected_group(self):
        """Проверка, что пост не попал в чужую группу."""
        group = Group.objects.get(title='Тестовая группа')
        self.post = Post.objects.create(
            author=self.user,
            text='Пост проверки соответствия группы',
            group=group,
        )
        self.assertEqual(Post.objects.get(pk=self.post.pk).group, group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for _ in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост' + str(_),
                group=cls.group
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Проверяем paginator на всех страницах"""
        pages = (
            reverse('posts:group_list', kwargs={'slug': 'test-slug'},),
            reverse('posts:profile', kwargs={'username': self.post.author},),
            reverse('posts:index',),
        )
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.authorized_client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class PostPagesTests(TestCase):
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

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk},):
                'posts/post_detail.html',
            reverse('posts:post_create',): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'},):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.post.author},):
                'posts/profile.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk},):
                'posts/create_post.html',
            reverse('posts:index',): 'posts/index.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
