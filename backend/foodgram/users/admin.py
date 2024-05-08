from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'get_recipes_count', 'get_followers_count')
    search_fields = ('username', 'email')
    list_filter = ('first_name', 'last_name')
    ordering = ('username', )
    empty_value_display = '-пусто-'

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    get_recipes_count.short_description = 'Количество рецептов'

    def get_followers_count(self, obj):
        return obj.recipeauthor.count()
    get_followers_count.short_description = 'Количество подписок'


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    list_display = ('recipe_author', 'follower')
    search_fields = ('follower', 'recipe_author',)
    list_filter = ('follower', 'recipe_author',)
    ordering = ('recipe_author', )
    empty_value_display = '-пусто-'
