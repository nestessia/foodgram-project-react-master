from rest_framework.serializers import ValidationError
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status

from recipes.models import (Ingredient,
                            Recipe,
                            Tag,
                            IngredientAmount,
                            Favorites,
                            ShoppingCart)
from users.models import User, Follow
from foodgram.constants import MAX_AMOUNT, MIN_AMOUNT, COOKING_TIME


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return request and (
            request.user.is_authenticated
            and request.user.follower.filter(recipe_author=obj).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(max_value=MAX_AMOUNT,
                                      min_value=MIN_AMOUNT)

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True,
                                              required=True)
    image = Base64ImageField(required=True,
                             allow_null=False,
                             allow_empty_file=False,
                             error_messages={'detail':
                                             'image не может быть пустым'})
    cooking_time = serializers.IntegerField(min_value=MIN_AMOUNT,
                                            max_value=COOKING_TIME)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        tags = data.get('tags', [])

        if not tags:
            raise ValidationError(
                {'tags': 'Список тегов не может быть пустым.'}
            )
        if len(tags) != len(set(tags)):
            raise ValidationError(
                {'tags': 'Теги должны быть уникальными.'}
            )
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Список ингредиентов не может быть пустым.'}
            )
        ingredients_ids = [ingredient.get('id') for ingredient in ingredients]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise ValidationError(
                {'ingredients': 'Нельзя использовать два ингрдиента.'}
            )
        return data

    @staticmethod
    def create_ingredients(recipe, ingredients_data):
        recipe_ingredients = [
            IngredientAmount(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        IngredientAmount.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='ingredientamount_set')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'image', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and request.user.shopping_cart.filter(recipe=obj).exists()
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowShowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except (ValueError, TypeError):
                recipes_limit = None
            recipes = recipes[:recipes_limit]
        return RecipeShortSerializer(recipes,
                                     many=True,
                                     context=self.context).data


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('follower', 'recipe_author')

    def validate(self, data):
        recipe_author = data.get('recipe_author')
        follower = data.get('follower')
        if recipe_author == follower:
            raise ValidationError(
                detail='Подписка уже есть.',
                code=status.HTTP_400_BAD_REQUEST)

        if recipe_author == follower:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST)
        return data

    def to_representation(self, instance):
        return FollowShowSerializer(
            instance.recipe_author,
            context=self.context).data


class FavoriteAndShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = None
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data.get('user')
        recipe_id = data.get('recipe').id
        if self.Meta.model.objects.filter(user=user,
                                          recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                {'detail': f'Рецепт уже добавлен в '
                 f'{self.Meta.model._meta.verbose_name}!'}
            )
        return data

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(
            instance.recipe, context=self.context)
        return serializer.data


class ShoppingCartSerializer(FavoriteAndShoppingCartSerializer):
    class Meta(FavoriteAndShoppingCartSerializer.Meta):
        model = ShoppingCart


class FavoriteSerializer(FavoriteAndShoppingCartSerializer):
    class Meta(FavoriteAndShoppingCartSerializer.Meta):
        model = Favorites
        fields = ('recipe', 'user')
