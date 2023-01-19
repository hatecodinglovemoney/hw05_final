# Generated by Django 2.2.16 on 2023-01-16 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0003_auto_20230116_1720"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="description",
            field=models.TextField(
                help_text="Опишите группу", verbose_name="Описание группы"
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="slug",
            field=models.SlugField(
                help_text="Укажите ключ адреса страницы группы",
                unique=True,
                verbose_name="Слаг",
            ),
        ),
    ]