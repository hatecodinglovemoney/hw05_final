from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

USERNAME = "NoName"
ANOTHER_USERNAME = "NoName2"
GROUP_SLUG = "test-slug"
LOGIN_URL = reverse("users:login")
INDEX_URL = reverse("posts:index")
CREATE_URL = reverse("posts:post_create")
FOLLOW_INDEX_URL = reverse("posts:follow_index")
FOLLOW_INDEX_URL_REDIRECT = f"{LOGIN_URL}?next={FOLLOW_INDEX_URL}"
CREATE_URL_REDIRECT = f"{LOGIN_URL}?next={CREATE_URL}"
UNEXISTING_URL = "/unexisting_page/"
GROUP_URL = reverse("posts:group_list", args=[GROUP_SLUG])
PROFILE_URL = reverse("posts:profile", args=[USERNAME])
PROFILE_FOLLOW_URL = reverse("posts:profile_follow", args=[USERNAME])
PROFILE_FOLLOW_REDIRECT = f"{LOGIN_URL}?next={PROFILE_FOLLOW_URL}"
PROFILE_UNFOLLOW_URL = reverse("posts:profile_unfollow", args=[USERNAME])
PROFILE_UNFOLLOW_REDIRECT = f"{LOGIN_URL}?next={PROFILE_UNFOLLOW_URL}"


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            description="Тестовый текст",
            slug=GROUP_SLUG,
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )
        cls.POST_URL = reverse("posts:post_detail", args=[cls.post.id])
        cls.EDIT_POST_URL = reverse("posts:post_edit", args=[cls.post.id])
        cls.EDIT_POST_URL_REDIRECT = f"{LOGIN_URL}?next={cls.EDIT_POST_URL}"
        cls.ADD_COMMENT_URL = reverse("posts:add_comment", args=[cls.post.id])
        cls.ADD_COMMENT_URL_REDIRECT = f"{LOGIN_URL}?next={cls.ADD_COMMENT_URL}"
        cls.another = Client()
        cls.another_user = User.objects.create_user(username=ANOTHER_USERNAME)
        cls.another.force_login(cls.another_user)

    def test_list_url_status(self):
        """Страницы приложения posts
        соотвествуют ожидаемому status_code."""
        cases = [
            (INDEX_URL, self.guest, 200),
            (UNEXISTING_URL, self.guest, 404),
            (CREATE_URL, self.author, 200),
            (CREATE_URL, self.guest, 302),
            (GROUP_URL, self.guest, 200),
            (PROFILE_URL, self.guest, 200),
            (self.POST_URL, self.guest, 200),
            (self.EDIT_POST_URL, self.author, 200),
            (self.EDIT_POST_URL, self.guest, 302),
            (self.EDIT_POST_URL, self.another, 302),
            (FOLLOW_INDEX_URL, self.guest, 302),
            (FOLLOW_INDEX_URL, self.author, 200),
            (self.ADD_COMMENT_URL, self.author, 302),
            (self.ADD_COMMENT_URL, self.guest, 302),
            (self.ADD_COMMENT_URL, self.another, 302),
            (PROFILE_FOLLOW_URL, self.author, 302),
            (PROFILE_FOLLOW_URL, self.guest, 302),
            (PROFILE_FOLLOW_URL, self.another, 302),
            (PROFILE_UNFOLLOW_URL, self.another, 302),
            (PROFILE_UNFOLLOW_URL, self.author, 302),
            (PROFILE_UNFOLLOW_URL, self.guest, 302),
        ]
        for url, client, status in cases:
            with self.subTest(url=url, client=client, status=status):
                self.assertEqual(client.get(url).status_code, status)

    def test_url_redirect(self):
        """Проверка редиректов"""
        url_redirect = [
            (self.EDIT_POST_URL, self.another, self.POST_URL),
            (self.EDIT_POST_URL, self.guest, self.EDIT_POST_URL_REDIRECT),
            (CREATE_URL, self.guest, CREATE_URL_REDIRECT),
            (FOLLOW_INDEX_URL, self.guest, FOLLOW_INDEX_URL_REDIRECT),
            (self.ADD_COMMENT_URL, self.author, self.POST_URL),
            (self.ADD_COMMENT_URL, self.guest, self.ADD_COMMENT_URL_REDIRECT),
            (self.ADD_COMMENT_URL, self.another, self.POST_URL),
            (PROFILE_FOLLOW_URL, self.author, PROFILE_URL),
            (PROFILE_FOLLOW_URL, self.guest, PROFILE_FOLLOW_REDIRECT),
            (PROFILE_FOLLOW_URL, self.another, PROFILE_URL),
            (PROFILE_UNFOLLOW_URL, self.author, PROFILE_URL),
            (PROFILE_UNFOLLOW_URL, self.guest, PROFILE_UNFOLLOW_REDIRECT),
            (PROFILE_UNFOLLOW_URL, self.another, PROFILE_URL),
        ]
        for url, client, redirect in url_redirect:
            with self.subTest(url=url, client=client, redirect=redirect):
                self.assertRedirects(client.get(url, follow=True), redirect)

    def test_urls_use_correct_template(self):
        """URL-адреса приложения posts используют соответствующий шаблон."""
        templates_url_dict = {
            INDEX_URL: "posts/index.html",
            GROUP_URL: "posts/group_list.html",
            PROFILE_URL: "posts/profile.html",
            self.POST_URL: "posts/post_detail.html",
            CREATE_URL: "posts/create_post.html",
            self.EDIT_POST_URL: "posts/create_post.html",
            UNEXISTING_URL: "core/404.html",
        }
        for url, template in templates_url_dict.items():
            with self.subTest(url=url, template=template):
                self.assertTemplateUsed(self.author.get(url), template)
