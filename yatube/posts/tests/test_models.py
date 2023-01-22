from django.test import TestCase

from yatube.settings import NUMB_SYMBOLS_SHORT_TEXT

from ..models import Comment, Follow, follow_str, Group, Post, User


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
            (self.post.text[:NUMB_SYMBOLS_SHORT_TEXT], str(self.post)),
            (self.group.title, str(self.group)),
            (follow_str.format(user=self.follow.user.username,
                               author=self.follow.author.username),
             str(self.follow)),
            (self.comment.text[:NUMB_SYMBOLS_SHORT_TEXT], str(self.comment))
        ]
        for model, str_method in models_str:
            with self.subTest(model=model, str_method=str_method):
                self.assertEqual(model, str_method)
