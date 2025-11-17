from flask import Flask, render_template
import requests
from datetime import datetime, timedelta, timezone

app = Flask(__name__)


# ---------------------------------------------------------
# Fetch Contracts Finder (OPEN, last 7 days)
# ---------------------------------------------------------
def get_contracts_finder():
    url = "https://www.contractsfinder.service.gov.uk/api/rest/2/search_notices/json"

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    payload = {
        "searchCriteria": {
            "statuses": ["Open"],
            "types": ["Contract"],
            "publishedFrom": week_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "publishedTo": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "suitableForSme": True,
        },
        "size": 1000,
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("noticeList", [])
    except Exception as e:
        print("Contracts Finder error:", e)
        return []


# ---------------------------------------------------------
# Fetch Find-a-Tender (OPEN tender stage, last 7 days)
# ---------------------------------------------------------
def get_find_tender():
    url = "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    params = {
        "stages": "tender",
        "updatedFrom": week_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updatedTo": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": 100,
    }

    all_releases = []

    try:
        while True:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()

            releases = data.get("releases", [])
            all_releases.extend(releases)

            cursor = data.get("cursor")
            if not cursor or not releases:
                break

            params["cursor"] = cursor

    except Exception as e:
        print("Find-a-Tender error:", e)

    return all_releases


# ---------------------------------------------------------
# Main Page
# ---------------------------------------------------------
@app.route("/")
def index():
    cf = get_contracts_finder()
    ft = get_find_tender()

    return render_template(
        "contracts.html",
        cf=cf,
        ft=ft,
        cf_count=len(cf),
        ft_count=len(ft),
        total=len(cf) + len(ft),
    )


if __name__ == "__main__":
    app.run(debug=True)
