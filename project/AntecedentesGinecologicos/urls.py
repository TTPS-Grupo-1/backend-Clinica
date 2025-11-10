from rest_framework.routers import DefaultRouter
from .views import AntecedentesGinecologicosViewSet

router = DefaultRouter()
router.register(r'antecedentes-ginecologicos', AntecedentesGinecologicosViewSet, basename='ante-gine')

urlpatterns = router.urls
