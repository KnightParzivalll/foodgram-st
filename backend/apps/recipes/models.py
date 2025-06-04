from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from apps.ingredients.models import Ingredient
from config.constants import (
    INGREDIENT_MIN_AMOUNT_IN_RECIPE,
    RECIPE_IMAGE_UPLOAD_TO,
    RECIPE_MIN_COOKING_TIME,
    RECIPE_NAME_MAX_LENGTH,
)

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        related_name="recipes",  # user.recipes — все его рецепты
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH, verbose_name="Название рецепта"
    )
    image = models.ImageField(
        verbose_name="Фотография рецепта",
        upload_to=RECIPE_IMAGE_UPLOAD_TO,
        blank=True,
    )
    text = models.TextField(verbose_name="Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        verbose_name="Ингредиенты",
        related_name="recipes",  # ingredient.recipes — рецепты с этим ингредиентом
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=[
            MinValueValidator(RECIPE_MIN_COOKING_TIME),
        ],
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата публикации рецепта",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created",)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="ingredient_amounts",  # recipe.ingredient_amounts — связи ингредиентов с количеством
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        related_name="recipe_amounts",  # ingredient.recipe_amounts — связи с рецептами и их количество
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(INGREDIENT_MIN_AMOUNT_IN_RECIPE),
        ],
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_ingredient_recipe_relation",
            )
        ]
        ordering = ("recipe__name", "ingredient__name")

    def __str__(self):
        return f"{self.ingredient.name} — {self.amount} ({self.ingredient.measurement_unit}) в рецепте {self.recipe.name}"
