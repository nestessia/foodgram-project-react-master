from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        fields = ('tags',
                  'author')
        model = Recipe

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset
