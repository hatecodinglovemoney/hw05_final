import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

USERNAME = "NoName"
ANOTHER_USERNAME = "NoName2"
GROUP_SLUG = "test-slug"
ANOTHER_SLUG = "test-slug2"
CREATE_POST = reverse("posts:post_create")
LOGIN_URL = reverse("users:login")
PROFILE_URL = reverse("posts:profile", args=[USERNAME])
IMAGE_FOLDER = Post.image.field.upload_to
SMALL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x02\x00"
    b"\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
    b"\x00\x00\x00\x2C\x00\x00\x00\x00"
    b"\x02\x00\x01\x00\x00\x02\x02\x0C"
    b"\x0A\x00\x3B"
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.EDIT_POST_URL_REDIRECT = f"{LOGIN_URL}?next={cls.EDIT_POST_URL}"
        cls.COMMENT_URL = reverse("posts:add_comment", args=[cls.post.pk])
        cls.another_group = Group.objects.create(
            title="Тестовая группа другая",
            slug=ANOTHER_SLUG,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Проверим создание поста через форму
        авторизированным клиентом"""
        posts = set(Post.objects.all())
        uploaded = SimpleUploadedFile(
            name='another_small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        form_data = {
            "text": "Тестовый пост2",
            "group": self.group.id,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            CREATE_POST,
            data=form_data,
            follow=True,
        )
        posts = set(Post.objects.all()) - posts
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.group.id, form_data["group"])
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(
            post.image,
            IMAGE_FOLDER + str(form_data["image"])
        )

    def test_guest_client_not_create_post(self):
        """Проверим создание поста через форму
        неавторизированным клиентом"""
        posts = set(Post.objects.all())
        uploaded = SimpleUploadedFile(
            name='another_small_2.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        form_data = {
            "text": "Тестовый пост2",
            "group": self.group.id,
            "image": uploaded,
        }
        response = self.guest_client.post(
            CREATE_POST,
            data=form_data,
        )
        self.assertEqual(posts, set(Post.objects.all()))
        self.assertEqual(response.status_code, 302)

    def test_post_edit_post(self):
        """Проверяем редактирование поста
        авторизированным клиентом"""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='another_small_3.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        form_data = {
            "text": "Тестовый пост редактирование",
            "group": self.another_group.id,
            "image": uploaded
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
        self.assertEqual(
            post.image,
            IMAGE_FOLDER + str(form_data["image"]),
        )

    def test_guest_or_another_not_edit_post(self):
        """Проверяем редактирование поста неавторизированным
        клиентом или не автором поста"""
        post_count = Post.objects.count()
        clients_not_edit = [
            (self.another_authorized_client, self.POST_URL),
            (self.guest_client, self.EDIT_POST_URL_REDIRECT),
        ]
        uploaded = SimpleUploadedFile(
            name='another_small_4.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        form_data = {
            "text": "Тестовый пост редактирование",
            "group": self.another_group.id,
            "image": uploaded
        }
        for client, redirect in clients_not_edit:
            with self.subTest(client=client):
                response = client.post(
                    self.EDIT_POST_URL, data=form_data,
                )
                post = Post.objects.get(id=self.post.pk)
                self.assertEqual(Post.objects.count(), post_count)
                self.assertRedirects(response, redirect)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.image, self.post.image)
                self.assertEqual(post.group, self.post.group)


    def test_create_post_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        url_list = [
            self.EDIT_POST_URL,
            CREATE_POST,
        ]
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
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
        comments = set(Comment.objects.all()) - comments
        self.assertEqual(len(comments), 1)
        comment = comments.pop()
        self.assertEqual(comment.text, form_data["text"])
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)

    def test_guest_not_create_comment(self):
        """Гости не могут комментировать посты."""
        comments = set(Comment.objects.all())
        form_data = {
            "text": "Комментарий",
        }
        self.guest_client.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True,
        )
        self.assertEqual(set(Comment.objects.all()), comments)
