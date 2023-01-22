from django.contrib.auth import get_user_model
from django.db import models

from yatube.settings import NUMB_SYMBOLS_SHORT_TEXT

User = get_user_model()

FOLLOW_STR = "{user} подписан на {author}"
COMMENT_STR = "Автор {author} написал комментарий: {text}"
POST_STR = "Автор {author} написал в группе {group} пост: {text}"


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название группы",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text="Укажите ключ адреса страницы группы",
    )
    description = models.TextField(
        verbose_name="Описание группы",
        help_text="Опишите группу",
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Наберите текст",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выберите группу",
    )
    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True,
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ("-pub_date",)

    def __str__(self):
        return POST_STR.format(
            author=self.author,
            group=self.group,
            text=self.text[:NUMB_SYMBOLS_SHORT_TEXT]
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Наберите текст",
    )
    created = models.DateTimeField(
        verbose_name="Дата публикации комментария",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ('-created',)

    def __str__(self):
        return COMMENT_STR.format(
            author=self.author,
            text=self.text[:NUMB_SYMBOLS_SHORT_TEXT]
        )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор постов",
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_follow'
            )
        ]

    def __str__(self):
        return FOLLOW_STR.format(
            user=self.user.username,
            author=self.author.username
        )
