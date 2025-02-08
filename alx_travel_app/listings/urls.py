from rest_framework import routers
from django.urls import path, include
from .views import ListingViewSet, BookingViewSet, user_listings, user_bookings, listing_bookings

router = routers.DefaultRouter()
router.register('listings', ListingViewSet)
router.register('bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('listings/<listing_id>/bookings/', listing_bookings),
    path('users/<user_id>/bookings/', user_bookings),
    path('users/<user_id>/listings/', user_listings),
]