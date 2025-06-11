from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet

router = DefaultRouter()
router.register(r"", IngredientViewSet, basename="ingredients")  # без 'ingredients'

urlpatterns = router.urls
