# Listings App

This Django app manages property listings, bookings, and reviews for the ALX Travel App platform.

## Models

### Listing Model
Represents a property listing in the system.

**Fields:**
- `property_id` (UUID): Primary key for the listing
- `host` (ForeignKey): Reference to the User model (property owner)
- `name` (CharField): Name of the property
- `description` (TextField): Detailed description of the property
- `location` (CharField): Property location
- `price_per_night` (DecimalField): Cost per night
- `created_at` (DateTimeField): Timestamp of creation
- `updated_at` (DateTimeField): Timestamp of last update

### Booking Model
Manages property bookings and reservations.

**Fields:**
- `booking_id` (UUID): Primary key for the booking
- `property` (ForeignKey): Reference to the Listing model
- `user` (ForeignKey): Reference to the User model (guest)
- `start_date` (DateField): Check-in date
- `end_date` (DateField): Check-out date
- `total_price` (DecimalField): Total cost of the booking
- `status` (CharField): Current status (pending/confirmed/canceled)
- `created_at` (DateTimeField): Timestamp of booking creation

### Review Model
Handles property reviews and ratings.

**Fields:**
- `review_id` (UUID): Primary key for the review
- `property` (ForeignKey): Reference to the Listing model
- `user` (ForeignKey): Reference to the User model (reviewer)
- `rating` (IntegerField): Rating score (1-5)
- `comment` (TextField): Review text
- `created_at` (DateTimeField): Timestamp of review creation

**Constraints:**
- One review per property-user combination (unique_together)
- Rating must be between 1 and 5

## Serializers

### ListingSerializer
Handles the serialization of Listing model data.

**Features:**
- Includes all listing fields
- Read-only fields: property_id, created_at, updated_at

### BookingSerializer
Manages the serialization of Booking model data.

**Features:**
- Includes all booking fields
- Read-only fields: booking_id, created_at
- Validates that end_date is after start_date

### ReviewSerializer
Controls the serialization of Review model data.

**Features:**
- Includes all review fields
- Read-only fields: review_id, created_at

## Database Seeding

The app includes a management command to populate the database with sample data:

```bash
python manage.py seed
```

This command creates:
- Sample users with different roles (guest, host, admin)
- Property listings for host users
- Bookings and reviews for guest users 