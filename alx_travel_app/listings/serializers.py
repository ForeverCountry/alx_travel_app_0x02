from rest_framework import serializers
from .models import Listing, Booking, Review, Payment


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "review_id",
            "property",
            "user",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["review_id", "created_at"]


class ListingSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = [
            "property_id",
            "host",
            "name",
            "description",
            "location",
            "price_per_night",
            "created_at",
            "updated_at",
            "reviews",
        ]
        read_only_fields = ["property_id", "created_at", "updated_at"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "property",
            "user",
            "start_date",
            "end_date",
            "total_price",
            "status",
            "created_at",
        ]
        read_only_fields = ["booking_id", "created_at"]

    def validate(self, data):
        """Validate booking dates"""
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        return data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
