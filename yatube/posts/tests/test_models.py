from django.contrib.auth import get_user_model
from django.core.validators import validate_unicode_slug
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост' * 15,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        task = PostModelTest.group
        expected_object_name = task.title
        self.assertEqual(expected_object_name, str(task))
        task = PostModelTest.post
        expected_object_name = task.text[:15]
        self.assertEqual(expected_object_name, str(task))

    def test_group_have_correct_slug(self):
        """Проверяем, наличие и корректность slug по умолчанию"""
        task = PostModelTest.group
        validate_unicode_slug(task.slug)
