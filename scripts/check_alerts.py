"""
Run on a GitHub Actions schedule. Reads alerts.json, checks each active
alert against BookMyShow, emails when tickets go live, and rewrites
alerts.json with sent alerts removed (mirrors the old Celery task's
alert.delete() behaviour).
"""
import json
import os
import smtplib
import sys
from email.mime.text import MIMEText
from pathlib import Path

from scraper_core import check_bms_availability

ALERTS_FILE = Path(__file__).resolve().parent.parent / "alerts.json"


def load_alerts():
    if not ALERTS_FILE.exists():
        return []
    with open(ALERTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_alerts(alerts):
    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
        f.write("\n")


def send_email(to_email: str, subject: str, body: str) -> None:
    host = os.environ["EMAIL_HOST"]
    port = int(os.environ.get("EMAIL_PORT", "587"))
    user = os.environ["EMAIL_HOST_USER"]
    password = os.environ["EMAIL_HOST_PASSWORD"]
    from_email = os.environ.get("DEFAULT_FROM_EMAIL", user)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(from_email, [to_email], msg.as_string())


def main():
    alerts = load_alerts()
    active = [a for a in alerts if a.get("is_active", True) and not a.get("alert_sent", False)]

    if not active:
        print("No active alerts to monitor.")
        return

    remaining = list(alerts)
    changed = False

    for alert in active:
        movie_name = alert["movie_name"]
        bms_url = alert["bms_url"]
        theatre_filter = alert.get("theatre_filter") or None
        target_date = alert.get("target_date") or None
        user_email = alert["user_email"]

        print(f"--> Checking BMS for: {movie_name} ({bms_url}) | Date: {target_date} | Filter: {theatre_filter}")
        try:
            is_available, venues, direct_url = check_bms_availability(
                url=bms_url,
                theatre_filter=theatre_filter,
                target_date=target_date,
            )
        except Exception as e:
            print(f"[!] Error checking {movie_name}: {e}")
            continue

        if is_available:
            venue_details = "\n- ".join(venues) if venues else "General Booking Open"
            target_display = f" on {target_date}" if target_date else ""
            subject = f"TICKETS LIVE: {movie_name}"
            message = (
                f"Booking is now LIVE for '{movie_name}'{target_display}!\n\n"
                f"Status / Venues:\n- {venue_details}\n\n"
                f"Book immediately here:\n{direct_url}\n\n"
                f"-- BookMyShow Alert Bot"
            )
            try:
                send_email(user_email, subject, message)
                print(f"[+] Alert email dispatched to {user_email}")
                remaining = [a for a in remaining if a is not alert]
                changed = True
            except Exception as e:
                print(f"[!] Failed to send email for {movie_name}: {e}")

    if changed:
        save_alerts(remaining)
        print(f"alerts.json updated: {len(alerts) - len(remaining)} alert(s) removed after sending.")
    else:
        print("No alerts fired this run.")


if __name__ == "__main__":
    sys.exit(main())