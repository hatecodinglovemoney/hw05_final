from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post, User

USERNAME = "NoName"
GROUP_SLUG = "test-slug"
ANOTHER_SLUG = "test-slug2"
CREATE_POST = reverse("posts:post_create")
PROFILE_URL = reverse("posts:profile", args=[USERNAME])


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug=GROUP_SLUG,
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )
        cls.POST_URL = reverse("posts:post_detail", args=[cls.post.pk])
        cls.EDIT_POST_URL = reverse("posts:post_edit", args=[cls.post.pk])
        cls.COMMENT_URL = reverse("posts:add_comment", args=[cls.post.pk])
        cls.another_group = Group.objects.create(
            title="Тестовая группа другая",
            slug=ANOTHER_SLUG,
        )

    def test_create_post(self):
        """Проверим создание поста через форму"""
        posts = set(Post.objects.all())
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        form_data = {
            "text": "Тестовый пост2",
            "group": self.group.id,
            "image": SimpleUploadedFile(
                name="small.gif", content=small_gif, content_type="image/gif"
            ),
        }
        response = self.authorized_client.post(
            CREATE_POST,
            data=form_data,
            follow=True,
        )
        new_posts = set(Post.objects.all()) - posts
        self.assertEqual(len(new_posts), 1)
        post = new_posts.pop()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.group.id, form_data["group"])
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)
        self.assertRedirects(response, PROFILE_URL)

    def test_post_edit_post(self):
        """Проверяем редактирование поста"""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый пост редактирование",
            "group": self.another_group.id,
        }
        response = self.authorized_client.post(
            self.EDIT_POST_URL, data=form_data, follow=True
        )
        post = Post.objects.get(id=self.post.pk)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, form_data["group"])
        self.assertEqual(post.text, form_data["text"])

    def test_create_post_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        url_list = [
            self.EDIT_POST_URL,
            CREATE_POST,
        ]
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for url in url_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            "form").fields.get(value)
                        self.assertIsInstance(form_field, expected)

    def test_auth_create_comment(self):
        """Авторизованный пользователь может комментировать посты."""
        comments = set(Comment.objects.all())
        form_data = {
            "text": "Комментарий",
        }
        self.authorized_client.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True,
        )
        new_comments = set(Comment.objects.all()) - comments
        self.assertEqual(len(new_comments), 1)
        comment = new_comments.pop()
        self.assertEqual(comment.text, form_data["text"])
        self.assertEqual(comment.post, self.post)

    def test_user_create_comment(self):
        """Гости не могут комментировать посты."""
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Комментарий",
        }
        self.guest_client.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count)
