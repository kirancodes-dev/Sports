# Working on the Sports portal

Read this first, then `docs/SPORTS_TODO.md` (the work list) and, for anything
about how a match is run, `docs/guides/KABADDI_PREMIER_LEAGUE_GUIDE.md`.

## What this is and who it's for

The sports portal of Sapthagiri NPS University, copied on 25 Nov 2026 from
the SapthaEvent portal. It runs the **Sapthagiri Pro Kabaddi Premier League**:
- **Men:** 8 teams, two pools of 4 with seeds, one round in each pool, then an
  inter-pool round (A1 v B1, …). Then semi-finals (1st A v 2nd B, 1st B v
  2nd A), third place and the final.
- **Women:** 3 teams, a **triangular series**: each plays the other two, then
  1st v 2nd in the final, and the third team is third.
- PKL Season 12 points (win 2, no ties: a level score goes to a 5-raid
  shootout) and **PKL mode**: every raid scored as raider → touched or
  tackled defenders → outcome.

**The owner** is the event's organiser (Club SPOC and Super Admin). They run
the matches on the day and deploy from Google Cloud Shell themselves. Their
messages are short and often sent during a live match. Answer short and
direct, and give ready-to-paste commands. When a match is about to start, the
first job is to keep it running (a workaround on the page), and the code fix
comes second.

## Rules

1. **Never lose match data.** Results, raids, line-ups and player points are
   the most important thing in this repo. Never write code that deletes or
   overwrites them without keeping a copy that can be restored. On 24 Nov 2026,
   "Replace Fixtures" (`/tournament/<id>/generate`) wiped every result and
   every match's raid record (`services_live_match.forget`). SP-01 fixes that.
2. **Never touch the live site or its database.** Don't deploy, push or
   change production settings unless the owner asks. When they do, give the
   Cloud Shell block and let them run it. Check a deploy by the page's
   content, not by the revision name gcloud prints.
3. **This repo has its own deployment** (its own Cloud Run service and its own
   database). It must never point at the main SapthaEvent portal's database.
4. **No secrets or personal data** in code, tests, docs, commits or commands:
   no `.env`, keys, passwords, real emails or phone numbers. Tests and sample
   data use made-up names. Use they/them for people.
5. **Every change gets a test**, and the full test run must pass before you
   finish (known failures below). Never delete, skip or weaken a test to get a
   pass.
6. Work on one item from `docs/SPORTS_TODO.md` at a time. When it's done, mark
   it DONE there with the commit and the test that proves it. Problems found
   along the way go in as new SP items; don't fix them in the same change.

## Run it

```bash
python3.11 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
zsh scripts/sample_data.sh load     # once: sample_sports.db with sample data
zsh scripts/sample_data.sh serve    # http://localhost:5001
zsh scripts/sample_data.sh reset    # start the sample data again
```

The sample data has every login on password `SportsDemo@2026`:
`admin@example.com` (Super Admin), `spoc@example.com` (Club SPOC) and
`coordinator@example.com` (Event Coordinator). It has a men's league with
results and M-04 being scored live, and a women's triangular series. See the
top of `scripts/sample_data.py`.

Tests:

```bash
.venv/bin/python -m pytest tests -o addopts="--tb=short --strict-markers" -q -p no:cacheprovider -rfE
```

Known failures, carried over from the main portal: two coordinator pagination
tests, `test_seminar_e2e`, and `test_no_mail_password_in_tracked_files` when a
local `.env` has a mail password. `test_hackathon_browser` sometimes fails in
the full run and passes alone. Anything else that fails is yours to fix. To
check one area fast, run its files (for example `tests/test_kabaddi_*.py`).

## Where the sports code is

| Area | Files |
|---|---|
| Fixtures, pools, points tables, playoffs, triangular, fixture sheet upload | `services_sports.py`, `routes_sports.py`, `templates/spoc/tournament.html`, `templates/includes/tournament.html` |
| Live scoring (point by point and PKL raid by raid), line-ups, the mat, tie-breaker | `services_live_match.py`, `templates/spoc/live_scorer.html`, `templates/spoc/_pkl_panel.html`, `static/js/live_match.js` |
| Public pages, Watch live and the big screen | `templates/public/live_match.html`, `templates/public/tournament_fixtures.html`, `templates/public/tournament_screen.html`, `static/js/tournament_screen.js` |
| Score sheet PDF | `services_score_sheet.py` |
| Players, jersey numbers, player stats | `services_players.py`, `routes_players.py`, `services_jerseys.py`, `templates/spoc/jerseys.html` |
| Team registration | `routes_forms.py`, `services_team_members.py` |
| Login and roles | `routes_auth.py`, `services_permission.py` |
| Certificates | `services_certificate*.py`, `certificate_pdf.py` |

Tests for these are under `tests/` with names like `test_kabaddi_*`,
`test_live_*`, `test_pkl_*`, `test_tournament_*`, `test_sports_*`,
`test_triangular_series.py` and `test_score_sheet_look.py`.
`tests/test_sports_tournament.py` (the `cup` fixture) and
`tests/test_kabaddi_premier_league.py` (the `league` fixture) set up events
for tests.

## The rest of the code

Hackathons, seminars, exams, placement, NAAC, sponsors and other non-sports
features are still here from the copy. They are taken out under SP-02, one at
a time. Until then, leave them alone unless the item says otherwise.

`docs/FEATURE_REVIEW.md` and `docs/archive/` are the main portal's history.
Read them for background on an old UPG item. Don't add to them; this repo's
work list is `docs/SPORTS_TODO.md`.
