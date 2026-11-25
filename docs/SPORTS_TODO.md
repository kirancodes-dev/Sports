# Sports portal: work list

One item at a time, in order unless the owner says otherwise. When an item is
done: Status → DONE, add the commit and the test that proves it. New problems
go in at the bottom with the next free number (SP-12, SP-13, …).

| ID | Title | Status |
|---|---|---|
| SP-01 | Replacing the fixtures keeps the old ones, with their results, and a button brings them back | TODO |
| SP-02 | Take out the parts that are not about sports | TODO |
| SP-03 | A sports home page and menus | TODO |
| SP-04 | Deploy this repo on its own service and database | TODO |
| SP-05 | One scorer per match, and a way to take over | TODO |
| SP-06 | Taps not yet sent survive a page reload | TODO |
| SP-07 | Season awards: best raider, best defender, most valuable player | TODO |
| SP-08 | A blank paper score sheet for each match | TODO |
| SP-09 | Teams level on everything are ordered by name | TODO |
| SP-10 | Card rules (green, yellow, red) are shown as done | TODO |
| SP-11 | Bring back one match's raid record from a database backup | TODO |
| SP-12 | IPL-style playoffs: Qualifier 1, Eliminator, Qualifier 2, final | DONE |

---

### SP-01 — Replacing the fixtures keeps the old ones, with their results, and a button brings them back

**Why.** On 24 Nov 2026, during the men's league, the owner changed a points
setting and pressed "Replace Fixtures". It made new fixtures in a different
order and deleted every result and every match's raid-by-raid record: the
generate route (`routes_sports.py`, `generate`) calls
`services_live_match.forget(db, event_id)`. Nothing kept a copy.

**Build.**
1. Before fixtures are replaced, save the current tournament **and** every live
   match record of the event, as one version with a time and who did it. Keep
   at least the last 5 versions.
2. On the tournament page: **Restore previous fixtures**. It lists the saved
   versions (time, who, how many results), and restoring one puts back the
   tournament and its live match records. The version being replaced is saved
   first, so a restore can itself be undone.
3. "Replace Fixtures" with any result entered or any match scored: say
   clearly how many results and scored matches will be put aside, and point
   to the **points rule** form and the **fixture sheet** for changes that keep
   results.
4. The same keep-a-copy for the playoffs undo (`/playoffs/undo`), which also
   forgets live records.

**Tests.** Replace and then restore gives back the same fixtures, results,
points tables, top raiders and score sheets. Restoring twice in a row goes
back and forth. A coordinator can't restore. The warning names the count.

### SP-02 — Take out the parts that are not about sports

One feature per change: hackathons and judging, seminars and sessions, exams,
placement, NAAC, sponsors, marketing and reach, gamification, portfolio, the
matchmaker and AI matching, interact and polls. For each: remove its routes,
templates, services, menu links and tests. Then run the full tests. Keep
anything sports uses: login, users and roles, events, registrations and team
forms, tickets and check-in, certificates, notifications and mail, uploads,
the audit log. If a feature is shared, say so in the item and leave it.

### SP-03 — A sports home page and menus

The home page leads with **Watch live** (Men / Women), today's matches, the
points tables and the latest results. The menus show only sports. The college
logo and colours stay.

### SP-04 — Deploy this repo on its own service and database

Write the owner's Cloud Shell steps in `docs/DEPLOY.md`, following its
existing steps with new names:
- its own Cloud SQL instance and database, and its own secrets;
- its own Cloud Run service (for example `sports`);
- the first Super Admin.

The owner runs them. Check the result by the page's content.

### SP-05 — One scorer per match, and a way to take over

Two phones scoring the same match is confusing. The first to open a match
holds it; another sees who holds it and can **Take over**, and the first is
told.

### SP-06 — Taps not yet sent survive a page reload

On a weak connection a tap waits to be sent. If the page reloads, it is lost.
Keep unsent taps in the browser (localStorage) and send them, in order, when
the page comes back. Each tap already has an id, so the same tap counts once.

### SP-07 — Season awards: best raider, best defender, most valuable player

From the season's raid and tackle points: best raider, best defender and
MVP, each with a certificate the SPOC can issue.

### SP-08 — A blank paper score sheet for each match

The score sheet PDF with the teams, players and jersey numbers filled in, and
empty boxes for the points, to fill in by hand when a phone can't be used.

### SP-09 — Teams level on everything are ordered by name

When two teams are level on points, score difference and points scored, the
table orders them by name. Check it, and test it with 3 teams, as in the
women's series. This was UPG-412 in the main portal.

### SP-10 — Card rules (green, yellow, red) are shown as done

Cards were built in the main portal (UPG-447), but UPG-418 still says TODO.
Check the cards work here, and note it.

### SP-11 — Bring back one match's raid record from a database backup

Write the steps (a copy of the database from a backup, read the one match's
records, write them back to the live database) for a match whose raid
record was deleted. The owner runs them. Nothing else on the live database
changes.

### SP-12 — IPL-style playoffs: Qualifier 1, Eliminator, Qualifier 2, final

**DONE** (UPG-479 in the main portal, `e28cab8` there; live on the main
portal as `saptha-e28c`). The owner asked for the pool playoffs in the IPL
format: 1st A v 1st B (Qualifier 1), 2nd A v 2nd B (Eliminator), Q1's loser v
the Eliminator's winner (Qualifier 2), then Q1's winner v Q2's winner in the
final: 4 matches. On the tournament page: Playoffs → Playoff format → IPL
style → Save the format. Choosing it changes no match, result or table;
semi-finals stay the default. Q2's loser is third. Tests:
`tests/test_ipl_playoffs.py`.
