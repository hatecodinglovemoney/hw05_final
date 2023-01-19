import time

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User

USERNAME = "NoName"
URL_INDEX = reverse("posts:index")
CACHE_TIME = 20


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )

    def test_cache_index(self):
        """Запись остаётся на главной странице после удаления 20 секунд"""
        response_before = self.guest_client.get(URL_INDEX)
        Post.objects.filter(pk=self.post.pk).delete()
        response = self.guest_client.get(URL_INDEX)
        self.assertEqual(response.content, response_before.content)
        time.sleep(CACHE_TIME)
        response_after = self.client.get(URL_INDEX)
        self.assertNotEqual(response.content, response_after.content)
