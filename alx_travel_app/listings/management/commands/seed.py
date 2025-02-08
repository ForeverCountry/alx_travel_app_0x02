"""Populates the database with seed data for listings."""
import random
from django.core.management.base import BaseCommand
from alx_travel_app.listings.models import Listing
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Populates the database with seed data for listings.'

    def handle(self, *args, **options):
        Listing.objects.all().delete()
        user = User.objects.first()

        if user is None:
            self.stdout.write(self.style.WARNING('No user found. Please create a user before seeding the database.'))
            return


        for i in range(10):
            Listing.objects.create(
                host_id=user,
                name=f'Listing {i}',
                description=f'This is a description for Listing {i}.',
                location=f'Location {i}',
                pricepernight=random.randint(50, 500)
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with listings.'))
