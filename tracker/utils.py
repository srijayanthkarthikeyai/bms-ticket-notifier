import re
from datetime import date

def normalize_bms_url(raw_url: str, target_date_str: str = None) -> str:
    """
    Converts any BMS movie overview link into a direct '/buytickets/' URL.
    
    Input:
      https://in.bookmyshow.com/movies/bhimavaram/toxic-a-fairy-tale-for-grownups/ET00378770
    Output:
      https://in.bookmyshow.com/movies/bhimavaram/toxic-a-fairy-tale-for-grownups/buytickets/ET00378770/YYYYMMDD
    """
    url = raw_url.strip().split("?")[0].rstrip("/")
    
    # If the user already provided a buytickets URL, return clean
    if "/buytickets/" in url:
        return url

    # Default to today's date in YYYYMMDD if not provided
    if not target_date_str:
        target_date_str = date.today().strftime("%Y%m%d")

    # Match pattern: /movies/{city}/{slug}/{event_code}
    pattern = r"https?://(?:in\.)?bookmyshow\.com/movies/([^/]+)/([^/]+)/([A-Z0-9]+)"
    match = re.search(pattern, url, re.IGNORECASE)

    if match:
        city = match.group(1)
        movie_slug = match.group(2)
        event_code = match.group(3)
        return f"https://in.bookmyshow.com/movies/{city}/{movie_slug}/buytickets/{event_code}/{target_date_str}"

    return raw_url