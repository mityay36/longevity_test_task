from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('user', 'USER'),
    ('moderator', 'MODERATOR'),
    ('admin', 'ADMIN'),
)

CODE_LENGTH = 6
PASSWORD_LENGTH = 18


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password='',
        bio='',
        role='user',
        first_name='',
        last_name=''
    ):

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(
            email=self.normalize_email(email),
            confirmation_code=self.make_random_password(length=CODE_LENGTH),
            password=make_password(password),
            role=role,
            bio=bio,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        return user

    def create_superuser(
        self,
        email,
        password=None,
        bio='',
        role='admin',
        first_name='',
        last_name=''
    ):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(
            email=email,
            password=make_password(password),
            role=role,
            bio=bio,
            first_name=first_name,
            last_name=last_name
        )
        user.is_superuser = True
        user.is_staff = True
        user.email_user(
            subject='confirmation_code',
            message=f'Your confirmation code is: {user.confirmation_code}',
            fail_silently=False
        )
        user.save()

        return user


class User(AbstractUser):
    email = models.EmailField(
        unique=True, max_length=128
    )
    username = None
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=16,
        choices=ROLE_CHOICES,
        default='user'
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=CODE_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        ordering = ['-date_joined']

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def __str__(self):
        return self.email
