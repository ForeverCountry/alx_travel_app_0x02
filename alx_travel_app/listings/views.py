from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Listing, Booking, Review
from django.contrib.auth.models import User
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

@api_view(['GET'])
def user_listings(request, user_id=None):
    user = (user_id or request.user.id)
    listings = Listing.objects.filter(host_id=user)
    serializer = ListingSerializer(listings, many=True)
    return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request):
        property_id = request.data.get('property_id')
        user_id = request.data.get('user_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        total_price = request.data.get('total_price')

        property = get_object_or_404(Listing, listing_id=property_id)
        user = get_object_or_404(User, id=user_id)

        booking = Booking.objects.create(
            property_id=property,
            user_id=user,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price
        )

        booking.save()

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])    
def user_bookings(request, user_id=None):
    user = (user_id or request.user.id)
    bookings = Booking.objects.filter(user_id=user)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def listing_bookings(request, listing_id=None):
    listing = get_object_or_404(Listing, listing_id=listing_id)
    bookings = Booking.objects.filter(property_id=listing)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)