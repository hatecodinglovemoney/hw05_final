from django.test import TestCase

from yatube.settings import NUMB_SYMBOLS_SHORT_TEXT

from ..models import Comment, COMMENT_STR, Follow, \
    FOLLOW_STR, Group, Post, POST_STR, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.user_follower = User.objects.create_user(username='user_follower')
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text="Тестовый комментарий",
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.user_follower,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_str = [
            (POST_STR.format(
                author=self.post.author,
                group=self.post.group,
                text=self.post.text[:NUMB_SYMBOLS_SHORT_TEXT]),
             self.post),
            (self.group.title, self.group),
            (FOLLOW_STR.format(
                user=self.follow.user.username,
                author=self.follow.author.username),
             self.follow),
            (COMMENT_STR.format(
                author=self.comment.author,
                text=self.comment.text[:NUMB_SYMBOLS_SHORT_TEXT]),
             self.comment)
        ]
        for str_method, model in models_str:
            with self.subTest():
                self.assertEqual(str_method, str(model))
