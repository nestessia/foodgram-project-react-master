from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import F, Q, UniqueConstraint

from foodgram.constants import (MAX_USER_PARAMETRS,
                                MAX_EMAIL_FIELD)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', )
    username = models.CharField(
        'Никнейм',
        max_length=MAX_USER_PARAMETRS,
        unique=True,
        error_messages={
            'unique':
            'Пользователь с таким именем уже существует.'},
        validators=(UnicodeUsernameValidator(),))
    email = models.EmailField('Электронная почта',
                              max_length=MAX_EMAIL_FIELD,
                              unique=True)
    first_name = models.CharField('Имя',
                                  max_length=MAX_USER_PARAMETRS)
    last_name = models.CharField('Фамилия',
                                 max_length=MAX_USER_PARAMETRS)

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    recipe_author = models.ForeignKey(User,
                                      related_name='recipeauthor',
                                      verbose_name='Автор',
                                      on_delete=models.CASCADE)
    follower = models.ForeignKey(User,
                                 related_name='follower',
                                 verbose_name='Подписчик',
                                 on_delete=models.CASCADE)

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=('follower', 'recipe_author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                name='unique_subscriptions',
                check=~Q(follower=F('recipe_author')),
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'{self.follower.username} '
                f'теперь подписан на {self.recipe_author.username}')
