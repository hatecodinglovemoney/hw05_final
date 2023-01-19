# Generated by Django 2.2.16 on 2023-01-19 03:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0007_comment"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="comment",
            options={
                "verbose_name": "Комментарий",
                "verbose_name_plural": "Комментарии",
            },
        ),
        migrations.AlterField(
            model_name="comment",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Дата публикации комментария"
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="posts.Post",
                verbose_name="Пост",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="text",
            field=models.TextField(
                help_text="Наберите текст", verbose_name="Текст комментария"
            ),
        ),
    ]