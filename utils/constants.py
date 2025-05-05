from typing import Dict

# HTTP headers to use for requests
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
}

# Region mappings
region_map: Dict[str, str] = {
    "na": "north-america",
    "eu": "europe",
    "ap": "asia-pacific",
    "la": "latin-america",
    "la-s": "la-s",
    "la-n": "la-n",
    "oce": "oceania",
    "kr": "korea",
    "mn": "mena",
    "gc": "game-changers",
    "br": "Brazil",
    "cn": "china",
}

# URL constants
BASE_URL = "https://www.vlr.gg"
NEWS_URL = f"{BASE_URL}/news"
MATCHES_URL = f"{BASE_URL}/matches"
RESULTS_URL = f"{BASE_URL}/matches/results"
RANKINGS_URL = f"{BASE_URL}/rankings"