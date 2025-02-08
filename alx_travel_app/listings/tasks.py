from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_booking_confirmation_email(booking_id, user_email, listing_title):
    """
    Send a booking confirmation email to the user.
    """
    subject = f"Booking Confirmation - {listing_title}"
    message = f"""
    Thank you for your booking!
    
    Your booking (ID: {booking_id}) for {listing_title} has been confirmed.
    
    Thank you for choosing our service!
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )

    return f"Confirmation email sent for booking {booking_id}"
