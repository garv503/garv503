"""Fetch a GitHub contribution calendar without an API token.

GitHub serves the calendar as public HTML at /users/<name>/contributions -
the same fragment the profile page loads. We parse it and write
data/contributions.json with the raw days plus derived stats.
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "garv503")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (profile-art generator)",
    "Accept": "text/html",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_html() -> str:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Counts live in <tool-tip for="..."> siblings, keyed by the cell id.
    counts = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if not target:
            continue
        text = tip.get_text(strip=True)
        match = re.match(r"^(\d[\d,]*)\s+contribution", text)
        counts[target] = int(match.group(1).replace(",", "")) if match else 0

    days = []
    for cell in soup.select("td[data-date]"):
        days.append(
            {
                "date": cell["data-date"],
                "level": int(cell.get("data-level", 0)),
                "count": counts.get(cell.get("id"), 0),
            }
        )

    if not days:
        raise SystemExit(
            "No day cells found. GitHub's markup for the contribution "
            "calendar has probably changed; the selectors need updating."
        )

    days.sort(key=lambda d: d["date"])

    total = sum(d["count"] for d in days)
    heading = soup.find("h2")
    if heading:
        match = re.search(r"([\d,]+)\s+contribution", " ".join(heading.get_text().split()))
        if match:
            total = int(match.group(1).replace(",", ""))

    return {
        "username": USERNAME,
        "generated": date.today().isoformat(),
        "total": total,
        "days": days,
        **derive_stats(days),
    }


def derive_stats(days: list) -> dict:
    today = date.today().isoformat()
    past = [d for d in days if d["date"] <= today]

    longest = run = 0
    for day in past:
        run = run + 1 if day["count"] > 0 else 0
        longest = max(longest, run)

    current = 0
    for day in reversed(past):
        if day["count"] > 0:
            current += 1
        elif current or day["date"] != today:
            # An empty today doesn't break a streak that ran until yesterday.
            break

    best = max(past, key=lambda d: d["count"], default={"date": "", "count": 0})

    monthly = defaultdict(int)
    for day in past:
        monthly[day["date"][:7]] += day["count"]

    return {
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "active_days": sum(1 for d in past if d["count"] > 0),
        "monthly": dict(sorted(monthly.items())),
    }


def main() -> int:
    data = parse(fetch_html())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(
        f"{OUT.name}: {len(data['days'])} days, {data['total']} contributions, "
        f"current streak {data['current_streak']}, longest {data['longest_streak']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
