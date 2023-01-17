from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.post_id = cls.post.pk

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_edit_post_change_post(self):
        """Edit_post изменяет пост"""
        post_text = Post.objects.get(pk=self.post_id).text
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk},),
            data={'text': post_text + 'changed_part'},
            follow=True,
        )
        self.assertNotEqual(post_text, Post.objects.get(pk=self.post_id).text)

    def test_form_create_post(self):
        """Create_post_form увеличивает количество постов"""
        exists_post_count = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_create',),
            data={'text': 'Проверка'},
            follow=True,
        )
        self.assertTrue(Post.objects.count() > exists_post_count)
