from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def prohibited_usernames_validator(value):
    """Validate prohibited usernames."""
    if value in settings.PROHIBITED_USER_NAMES:
        raise ValidationError(
            _("%(value)s username is prohibited!"),
            params={"value": value},
        )


class User(AbstractUser):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLE_CHOICES = [
        (USER, "User"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Administrator"),
    ]

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            (
                "Required. 150 characters or fewer."
                " Letters, digits and @/./+/-/_ only."
            )
        ),
        validators=[username_validator, prohibited_usernames_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        "Роль пользователя",
        choices=ROLE_CHOICES,
        default=USER,
        max_length=20,
        blank=True,
    )
    bio = models.TextField(
        "Биография",
        blank=True,
    )
    confirmation_code = models.CharField(max_length=24, blank=True)

    def save(self, *args, **kwargs):
        """Update is_staff for admin users and role for superuser."""
        if self.role == User.ADMIN:
            self.is_staff = True
        if self.is_superuser:
            self.role = User.ADMIN
        super(User, self).save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.is_staff or self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return (
            self.role == self.MODERATOR
            or self.role == self.ADMIN
            or self.is_staff
            or self.is_superuser
        )
