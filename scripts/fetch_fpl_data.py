#!/usr/bin/env python3
"""
Fetches FPL's public bootstrap-static endpoint and writes a trimmed,
WebFetch-friendly JSON mirror to fpl-data/players.json.

Uses only the standard library — no pip install needed in CI.
"""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "fpl-data" / "players.json"


def fetch_bootstrap():
    req = urllib.request.Request(BOOTSTRAP_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def trim(data):
    teams = {t["id"]: t["short_name"] for t in data["teams"]}
    positions = {p["id"]: p["singular_name_short"] for p in data["element_types"]}

    players = []
    for e in data["elements"]:
        players.append({
            "id": e["id"],
            "web_name": e["web_name"],
            "full_name": f"{e['first_name']} {e['second_name']}",
            "team": teams.get(e["team"], e["team"]),
            "pos": positions.get(e["element_type"], e["element_type"]),
            "price": round(e["now_cost"] / 10, 1),
            "cost_change_event": e["cost_change_event"],
            "selected_by_percent": e["selected_by_percent"],
            "form": e["form"],
            "points_per_game": e["points_per_game"],
            "total_points": e["total_points"],
            "event_points": e["event_points"],
            "status": e["status"],  # a=available, i=injured, d=doubtful, s=suspended, u=unavailable
            "news": e["news"],
            "chance_of_playing_next_round": e["chance_of_playing_next_round"],
            "minutes": e["minutes"],
            "goals_scored": e["goals_scored"],
            "assists": e["assists"],
            "clean_sheets": e["clean_sheets"],
            "ict_index": e["ict_index"],
            "expected_goals": e.get("expected_goals"),
            "expected_assists": e.get("expected_assists"),
            "expected_goals_conceded": e.get("expected_goals_conceded"),
            "transfers_in_event": e["transfers_in_event"],
            "transfers_out_event": e["transfers_out_event"],
        })

    current_event = next((ev["id"] for ev in data["events"] if ev["is_current"]), None)
    next_event = next((ev["id"] for ev in data["events"] if ev["is_next"]), None)
    deadlines = {ev["id"]: ev["deadline_time"] for ev in data["events"]}

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_event": current_event,
        "next_event": next_event,
        "deadlines": deadlines,
        "player_count": len(players),
        "players": players,
    }


def main():
    raw = fetch_bootstrap()
    trimmed = trim(raw)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(trimmed, indent=1))
    print(f"Wrote {trimmed['player_count']} players to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
