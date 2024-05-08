from django.db import models
from django.core.validators import (MaxValueValidator,
                                    MinValueValidator)
from django.db.models import UniqueConstraint
from colorfield.fields import ColorField

from users.models import User
from foodgram.constants import (MAX_NAME,
                                COOKING_TIME,
                                MAX_AMOUNT,
                                MAX_COLOR_FIELD,
                                MAX_MEASUREMENTS_UNIT,
                                MIN_AMOUNT)


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=MAX_NAME,
        db_index=True,
        unique=True
    )
    color = ColorField(
        verbose_name='HEX-код',
        format='hex',
        max_length=MAX_COLOR_FIELD,
        unique=True,
    )
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Ингредиент', max_length=MAX_NAME)
    measurement_unit = models.CharField('Величина измерения',
                                        max_length=MAX_MEASUREMENTS_UNIT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            ),
        )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField('Рецепт', max_length=MAX_NAME)
    author = models.ForeignKey(User,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='recipes',)
    tags = models.ManyToManyField(Tag, verbose_name='Список тегов',
                                  related_name='recipes')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientAmount',
        through_fields=('recipe', 'ingredient'),)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(MinValueValidator(MIN_AMOUNT,
                                      message='Время должно быть больше нуля'),
                    MaxValueValidator(COOKING_TIME,
                                      message=(f'Время приготовления не более '
                                               f'{COOKING_TIME} минут')))
    )
    image = models.ImageField('Картинка',
                              upload_to='recipes/',
                              help_text='Выберите картинку')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True)

    class Meta:
        ordering = ('-pub_date', 'name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return f'{self.name} - {self.author.username}'


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            limit_value=MIN_AMOUNT,
            message=f'Количество должно быть равно или больше {MIN_AMOUNT}'),
            MaxValueValidator(
            limit_value=MAX_AMOUNT,
            message=f'Количество должно быть не больше {MAX_AMOUNT}'),
        ))
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredientamount_set')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('ingredient', 'recipe'),
                                    name='unique_ingredient_in_recipe'),
        )
        ordering = ('recipe', 'ingredient',)
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количества ингредиента в рецепте'

    def __str__(self) -> str:
        return (
            f'{self.recipe.name} - {self.ingredient.name} '
            f'{self.amount}{self.ingredient.measurement_unit} '
            f'{self.ingredient.name}'
        )


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            ),
        )

    def __str__(self):
        return f'{self.user} :: {self.recipe}'


class Favorites(FavoriteShoppingCart):

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(FavoriteShoppingCart):

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
