#!/usr/bin/env python3
"""
tmdb-app – tiny CLI for now-playing, popular, top-rated, upcoming movies.
Usage:
    python tmdb_app.py --type playing
    python tmdb_app.py --type popular
    python tmdb_app.py --type top
    python tmdb_app.py --type upcoming
"""
import argparse
import os
import sys
import datetime
import ssl
import certifi
import requests
import subprocess, json
from dotenv import load_dotenv

# fix Windows TLS / cert issues
ssl.create_default_context(cafile=certifi.where())

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
if not API_KEY:
    sys.exit("ERROR: TMDB_API_KEY not found in .env file")

BASE_URL = "https://api.themoviedb.org/3"
ENDPOINTS = {
    "playing": "/movie/now_playing",
    "popular": "/movie/popular",
    "top": "/movie/top_rated",
    "upcoming": "/movie/upcoming",
}



def fetch_movies(category: str):
    import subprocess, json, os
    url = BASE_URL + ENDPOINTS[category]
    params = f"api_key={API_KEY}&language=en-US&page=1"
    cmd = ["curl", "-s", "-L", f"{url}?{params}"]
    try:
        raw = subprocess.check_output(cmd, timeout=15)
        data = json.loads(raw.decode('utf-8'))
        if "results" not in data:
            raise RuntimeError("Bad JSON from TMDB.")
        return data["results"]
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Network/curl error: {exc}") from None

def format_movie(m):
    """Pretty single-line summary."""
    title = m.get("title", "N/A")
    date = m.get("release_date", "")
    if date:
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
        except ValueError:
            date = ""
    rating = m.get("vote_average", 0)
    return f"{title}  |  {date}  |  ★ {rating}/10"


def main():
    parser = argparse.ArgumentParser(description="CLI for TMDB movie lists.")
    parser.add_argument(
        "--type",
        choices=list(ENDPOINTS.keys()),
        required=True,
        help="Category: playing, popular, top, upcoming",
    )
    args = parser.parse_args()

    try:
        movies = fetch_movies(args.type)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    if not movies:
        print("No movies found.")
        return

    print(f"\n{args.type.upper()} MOVIES\n" + "-" * 50)
    for m in movies[:15]:  # limit output
        print(format_movie(m))


if __name__ == "__main__":
    main()