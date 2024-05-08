from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from django.db.models import Sum
from django.http import FileResponse

from .filters import RecipeFilter, IngredientFilter
from .paginations import LimitPageNumberPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            Favorites,
                            IngredientAmount,
                            ShoppingCart)
from .serializers import (UserSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          RecipeCreateSerializer,
                          FollowSerializer,
                          FavoriteSerializer,
                          ShoppingCartSerializer,
                          FollowShowSerializer)
from users.models import User


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(detail=True,
            methods=['post'],
            permission_classes=(IsAuthenticated,),
            url_path='subscribe',)
    def subscribe(self, request, id):
        data = {'follower': request.user.id, 'recipe_author': id}
        context = {'request': request}
        serializer = FollowSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False,
            permission_classes=(IsAuthenticated,),
            url_path='subscriptions',
            methods=['get'],)
    def subscriptions(self, request):
        queryset = User.objects.filter(
            recipeauthor__follower=self.request.user)
        paginator = LimitPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = FollowShowSerializer(
            page,
            many=True,
            context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @subscribe.mapping.delete
    def delete_subscribtions(self, request, id):
        subscription = request.user.follower.filter(
            recipe_author_id=id
        )
        if not subscription.exists():
            return Response({'detail':
                             'Такой подписки нет'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    pagination_class = None
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags',
        'ingredients').all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = (IsAdminOrAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    @staticmethod
    def create_object(serializer_class, pk, request):
        create_data = {
            'user': request.user.id,
            'recipe': pk
        }
        context = {'request': request}
        serializer = serializer_class(data=create_data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_object(model, pk, request):
        obj = model.objects.filter(recipe_id=pk, user=request.user)
        if not obj.exists():
            return Response({'detail': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='favorite',)
    def favorite(self, request, pk):
        return self.create_object(FavoriteSerializer, pk, request)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_object(Favorites, pk, request)

    @action(detail=True, methods=['post'],
            url_path='shopping_cart', permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.create_object(ShoppingCartSerializer, pk, request)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_object(ShoppingCart, pk, request)

    @staticmethod
    def send_message(ingredients):
        shopping_list = ('Необходимые ингредиенты для покупки:\n')
        for ingredient in ingredients:
            shopping_list += '\n'.join([
                f'{ingredient["ingredient__name"]} '
                f'{ingredient["amount"]}'
                f'{ingredient["ingredient__measurement_unit"]}\n'])
        response = FileResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename=shopping_cart.txt')
        return response

    @action(methods=['GET', ],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')
        return self.send_message(ingredients=ingredients)
