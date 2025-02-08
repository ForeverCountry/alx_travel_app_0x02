from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ListingViewSet,
    BookingViewSet,
    ReviewViewSet,
    InitiatePaymentAPIView,
    VerifyPaymentAPIView,
)


router = DefaultRouter()
router.register(r"listings", ListingViewSet)
router.register(r"bookings", BookingViewSet)
router.register(r"reviews", ReviewViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "payments/initiate/",
        InitiatePaymentAPIView.as_view(),
        name="initiate-payment",
    ),
    path(
        "payments/verify/",
        VerifyPaymentAPIView.as_view(),
        name="verify-payment",
    ),
]
