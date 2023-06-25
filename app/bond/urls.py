from django.urls import path, include

from rest_framework.routers import DefaultRouter

from bond import views

router = DefaultRouter()
# router.register("", views.BondViewSet, basename="bonds")
router.register("ratio", views.BondRatioViewSet, basename="bond-ratio")

app_name = "bond"

urlpatterns = [path("", include(router.urls))]
