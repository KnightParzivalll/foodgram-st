from rest_framework import serializers

from apps.favorites.models import Favorite
from apps.shopping_cart.models import ShoppingCart
from .models import Recipe, IngredientInRecipe
from apps.users.serializers import UserShortSerializer
from apps.ingredients.serializers import (
    IngredientInRecipeSerializer,
    CreateShortIngredientsSerializer,
)
from config.fields import Base64ImageField


class RecipeSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(source="ingredient_amounts", many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")

        return (
            request is not None
            and request.user.is_authenticated
            and request.user.favorites.filter(recipe_id=obj.id).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")

        return (
            request is not None
            and request.user.is_authenticated
            and request.user.shoppingcarts.filter(recipe_id=obj.id).exists()
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateShortIngredientsSerializer(many=True)
    image = Base64ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return serializer.data

    def validate(self, data):
        ingredients = data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                "Список ингредиентов не может быть пустым!"
            )

        ingredients_ids = [el["id"] for el in ingredients]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError("Ингредиенты должны быть уникальными!")

        for ingredient in ingredients:
            amount = ingredient.get("amount")
            if amount is None or amount < 1:
                raise serializers.ValidationError(
                    "Количество ингредиента должно быть не меньше 1."
                )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")

        user = self.context.get("request").user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.pop("ingredients"), instance)
        return super().update(instance, validated_data)

    def create_ingredients(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                ingredient=element["id"],
                recipe=recipe,
                amount=element["amount"],
            )
            for element in ingredients
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class UserRecipeRelationSerializer(serializers.Serializer):
    class Meta:
        fields = ("user", "recipe")

    def to_representation(self, instance):
        serializer = ShortRecipeSerializer(instance.recipe, context=self.context)
        return serializer.data

    def validate(self, data, related_name):
        user = data.get("user")
        recipe = data.get("recipe")

        if getattr(user, related_name).filter(recipe__id=recipe.id).exists():
            raise serializers.ValidationError(
                f"{related_name} пользователя {user.username} "
                f"уже содержит рецепт {recipe.name}."
            )

        return data


class FavoriteSerializer(UserRecipeRelationSerializer, serializers.ModelSerializer):
    class Meta(UserRecipeRelationSerializer.Meta):
        model = Favorite

    def validate(self, data):
        return super().validate(data, "favorites")


class ShoppingCartSerializer(UserRecipeRelationSerializer, serializers.ModelSerializer):
    class Meta(UserRecipeRelationSerializer.Meta):
        model = ShoppingCart

    def validate(self, data):
        return super().validate(data, "shoppingcarts")
