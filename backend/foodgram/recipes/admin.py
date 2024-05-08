from django.contrib import admin

from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
    IngredientAmount)


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color',)
    list_filter = ('name', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'cooking_time',
                    'get_favorites', 'get_ingredients',)
    search_fields = ('name', 'author', 'tags',)
    list_filter = ('author', 'name', 'tags',)
    inlines = (IngredientInline,)

    def get_favorites(self, obj):
        return obj.favorites.count()
    get_favorites.short_description = 'Избранное'

    def get_ingredients(self, obj):
        return ', '.join([
            ingredients.name for ingredients
            in obj.ingredients.all()])
    get_ingredients.short_description = 'Ингредиенты'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name', )
    list_filter = ('name', )


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user',)
    list_filter = ('recipe', 'user',)
    search_fields = ('user', )
