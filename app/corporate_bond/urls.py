from django.urls import path, include

from rest_framework.routers import DefaultRouter

from corporate_bond.views import CashFlowViewSet

router = DefaultRouter()

router.register(
    r"corporate-bond/(?P<corporate_bond_name>\w+)/cash-flow",
    CashFlowViewSet,
    basename="corporate-bond-cash-flow",
)

app_name = "corporate_bond"

urlpatterns = [path("", include(router.urls))]
