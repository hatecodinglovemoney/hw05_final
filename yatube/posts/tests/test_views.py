from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import POSTS_ON_PAGE_NUMB
from ..models import Follow, Group, Post, User

USERNAME = "NoName"
ANOTHER_USERNAME = "NoName2"
GROUP_SLUG = "test-slug"
ANOTHER_SLUG = "test-slug2"
INDEX_URL = reverse("posts:index")
GROUP_URL = reverse("posts:group_list", args=[GROUP_SLUG])
ANOTHER_GROUP_URL = reverse("posts:group_list", args=[ANOTHER_SLUG])
PROFILE_URL = reverse("posts:profile", args=[USERNAME])
PROFILE_FOLLOW_URL = reverse("posts:profile_follow", args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse("posts:profile_unfollow", args=[USERNAME])
FOLLOW_INDEX_URL = reverse("posts:follow_index")


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another_user = User.objects.create_user(username=ANOTHER_USERNAME)
        cls.another_authorized_client = Client()
        cls.another_authorized_client.force_login(cls.another_user)
        cls.date = datetime.now()
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug=GROUP_SLUG,
            description="Тестовое описание",
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
            pub_date=cls.date,
            image=SimpleUploadedFile(
                name="small.gif", content=small_gif, content_type="image/gif"
            ),
        )
        cls.POST_URL = reverse("posts:post_detail", args=[cls.post.id])
        cls.EDIT_POST_URL = reverse("posts:post_edit", args=[cls.post.id])
        cls.another_group = Group.objects.create(
            title="Тестовая группа другая",
            slug=ANOTHER_SLUG,
        )

    def context_post(self, post):
        """Метод проверки контекста поста."""
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.pk, self.post.pk)
        self.assertEqual(post.image, self.post.image)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.context_post(response.context["page_obj"][0])

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_URL)
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.context_post(response.context["page_obj"][0])
        group = response.context.get("group")
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.pk, self.group.pk)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.context_post(response.context["page_obj"][0])
        post_author = response.context.get("author")
        self.assertEqual(post_author, self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        self.context_post(self.authorized_client.get(self.POST_URL).context.get("post"))

    def test_post_not_in_another_group(self):
        """Пост при создании пост не попал в другую группу."""
        self.assertNotIn(
            self.post,
            self.authorized_client.get(ANOTHER_GROUP_URL).context["page_obj"],
        )

    def test_auth_able_follow(self):
        """Авторизованный пользователь может подписываться
        на пользователей."""
        cnt_follower = Follow.objects.count()
        response = self.another_authorized_client.get(PROFILE_FOLLOW_URL)
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Follow.objects.count() - cnt_follower, 1)
        self.assertTrue(Follow.objects.filter(
            author__username=USERNAME).exists())

    def test_auth_able_unfollow(self):
        """Авторизованный пользователь может удалять авторов из подписок."""
        cnt_follower = Follow.objects.count()
        self.another_authorized_client.get(PROFILE_FOLLOW_URL)
        self.assertEqual(Follow.objects.count() - cnt_follower, 1)
        response = self.another_authorized_client.get(PROFILE_UNFOLLOW_URL)
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Follow.objects.count(), cnt_follower)
        self.assertFalse(Follow.objects.filter(
            author__username=USERNAME).exists())

    def test_do_not_show_posts_to_not_followers(self):
        """Новая запись автора не появляется в ленте тех, кто не подписан."""
        response = self.another_authorized_client.get(FOLLOW_INDEX_URL)
        self.assertEqual(len(response.context["page_obj"]),
                         Follow.objects.count())

    def test_show_posts_to_followers(self):
        """Новая запись автора появляется в ленте тех, кто на него подписан."""
        self.another_authorized_client.get(PROFILE_FOLLOW_URL)
        response = self.another_authorized_client.get(FOLLOW_INDEX_URL)
        self.assertEqual(len(response.context["page_obj"]),
                         Follow.objects.count())

    def test_paginator_on_pages(self):
        """Пагинация на страницах."""
        self.POSTS_ON_SECOND_PAGE = Post.objects.count()
        Post.objects.bulk_create(
            Post(
                author=self.user,
                group=self.group,
                text=f"Пост #{i}",
            )
            for i in range(POSTS_ON_PAGE_NUMB)
        )
        url_pages = {
            INDEX_URL: POSTS_ON_PAGE_NUMB,
            f"{INDEX_URL}?page=2": self.POSTS_ON_SECOND_PAGE,
            GROUP_URL: POSTS_ON_PAGE_NUMB,
            f"{GROUP_URL}?page=2": self.POSTS_ON_SECOND_PAGE,
            PROFILE_URL: POSTS_ON_PAGE_NUMB,
            f"{PROFILE_URL}?page=2": self.POSTS_ON_SECOND_PAGE,
        }
        for url_page, args in url_pages.items():
            with self.subTest(url_page=url_page):
                self.assertEqual(
                    len(self.guest_client.get(
                        url_page).context.get("page_obj")),
                    args,
                )