#!/usr/bin/env python3
"""Download the English Ontario ambulance response-time CSV from the official catalogue."""
from pathlib import Path
from urllib.request import Request, urlopen

URL = "https://data.ontario.ca/dataset/0c4c8e2d-5e72-4a72-9101-1570e5a28677/resource/feaebc4c-a197-44ba-84e7-bd19c358e87c/download/average_response_times_and_call_volumes.csv"
DEST = Path(__file__).resolve().parents[1] / "data" / "raw" / "average_response_times_and_call_volumes.csv"

def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    request = Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        content = response.read()
    if len(content) < 100 or b"<html" in content[:500].lower():
        raise RuntimeError("The downloaded response does not appear to be a valid CSV.")
    DEST.write_bytes(content)
    print(f"Saved official CSV to: {DEST}")
    print(f"File size: {len(content):,} bytes")

if __name__ == "__main__":
    main()
