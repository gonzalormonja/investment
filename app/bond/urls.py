from django.urls import path, include

from rest_framework.routers import DefaultRouter

from bond import views

router = DefaultRouter()
router.register("", views.BondViewSet, basename="bonds")

app_name = "bond"

urlpatterns = [path("", include(router.urls))]
