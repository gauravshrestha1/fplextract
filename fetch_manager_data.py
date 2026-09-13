"""
Fetches Gaurav's FPL manager data (overall points, league positions,
current squad picks, and season history) and writes it into fpl-data/
alongside the existing players.json mirror.

Run by GitHub Actions (fpl-manager-mirror.yml), which has normal internet
access — the resulting JSON is then pulled via raw.githubusercontent.com
by scheduled Claude tasks that can't reach fantasy.premierleague.com directly.
"""

import json
import os
import urllib.request

TEAM_ID = os.environ.get("FPL_TEAM_ID", "7063120")
BASE = "https://fantasy.premierleague.com/api"
OUT_DIR = "fpl-data"


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def write_json(filename: str, data):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {path}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Manager summary: overall points, overall rank, team value, bank,
    # and — critically — entry_rank/entry_last_rank per league under
    # leagues.classic, so no league IDs need to be hardcoded.
    manager = fetch_json(f"{BASE}/entry/{TEAM_ID}/")
    write_json("manager.json", manager)

    # Season history: gameweek-by-gameweek points/rank, chips used,
    # transfer costs, and past-season summaries.
    history = fetch_json(f"{BASE}/entry/{TEAM_ID}/history/")
    write_json("history.json", history)

    # Current gameweek's squad picks: 15 players, captain/vice-captain,
    # formation, and any active chip.
    bootstrap = fetch_json(f"{BASE}/bootstrap-static/")
    events = bootstrap.get("events", [])
    current_event = next((e["id"] for e in events if e.get("is_current")), None)
    if current_event is None:
        current_event = next((e["id"] for e in events if e.get("is_next")), None)

    if current_event is not None:
        picks = fetch_json(f"{BASE}/entry/{TEAM_ID}/event/{current_event}/picks/")
        write_json("picks.json", picks)
    else:
        print("could not determine current/next event id — skipped picks.json")


if __name__ == "__main__":
    main()
