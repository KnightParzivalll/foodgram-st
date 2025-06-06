from django.contrib import admin
from django.contrib.admin import TabularInline, register, ModelAdmin
from .models import IngredientInRecipe, Recipe
from config.constants import INGREDIENT_INLINE_MIN_AMOUNT
from django.db.models import Count


class IngredientInRecipeInline(TabularInline):
    model = IngredientInRecipe
    min_num = INGREDIENT_INLINE_MIN_AMOUNT
    extra = 0
    classes = ["collapse"]
    autocomplete_fields = ["ingredient"]


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ("pk", "name", "author", "favorites_count", "created")
    list_filter = ("author", "name")
    search_fields = ("name", "author__username")
    inlines = [IngredientInRecipeInline]
    list_per_page = 20
    ordering = ("-created",)
    readonly_fields = ("favorites_count",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(fav_count=Count("favorites"))

    @admin.display(description="В избранном (раз)")
    def favorites_count(self, obj):
        return obj.fav_count


@register(IngredientInRecipe)
class IngredientInRecipeAdmin(ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")
    list_filter = ("ingredient",)
    search_fields = ("ingredient__name",)
