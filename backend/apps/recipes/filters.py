import django_filters
from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.CharFilter(method="is_recipe_in_favorites_filter")
    is_in_shopping_cart = django_filters.CharFilter(
        method="is_recipe_in_shoppingcart_filter"
    )

    def is_recipe_in_favorites_filter(self, queryset, name, value):
        user = self.request.user

        if value.lower() in ("1", "true", "yes") and user.is_authenticated:
            return queryset.filter(favorites__user=user)

        return queryset

    def is_recipe_in_shoppingcart_filter(self, queryset, name, value):
        user = self.request.user

        if value.lower() in ("1", "true", "yes") and user.is_authenticated:
            return queryset.filter(shoppingcarts__user=user)

        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "is_favorited", "is_in_shopping_cart")
