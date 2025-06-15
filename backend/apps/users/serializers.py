from rest_framework import serializers

from config.fields import Base64ImageField
from .models import Subscription, User
from djoser.serializers import UserCreateSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(use_url=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj) -> bool:
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(subscriber=user, author=obj).exists()

    def get_recipes(self, obj):
        from apps.recipes.serializers import RecipeSerializer

        request = self.context.get("request")
        recipes = obj.recipes.all()
        return RecipeSerializer(recipes, many=True, context={"request": request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CreateUserProfileSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class UserProfileAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(use_url=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, value):
        if not value:
            raise serializers.ValidationError("Аватар не может быть пустым")
        return value


class SubscriptionSerializer(UserProfileSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source="recipes.count", read_only=True)

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields

    def get_recipes(self, obj):
        from apps.recipes.serializers import ShortRecipeSerializer

        request = self.context.get("request")
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[: int(recipes_limit)]
        return ShortRecipeSerializer(
            recipes, many=True, context={"request": request}
        ).data


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("author", "subscriber")
        extra_kwargs = {
            "author": {"write_only": True},
            "subscriber": {"write_only": True},
        }

    def validate(self, data):
        if data["subscriber"] == data["author"]:
            raise serializers.ValidationError("Вы не можете подписаться на себя!")
        return data

    def to_representation(self, instance):
        return SubscriptionSerializer(instance.author, context=self.context).data


class UserShortSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(use_url=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj) -> bool:
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(subscriber=user, author=obj).exists()
