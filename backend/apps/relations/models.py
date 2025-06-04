from django.db import models
from django.contrib.auth import get_user_model
from apps.recipes.models import Recipe

User = get_user_model()


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="%(class)ss",
        # user.favorites — избранные рецепты пользователя (если класс Favorite)
        # user.shoppingcarts — списки покупок пользователя (если класс ShoppingCart)
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="%(class)ss",
        # recipe.favorites — пользователи, добавившие рецепт в избранное
        # recipe.shoppingcarts — пользователи, добавившие рецепт в список покупок
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe_%(class)s"
            )
        ]
        ordering = ("-user",)

    def __str__(self):
        return f"{self.user} — {self.recipe}"
