"""
BookMyShow ticket-availability scraper.
Ported as-is from the original Django project's tracker/scraper.py
(no Django dependency here, just requests + re + json).
"""
import json
import re
from datetime import date, datetime
from typing import Optional, Union
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1",
}


def to_buytickets_url(url: str, target_date: Optional[Union[str, date, datetime]] = None):
    """Converts any BMS link to the canonical /buytickets/{slug}-{city}/movie-{city}-{event_code}-MT/{date_str} URL."""
    clean_url = url.strip().split("?")[0].rstrip("/")
    if target_date:
        if isinstance(target_date, (date, datetime)):
            date_str = target_date.strftime("%Y%m%d")
        else:
            date_str = str(target_date).replace("-", "").replace("/", "").strip()
    else:
        date_str = date.today().strftime("%Y%m%d")

    # Standard synopsis URL (/movies/city/slug/event_code)
    synopsis_pattern = r"bookmyshow\.com/movies/([^/]+)/([^/]+)(?:/buytickets)?/([A-Z0-9]+)"
    match = re.search(synopsis_pattern, clean_url, re.IGNORECASE)
    if match:
        city, slug, event_code = match.group(1), match.group(2), match.group(3)
        return f"https://in.bookmyshow.com/buytickets/{slug}-{city}/movie-{city}-{event_code}-MT/{date_str}", date_str

    # Direct /buytickets/ URL
    if "/buytickets/" in clean_url:
        parts = clean_url.split("/")
        if parts[-1].isdigit() and len(parts[-1]) == 8:
            parts[-1] = date_str
            return "/".join(parts), date_str
        return f"{clean_url}/{date_str}", date_str

    return clean_url, date_str


def check_bms_availability(
    url: str,
    theatre_filter: Optional[str] = None,
    target_date: Optional[Union[str, date, datetime]] = None,
):
    target_url, date_str = to_buytickets_url(url, target_date=target_date)
    print(f"[*] Checking URL: {target_url} for target date: {date_str}")

    try:
        response = requests.get(target_url, headers=HEADERS, timeout=12, allow_redirects=True)
        if response.status_code != 200:
            print(f"[!] HTTP status code: {response.status_code}")
            return False, [], target_url

        final_url = response.url.split("?")[0].rstrip("/")
        if date_str not in final_url and not final_url.endswith(date_str):
            print(f"[-] BMS redirected away from {date_str}. Booking not open for this date.")
            return False, [], target_url
        html = response.text

        # STRATEGY 1: Parse Embedded Next.js / Initial State
        json_matches = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for script_body in json_matches:
            if '{"props":' in script_body or 'window.__INITIAL_STATE__' in script_body:
                json_text = script_body
                if "window.__INITIAL_STATE__" in script_body:
                    assign_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});?', script_body, re.DOTALL)
                    if assign_match:
                        json_text = assign_match.group(1)
                try:
                    data = json.loads(json_text)
                    valid_venues = []

                    def scan_venues(node):
                        if isinstance(node, dict):
                            venue_name = (
                                node.get("name")
                                or node.get("VenueName")
                                or node.get("venueName")
                                or node.get("venue_name")
                                or node.get("CinemaName")
                            )
                            shows = (
                                node.get("shows")
                                or node.get("arrShows")
                                or node.get("ShowTimes")
                                or node.get("showTimes")
                                or node.get("sessions")
                                or node.get("ShowDetails")
                            )
                            if venue_name and isinstance(shows, list) and len(shows) > 0:
                                if not theatre_filter or theatre_filter.lower() in str(venue_name).lower():
                                    valid_venues.append(str(venue_name))
                            for v in node.values():
                                scan_venues(v)
                        elif isinstance(node, list):
                            for item in node:
                                scan_venues(item)

                    scan_venues(data)
                    if valid_venues:
                        unique_venues = list(set(valid_venues))
                        print(f"[+] Confirmed {len(unique_venues)} live venue(s): {unique_venues}")
                        return True, unique_venues, target_url
                except (json.JSONDecodeError, Exception):
                    continue

        # STRATEGY 2: Resilient HTML Markup & Showtime Parsing
        has_time_pill = bool(re.search(r'(?:showtime-pill|btn-showtime|showtime-cell|__showtime)', html, re.IGNORECASE))
        has_time_string = bool(re.search(r'\b\d{1,2}:\d{2}\s*(?:AM|PM)\b', html, re.IGNORECASE))
        has_pricing_or_session = bool(re.search(r'data-session-id|data-show-time|data-cut-off|price-list|avail-status', html, re.IGNORECASE))

        if (has_time_pill and has_time_string) or (has_time_string and has_pricing_or_session):
            print("[+] Active showtimes detected in page markup!")
            return True, ["Venues detected (Booking is open)"], target_url

        print(f"[-] No valid shows listed for {date_str}.")
        return False, [], target_url

    except requests.RequestException as e:
        print(f"[!] Scraper network error: {e}")
        return False, [], target_url