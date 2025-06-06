from django.contrib import admin
from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.html import format_html
from django.contrib.auth.models import Group
from .models import Subscription, User

admin.site.unregister(Group)


@register(User)
class UserAdminConfig(UserAdmin):
    list_display = (
        "pk",
        "username",
        "email",
        "first_name",
        "last_name",
        "avatar_preview",
        "recipes_count",
        "subscribers_count",
    )
    list_filter = ("username", "email")
    search_fields = ("username", "email")

    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("avatar",)}),)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            recipes_count=Count("recipes", distinct=True),
            subscribers_count=Count("followers", distinct=True),
        )
        return qs

    @admin.display(description="Количество рецептов", ordering="recipes_count")
    def recipes_count(self, obj):
        return obj.recipes_count

    @admin.display(description="Количество подписчиков", ordering="subscribers_count")
    def subscribers_count(self, obj):
        return obj.subscribers_count

    @admin.display(description="Аватар")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return "-"


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ("pk", "subscriber", "author")
    search_fields = ("subscriber__username", "author__username")
    list_filter = ("subscriber", "author")
    list_per_page = 25
    ordering = ("-pk",)
    autocomplete_fields = ["subscriber", "author"]
