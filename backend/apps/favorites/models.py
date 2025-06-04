from apps.relations.models import UserRecipeRelation


class Favorite(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        default_related_name = "favorites"
