# Sports

The sports portal of Sapthagiri NPS University: team registration, fixtures,
live scoring, the big screen, points tables, score sheets and certificates.
It runs the **Sapthagiri Pro Kabaddi Premier League** (men's and women's).

This repository started as a copy of the SapthaEvent portal on 25 Nov 2026.
It has its own deployment and its own database, so nothing here touches the
main portal. The parts that are not about sports (hackathons, seminars, exams,
placement, NAAC, sponsors) are still in the code and will be taken out step by
step; see "What happens next".

---

## The home page

- **Events:** the sports events open for registration.
- **Watch live:** choose Men or Women, then **Watch live scoring**. It opens the
  match being played, with the score, the clock, who is raiding and the
  players on the mat.
- **Fixtures and tables:** each tournament has a public page with the pools,
  the points tables, every match and its result, the road to the final and
  the top raiders. No login is needed.

## Logging in

Open `/login`, choose your role, then type your email and password.

| Role | What they do |
|---|---|
| **Super Admin** | Runs the whole portal: users, events, settings. Also needs the master secret key. |
| **Club SPOC** | Owns a sports event: creates it, assigns coordinators, makes the fixtures, adds logos, uploads the fixture sheet, makes the playoffs, publishes results, issues certificates. Can score any match. |
| **Event Coordinator** | Scores matches live from a phone or types a final score; postpones a match; checks teams in. Can't change the fixtures. |
| **Student** | Registers a team (captain plus players, with jersey numbers) and gets a ticket. |

The audience and the big screen need no login.

## How the Kabaddi league runs

The full step-by-step guide is
[docs/guides/KABADDI_PREMIER_LEAGUE_GUIDE.md](docs/guides/KABADDI_PREMIER_LEAGUE_GUIDE.md).
In short:

1. **Create the event** (SPOC): type Sports tournament, sport Kabaddi, format
   League then knockout, team participation.
2. **Register the teams:** each captain registers the team with its logo and
   every player's name and jersey number.
3. **Assign the coordinators** who will score.
4. **Make the fixtures** (SPOC), once:
   - **Men (8 teams):** two pools, A and B, with a seed for each team, and an
     inter-pool round (A1 v B1, A2 v B2, …). Then semi-finals 1st A v 2nd B
     and 1st B v 2nd A, a third-place match and the final.
   - **Women (3 teams):** a **triangular series**. Each team plays the other
     two, then 1st and 2nd in the table play the final, and the third team
     is third.
   - Points rule: PKL Season 12 (win 2, no ties: a level score goes to a
     5-raid shootout), or your own numbers (win, tie, loss, close loss).
   - **PKL mode** on: matches are scored raid by raid.
5. **Logos and schedule:** add team logos; download the fixture sheet, fill in
   the teams, dates, times and venues, and upload it.
6. **Score each match** (coordinator or SPOC): open the match → **Score live**.
   - Before the start, tap each team's seven starters and save the line-ups,
     choose who raids first, then **Start 1st half**.
   - Every raid is three taps: the raider, the defenders he touched (or who
     tackled him), then how the raid ended (touch points, tackled, bonus,
     empty raid, out of court).
   - The portal counts the points, puts players out and brings them back,
     and counts all outs, super tackles and do-or-die raids.
   - **Half time**, **Start 2nd half**, then **Full time: save the result**.
   - Missed raids? **Type the final score** and the match ends with it.
7. **What the audience sees:** the scores, the tables, the road to the final
   and the big screen all update by themselves. Each match has a score sheet
   PDF with the college logo, both teams, points by half, line-ups, every
   player's points and signature lines.
8. **Playoffs and results:** after the league, **Make the playoffs**, score the
   semi-finals, third place and final, then **Publish results** and issue
   the certificates.

### Don't lose results

- **Never use "Replace Fixtures" once matches have been played.** It makes new
  fixtures and deletes every result and every match's raid-by-raid record.
- To change the points rule, use the **points rule** form: it keeps every
  match and works the table out again.
- To change which teams play which match, or the dates, upload the
  **fixture sheet** or use a match's **change teams** form.
- A mistake in one match: **Undo last**, **Remove** a point, **Reopen the
  match**, or **Type the final score**.

## Run it locally

You need Python 3.11. SQLite is used in development, so no database set-up
is needed.

```bash
git clone https://github.com/kirancodes-dev/Sports.git
cd Sports
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # then fill in what you need
python app.py                 # http://localhost:5001
```

Make the first Super Admin (local database only):

```bash
SUPER_ADMIN_EMAIL=admin@local.test SUPER_ADMIN_PASS='a strong password' python init_superadmin.py
```

Run the tests:

```bash
python -m pytest -o addopts="" -q
```

## Deploying

This repository needs **its own** Cloud Run service and **its own** database.
Don't point it at the main portal's database, or both would share and change
the same data. [docs/DEPLOY.md](docs/DEPLOY.md) has every step: the database,
the secrets, building the image and the deploy command. Use a different
service name (for example `sports`) and a different database instance.

Never commit `.env`, a service account key, or a local `.db` file.

## What happens next

1. Take out the parts that are not about sports, one at a time, running the
   tests after each.
2. A sports-only home page and menus.
3. Keep the previous fixtures and their results whenever fixtures are
   replaced, with a button to go back.

## License

See [LICENSE](LICENSE).
