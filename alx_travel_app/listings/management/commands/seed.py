import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from alx_travel_app.listings.models import Listing, Booking, Review
from faker import Faker

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        self.create_users()

        self.create_listings()

        self.create_bookings_and_reviews()

        self.stdout.write(self.style.SUCCESS("Successfully seeded database"))

    def create_users(self):
        """Create sample users"""
        for _ in range(5):
            username = fake.user_name()
            User.objects.create_user(
                username=username,
                email=fake.email(),
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_staff=False,
            )

        # Create staff users
        for _ in range(2):
            username = fake.user_name()
            User.objects.create_user(
                username=username,
                email=fake.email(),
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_staff=True,
            )

        self.stdout.write("Created sample users")

    def create_listings(self):
        """Create sample listings"""
        users = User.objects.all()

        for user in users:
            for _ in range(2):
                Listing.objects.create(
                    host=user,
                    name=fake.company(),
                    description=fake.text(),
                    location=fake.address(),
                    price_per_night=random.randint(50, 500),
                )

        self.stdout.write("Created sample listings")

    def create_bookings_and_reviews(self):
        """Create sample bookings and reviews"""
        users = User.objects.all()
        listings = Listing.objects.all()
        status_choices = ["pending", "confirmed", "canceled"]

        for user in users:
            for _ in range(2):
                listing = random.choice(listings)
                if listing.host != user:  # Don't book own listing
                    start_date = datetime.now().date() + timedelta(
                        days=random.randint(1, 30)
                    )
                    end_date = start_date + timedelta(
                        days=random.randint(1, 7)
                    )

                    # Create booking
                    booking = Booking.objects.create(
                        property=listing,
                        user=user,
                        start_date=start_date,
                        end_date=end_date,
                        total_price=listing.price_per_night
                        * (end_date - start_date).days,
                        status=random.choice(status_choices),
                    )

                    # Create review (only for confirmed bookings)
                    if booking.status == "confirmed":
                        Review.objects.create(
                            property=listing,
                            user=user,
                            rating=random.randint(1, 5),
                            comment=fake.text(),
                        )

        self.stdout.write("Created sample bookings and reviews")
