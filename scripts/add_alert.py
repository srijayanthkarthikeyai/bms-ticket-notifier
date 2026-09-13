"""
Small CLI helper to append a new alert to alerts.json.
Run locally, then git add/commit/push alerts.json.

Usage:
  python scripts/add_alert.py \
    --email you@example.com \
    --movie "Avengers: Secret Wars" \
    --url "https://in.bookmyshow.com/movies/city/slug/ET00000000" \
    --theatre "PVR" \
    --date 2026-09-20
"""
import argparse
import json
from pathlib import Path

ALERTS_FILE = Path(__file__).resolve().parent.parent / "alerts.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--movie", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--theatre", default=None)
    parser.add_argument("--date", default=None, help="YYYY-MM-DD")
    args = parser.parse_args()

    alerts = []
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, "r", encoding="utf-8") as f:
            alerts = json.load(f)

    alerts.append({
        "user_email": args.email,
        "movie_name": args.movie,
        "bms_url": args.url,
        "theatre_filter": args.theatre,
        "target_date": args.date,
        "is_active": True,
        "alert_sent": False,
    })

    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
        f.write("\n")

    print(f"Added alert for '{args.movie}' -> {args.email}. Now git add/commit/push alerts.json.")


if __name__ == "__main__":
    main()