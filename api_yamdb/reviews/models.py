from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def validate_year(value):
    current_year = date.today().year
    if not (value <= current_year):
        raise ValidationError(
            _(
                f"You cannot add works that have not yet been released."
                f" The year of issue cannot be greater than {current_year}"
            ),
            params={"value": value},
        )
    return value


class Category(models.Model):
    """Category model."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название категории",
        help_text="Добавьте название категории",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Уникальный адрес категории",
        help_text="Добавьте адрес категории",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Genre model."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название жанра",
        help_text="Добавьте название жанра",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Уникальный адрес жанра",
        help_text="Добавьте адрес жанра",
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    """Title model."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название произведения",
        help_text="Добавьте название произведения",
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Год выпуска произведения",
        help_text="Добавьте год выпуска произведения",
        validators=[validate_year],
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Описание произведения",
        help_text="Добавьте описание произведения",
    )
    genre = models.ManyToManyField(
        Genre,
        related_name="titles",
        verbose_name="Жанр",
        help_text="Выберите жанр",
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="titles",
        verbose_name="Категория",
        help_text="Выберите категорию",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_name_year_title",
                fields=["name", "year"],
            )
        ]
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class Review(models.Model):
    """Review model."""

    RATING_CHOICES = [
        (None, "---"),
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
        (9, "9"),
        (10, "10"),
    ]

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
        help_text="Выберите произведение",
    )
    text = models.TextField(
        blank=False,
        verbose_name="Текст отзыва",
        help_text="Напишите свой отзыв",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
    )
    score = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default="---",
        verbose_name="Оценка",
        help_text="Дайте оценку произведению от 1 до 10",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_title_author_review",
                fields=["title", "author"],
            )
        ]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return (f"{self.author} добавил отзыв на {self.title},"
                f" с оценкой {self.score}")


class Comment(models.Model):
    """Comment model."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзывы",
        help_text="Выберите отзыв",
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name="Комментарий",
        help_text="Оставьте свой комментарий к отзыву",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )

    class Meta:
        verbose_name = "Комментарий к отзыву"
        verbose_name_plural = "Комментарии к отзывам"

    def __str__(self):
        return (f"{self.author} добавил новый комментарий: {self.text}"
                f" к отзыву: {self.review}")
