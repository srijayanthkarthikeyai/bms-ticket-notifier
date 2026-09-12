from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import TicketAlert
from .scraper import check_bms_availability


@shared_task
def check_all_movie_alerts():
    active_alerts = list(
        TicketAlert.objects.filter(is_active=True, alert_sent=False)
    )
    if not active_alerts:
        print("No active alerts to monitor.")
        return "No active alerts."

    processed = 0
    sent = 0

    for alert in active_alerts:
        print(f"--> Checking BMS for: {alert.movie_name} ({alert.bms_url}) | Date: {alert.target_date} | Filter: {alert.theatre_filter}")
        try:
            is_available, venues, direct_url = check_bms_availability(
                url=alert.bms_url,
                theatre_filter=alert.theatre_filter,
                target_date=alert.target_date,
            )
            alert.last_checked_at = timezone.now()
            if is_available:
                print(f"✅ Tickets found for {alert.movie_name}! Sending email to {alert.user_email}...")
                venue_details = "\n- ".join(venues) if venues else "General Booking Open"
                target_display = f" on {alert.target_date}" if alert.target_date else ""
                
                subject = f"🚨 TICKETS LIVE: {alert.movie_name}"
                message = (
                    f"Booking is now LIVE for '{alert.movie_name}'{target_display}!\n\n"
                    f"Status / Venues:\n- {venue_details}\n\n"
                    f"Book immediately here:\n{direct_url}\n\n"
                    f"— BookMyShow Alert Bot"
                )
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,
                    recipient_list=[alert.user_email],
                    fail_silently=False,
                )
                alert.alert_sent = True
                alert.delete()
                sent += 1
                print(f"🚀 Alert email dispatched to {alert.user_email}")
            processed += 1
        except Exception as e:
            print(f"❌ Error processing alert {alert.pk} ({alert.movie_name}): {e}")
            continue
    return f"Processed {processed}/{len(active_alerts)} alert(s), {sent} email(s) sent."