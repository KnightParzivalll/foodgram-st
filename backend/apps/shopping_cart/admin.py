from django.contrib.admin import ModelAdmin, register
from .models import ShoppingCart


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user",)
    list_per_page = 25
    ordering = ("-pk",)
