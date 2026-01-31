from rest_framework.routers import DefaultRouter
from .views import SaldosViewSet

router = DefaultRouter()
router.register(r'saldos', SaldosViewSet, basename='saldos')

urlpatterns = router.urls
