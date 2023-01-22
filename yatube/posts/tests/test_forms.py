from django.test import Client, TestCase
from django.urls import reverse

from mixer.backend.django import mixer

from posts.models import Group, Post, User

from .utils import get_obj_test_urls


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.user_no_post_author = mixer.blend(User)
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, author=cls.user, group=cls.group)
        cls.test_urls = get_obj_test_urls(cls)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_edit_post_change_post(self):
        """Edit_post изменяет пост"""
        post_text = Post.objects.get(pk=self.post.pk).text
        self.authorized_client.post(
            reverse(f"{self.test_urls['post_edit'].app_name}"
                    f":{self.test_urls['post_edit'].page_name}",
                    kwargs=self.test_urls['post_edit'].kwargs),
            data={'text': post_text + 'changed_part'}, follow=True)
        self.assertNotEqual(post_text, Post.objects.get(pk=self.post.pk).text)

    def test_form_create_post(self):
        """Create_post_form увеличивает количество постов"""
        exists_post_count = Post.objects.count()
        self.authorized_client.post(
            reverse(
                f"{self.test_urls['post_create'].app_name}"
                f":{self.test_urls['post_create'].page_name}",),
            data={'text': 'Проверка'},
            follow=True,
        )
        self.assertTrue(Post.objects.count() > exists_post_count)
        latest_post = Post.objects.latest('pub_date')
        self.assertEqual(latest_post.text, 'Проверка')
        self.assertEqual(latest_post.author, self.user)
