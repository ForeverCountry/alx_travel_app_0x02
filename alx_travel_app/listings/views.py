import os
import requests
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import Listing, Booking, Review, Payment
from .serializers import (
    ListingSerializer,
    BookingSerializer,
    ReviewSerializer,
    PaymentSerializer,
)
from .tasks import send_booking_confirmation_email


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing property listings.
    """

    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    @swagger_auto_schema(
        operation_description="List all property listings",
        responses={200: ListingSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new property listing",
        request_body=ListingSerializer,
        responses={201: ListingSerializer()},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing bookings.
    """

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter bookings based on user role"""
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        # Send booking confirmation email asynchronously
        send_booking_confirmation_email.delay(
            booking_id=booking.id,
            user_email=booking.user.email,
            listing_title=booking.listing.title,
        )

    @swagger_auto_schema(
        operation_description="List all bookings for the authenticated user",
        responses={200: BookingSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new booking",
        request_body=BookingSerializer,
        responses={201: BookingSerializer()},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing reviews.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InitiatePaymentAPIView(APIView):
    """
    API endpoint to initiate payment via Chapa.
    Expects a POST with the booking_id.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=PaymentSerializer,
        operation_description="Initiate payment for a booking",
        responses={200: PaymentSerializer()},
    )
    def post(self, request, *args, **kwargs):
        booking_id = request.data.get("booking_id")
        if not booking_id:
            return Response(
                {"error": "Booking ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the booking belongs to the user
        booking = get_object_or_404(
            Booking, booking_id=booking_id, user=request.user
        )

        # Create a Payment record (or get the existing one)
        payment, created = Payment.objects.get_or_create(
            booking=booking, defaults={"amount": booking.total_price}
        )

        # Prepare data for Chapa payment initiation
        chapa_secret_key = os.environ.get("CHAPA_SECRET_KEY")
        if not chapa_secret_key:
            return Response(
                {"error": "Chapa secret key not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        headers = {
            "Authorization": f"Bearer {chapa_secret_key}",
            "Content-Type": "application/json",
        }
        # Build the callback URL so that Chapa redirects after payment
        callback_url = request.build_absolute_uri(
            "/api/payments/verify/"
        )  # adjust path if needed

        # Data expected by Chapa – adjust fields as per Chapa API docs.
        data = {
            "amount": str(booking.total_price),
            "currency": "ETB",  # Change this to your required currency
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": getattr(request.user, "last_name", ""),
            "tx_ref": str(
                payment.payment_id
            ),  # Use payment_id as transaction reference
            "callback_url": callback_url,
        }

        # Call Chapa API to initiate the payment
        response = requests.post(
            "https://api.chapa.co/v1/transaction/initialize",
            json=data,
            headers=headers,
        )
        if response.status_code != 200:
            return Response(
                {"error": "Failed to initiate payment with Chapa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        res_data = response.json()
        # Extract transaction details (adjust keys based on Chapa’s response)
        transaction_id = res_data.get("data", {}).get("transaction_id")
        payment_link = res_data.get("data", {}).get("checkout_url")
        if not transaction_id or not payment_link:
            return Response(
                {"error": "Invalid response from Chapa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save the transaction_id in our Payment record
        payment.transaction_id = transaction_id
        payment.save()

        # Return the payment link and payment details to the client
        return Response(
            {
                "payment_id": str(payment.payment_id),
                "payment_link": payment_link,
                "status": payment.status,
            },
            status=status.HTTP_200_OK,
        )


class VerifyPaymentAPIView(APIView):
    """
    API endpoint to verify a payment with Chapa.
    This could be the endpoint used as the callback URL.
    Expects query parameters 'transaction_id' and 'tx_ref' (payment_id).
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        transaction_id = request.query_params.get("transaction_id")
        tx_ref = request.query_params.get("tx_ref")

        if not transaction_id or not tx_ref:
            return Response(
                {"error": "Missing transaction_id or tx_ref parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(payment_id=tx_ref)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        chapa_secret_key = os.environ.get("CHAPA_SECRET_KEY")
        headers = {
            "Authorization": f"Bearer {chapa_secret_key}",
            "Content-Type": "application/json",
        }
        verify_url = (
            f"https://api.chapa.co/v1/transaction/verify/{transaction_id}"
        )
        response = requests.get(verify_url, headers=headers)
        if response.status_code != 200:
            payment.status = Payment.PaymentStatus.FAILED
            payment.save()
            return Response(
                {"error": "Payment verification failed with Chapa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        res_data = response.json()
        chapa_status = res_data.get("data", {}).get("status")
        if chapa_status == "successful":
            payment.status = Payment.PaymentStatus.COMPLETED
            payment.save()
            booking = payment.booking
            booking.status = Booking.BookingStatus.CONFIRMED
            booking.save()
            send_booking_confirmation_email.delay(
                booking_id=str(booking.booking_id),
                user_email=booking.user.email,
                listing_title=booking.property.name,
            )
            return Response(
                {"message": "Payment verified and booking confirmed."},
                status=status.HTTP_200_OK,
            )
        else:
            payment.status = Payment.PaymentStatus.FAILED
            payment.save()
            return Response(
                {"message": "Payment verification unsuccessful."},
                status=status.HTTP_400_BAD_REQUEST,
            )
