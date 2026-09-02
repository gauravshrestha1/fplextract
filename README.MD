# FPL Data Mirror

Solves one specific problem: Claude's cloud/scheduled sessions can `WebFetch`
small FPL API endpoints fine, but `bootstrap-static`'s `elements` array
(600+ players) is too large and gets silently truncated to ~17 entries.

This repo has a GitHub Action that fetches `bootstrap-static` on a schedule,
trims it down to the fields actually needed (price, ownership%, form,
status/injury news, etc.), and commits the result to `fpl-data/players.json`.
That file is small enough for WebFetch to read in full, and lives at a
raw.githubusercontent.com URL — a domain Claude's sandbox can already reach.

## Setup (one-time)

1. Create a new GitHub repo (private is fine — this is public FPL data
   either way, but no reason to make it public).
2. Add these three files to it, keeping the folder structure:
   - `.github/workflows/fpl-mirror.yml`
   - `scripts/fetch_fpl_data.py`
   - `README.md` (this file)
3. Push to `main`. GitHub Actions should pick up the workflow automatically.
4. Go to the repo's **Actions** tab → **FPL Data Mirror** → **Run workflow**
   to trigger the first run manually (don't wait for the first scheduled
   cron tick). Check that `fpl-data/players.json` appears after it finishes.
5. Note your mirror's raw URL, it will be:

   ```
   https://raw.githubusercontent.com/<your-username>/<repo-name>/main/fpl-data/players.json
   ```

   Give this URL to Claude (in the FPL state doc / scheduled task
   instructions) as the source for player-level data going forward.

## What this does and doesn't fix

- ✅ Full live player database — prices, ownership %, form, status/injury
  news, minutes, xG/xA, transfers in/out this event — all resolvable by
  name now, not just low-ID Arsenal players.
- ✅ No more WebFetch truncation, no browser needed for this data.
- ❌ Does **not** fix `/api/my-team/{id}/` (free transfers, bank) — that
  endpoint needs your logged-in session cookie, which a public mirror
  can't have. Free-transfer count still needs either a live browser
  session or your manual confirmation.
- ❌ Not literally real-time — refreshes every 2 hours by default (cron
  schedule in the workflow). Tighten the cron expression if you want
  faster updates, e.g. `*/30 * * * *` for every 30 minutes.

## Maintenance

Nothing ongoing — it's a fire-and-forget GitHub Action. If FPL ever changes
its `bootstrap-static` schema, `fetch_fpl_data.py` may need a small update.
