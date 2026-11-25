"""
scripts/sample_data.py — sample data for trying the sports portal on your own
computer. Run it through scripts/sample_data.sh, never by itself: the script
refuses to run unless it is writing to its own SQLite file (sample_sports.db)
with mail and WhatsApp off.

What it makes (every name is made up):
  * Logins (password SportsDemo@2026):
      admin@example.com        Super Admin
      spoc@example.com         Club SPOC (owns both events)
      coordinator@example.com  Event Coordinator (scores matches)
  * Men's league: 8 teams, each with a logo and 9 players with jersey numbers;
    two pools of 4 with seeds, one round in each pool, an inter-pool round,
    PKL Season 12 points and PKL mode (raid by raid). M-01 to M-03 have
    results, and M-04 is being scored live (first half, a few raids in).
  * Women's league: 3 teams in a triangular series; W M-01 has a result.

The teams register through the real registration form, and the fixtures,
results and raids go through the same pages the SPOC and coordinator use, so
the data is exactly what the portal itself would make.
"""
import datetime
import io
import itertools
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.chdir(REPO)
if not os.environ.get('LOCAL_SQLITE_PATH', '').endswith('sample_sports.db'):
    sys.exit('Run this through scripts/sample_data.sh: it uses its own database file.')
if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('DATABASE_URL') or os.environ.get('CLOUD_SQL_INSTANCE'):
    sys.exit('Refusing: this looks like a real database.')
if os.environ.get('MAIL_USER') or os.environ.get('TWILIO_ACCOUNT_SID'):
    sys.exit('Refusing: mail or WhatsApp is switched on.')

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

import app as app_module  # noqa: E402
import services_sports  # noqa: E402
from extensions import limiter  # noqa: E402
from models import db  # noqa: E402

PASSWORD = 'SportsDemo@2026'
ADMIN, SPOC, COORD = 'admin@example.com', 'spoc@example.com', 'coordinator@example.com'
FONT = os.path.join(REPO, 'static', 'fonts', 'certificate', 'Montserrat-Bold.ttf')

MEN = {   # team: (pool, seed, colour, captain first, then the players)
    'Garuda Sena': ('A', 1, '#1d4ed8', ['Arjun', 'Bharat', 'Chetan', 'Darshan', 'Eshwar', 'Farhan', 'Girish', 'Hemanth', 'Imran']),
    'Malnad Fighters': ('A', 2, '#15803d', ['Jagadish', 'Kiran', 'Lokesh', 'Manoj', 'Nikhil', 'Omkar', 'Prakash', 'Qadir', 'Rahul']),
    'Neuro Ninjas': ('A', 3, '#7c3aed', ['Sagar', 'Tejas', 'Uday', 'Varun', 'Wasim', 'Yash', 'Zubair', 'Abhay', 'Basava']),
    'Vajra': ('A', 4, '#b91c1c', ['Chandan', 'Deepak', 'Ganesh', 'Harish', 'Ishaan', 'Jeevan', 'Karthik', 'Lakshman', 'Mahesh']),
    'Gaja Pade': ('B', 1, '#a16207', ['Naveen', 'Omprakash', 'Pavan', 'Raghu', 'Santosh', 'Tarun', 'Umesh', 'Vinay', 'Yogesh']),
    'Code Blue': ('B', 2, '#0e7490', ['Akash', 'Bhuvan', 'Chiranth', 'Dhanush', 'Gagan', 'Hrithik', 'Jayanth', 'Kushal', 'Likhith']),
    'Veera Yodha': ('B', 3, '#c2410c', ['Madhu', 'Nandan', 'Pradeep', 'Rakesh', 'Shashank', 'Tilak', 'Vikas', 'Yatish', 'Anil']),
    'Gandaberunda Warriors': ('B', 4, '#334155', ['Bhaskar', 'Chethan', 'Dinesh', 'Gopal', 'Hanumanth', 'Jagan', 'Kumar', 'Mallesh', 'Nagaraj']),
}
WOMEN = {
    'Shakti': ('', 0, '#be185d', ['Ananya', 'Bhavya', 'Chaitra', 'Divya', 'Esha', 'Gowri', 'Harini', 'Ishita', 'Jyothi']),
    'Durga': ('', 0, '#9333ea', ['Kavya', 'Lavanya', 'Meghana', 'Nayana', 'Pooja', 'Rashmi', 'Sahana', 'Tanvi', 'Usha']),
    'Chamundi': ('', 0, '#0f766e', ['Vani', 'Yamini', 'Akshata', 'Bindu', 'Deepa', 'Geetha', 'Hema', 'Keerthi', 'Lata']),
}
JERSEYS = ['7', '1', '3', '5', '9', '10', '11', '22', '33']    # the captain's, then each player's

flask_app = app_module.app
flask_app.config.update(WTF_CSRF_ENABLED=False)
limiter.enabled = False
today = datetime.date.today()
last = today + datetime.timedelta(days=2)
_taps = itertools.count(1)


def user(email, role, name):
    db.collection('users').document(email).set({
        'email': email, 'name': name, 'role': role, 'category': 'Sports' if role != 'SuperAdmin' else 'All',
        'password': generate_password_hash(PASSWORD, method='pbkdf2:sha256'),
        'needs_password_reset': False, 'is_active': True}, merge=False)


def login(email, role):
    client = flask_app.test_client()
    resp = client.post('/login', data={'role': role, 'email': email, 'password': PASSWORD})
    assert resp.status_code == 302 and '/login' not in resp.headers['Location'], resp.data[:300]
    return client


def logo_png(name, colour):
    """A round badge with the team's initials."""
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, 248, 248), fill=colour, outline='white', width=10)
    letters = ''.join(w[0] for w in name.split()[:2]).upper()
    font = ImageFont.truetype(FONT, 96)
    box = draw.textbbox((0, 0), letters, font=font)
    draw.text(((256 - box[2] - box[0]) / 2, (256 - box[3] - box[1]) / 2), letters, fill='white', font=font)
    out = io.BytesIO()
    img.save(out, 'PNG')
    return out.getvalue()


def make_event(spoc, title, gender, teams_text):
    for old in db.collection('events').where('title', '==', title).stream():
        sys.exit(f'"{title}" exists already ({old.id}). Delete sample_sports.db to start again.')
    resp = spoc.post('/spoc/create_event', data={
        'title': title, 'category': 'Sports', 'description': teams_text, 'rules': 'PKL Season 12 rules.',
        'date': today.isoformat(), 'time': '09:00', 'reg_deadline': today.isoformat(), 'venue': 'Main Ground',
        'participation_type': 'Team', 'team_min': '7', 'team_max': '12', 'max_participants': '16', 'reg_fee': '0',
        'prize_1': '15000', 'prize_2': '10000', 'prize_3': '5000', 'visibility': 'public'})
    assert resp.status_code == 302, resp.data[:300]
    [event_id] = [d.id for d in db.collection('events').where('title', '==', title).stream()]
    db.collection('events').document(event_id).update({
        'event_type': 'sports_tournament', 'category': 'Sports', 'status': 'active', 'visibility': 'public',
        'details': {'sport': 'Kabaddi', 'format': 'League then knockout', 'gender': gender,
                    'match_rules': 'PKL Season 12: 2 halves of 20 minutes'},
        'limits': {'team_min': 7, 'team_max': 12, 'max_participants': 16},
        'is_team_event': True, 'min_team_size': 7, 'max_team_size': 12,
        'date': today.isoformat(), 'time': '09:00', 'start_datetime': f'{today.isoformat()} 09:00',
        'end_date': last.isoformat(), 'end_datetime': f'{last.isoformat()} 18:00',
        'reg_deadline': last.isoformat(),          # open while the teams register; closed again below
        'form_member_fields': {'usn': 'optional', 'phone': 'off', 'jersey_name': 'required'},
        'staff': [{'name': 'Court Coordinator', 'email': COORD, 'role': 'EventCoordinator'}]})
    from routes_forms import _simple_schema_fallback
    db.collection('event_forms').document(event_id).set({
        'event_id': event_id, 'form_type': 'custom', 'source': 'wizard',
        'fields': _simple_schema_fallback(is_team=True)['fields']})
    db.collection('events').document(event_id).update({'has_custom_form': True, 'form_type': 'custom', 'form_chosen': True})
    return event_id


def register(event_id, teams, start):
    """Every team through the registration form, with its logo and jerseys."""
    ids = {}
    for n, (team, (_pool, _seed, colour, squad)) in enumerate(teams.items(), start=start):
        captain, players = squad[0], squad[1:]
        tag = team.lower().replace(' ', '')
        form = {'privacy_consent': 'yes', 'full_name': captain, 'email': f'{tag}.captain@example.com',
                'phone': f'98765{n:05d}', 'usn': f'1SN22KB{n:03d}', 'team_name': team,
                'lead_jersey': JERSEYS[0], 'lead_jersey_name': captain.upper(), 'lead_dob': f'2004-0{n % 9 + 1}-1{n % 9}',
                'lead_position': 'Raider', 'team_logo': (io.BytesIO(logo_png(team, colour)), 'logo.png')}
        for i, (name, number) in enumerate(zip(players, JERSEYS[1:]), start=1):
            form.update({f'member_{i}_name': name, f'member_{i}_email': f'{tag}.{name.lower()}@example.com',
                         f'member_{i}_usn': f'1SN22KB{n}{i:02d}', f'member_{i}_jersey': number,
                         f'member_{i}_jersey_name': name.upper(), f'member_{i}_dob': f'200{3 + i % 4}-1{i % 3}-0{i}',
                         f'member_{i}_position': ('Raider', 'Defender', 'All-rounder')[i % 3]})
        resp = flask_app.test_client().post(f'/forms/submit/{event_id}', data=form, content_type='multipart/form-data')
        assert resp.status_code == 302, (team, resp.data[:300])
        [reg] = [d for d in db.collection('registrations').where('event_id', '==', event_id).stream()
                 if d.to_dict().get('team_name') == team]
        db.collection('registrations').document(reg.id).update({'status': 'Confirmed', 'attendance': 'Present'})
        ids[team] = reg.id
        print(f'  registered {team}: {len(reg.to_dict().get("members") or [])} players')
    db.collection('events').document(event_id).update({'reg_deadline': today.isoformat()})
    return ids


def tournament(event_id):
    return db.collection('events').document(event_id).get().to_dict()['tournament']


def final(client, event_id, match, home, away):
    resp = client.post(f"/tournament/{event_id}/match/{match['id']}/final", data={'home': str(home), 'away': str(away)})
    assert resp.status_code == 302, resp.data[:300]


def tap(client, event_id, match, **body):
    body['tap'] = f'sample-{next(_taps)}'
    resp = client.post(f"/tournament/{event_id}/match/{match['id']}/score", json=body)
    assert resp.status_code == 200, (body, resp.get_json())
    return resp.get_json()


# ── Logins ──────────────────────────────────────────────────────────────────
user(ADMIN, 'SuperAdmin', 'Sample Admin')
user(SPOC, 'ClubSPOC', 'Sports SPOC')
user(COORD, 'EventCoordinator', 'Court Coordinator')
spoc = login(SPOC, 'ClubSPOC')
coord = login(COORD, 'EventCoordinator')

# ── Men: two pools, an inter-pool round, PKL mode ─────────────────────────
print("Men's league")
men_id = make_event(spoc, 'Sample Kabaddi League (Men)', 'Men',
                    '8 teams in two pools, an inter-pool round, semi-finals and the final.')
men = register(men_id, MEN, 1)
data = {'format': 'league_knockout', 'rules': 'pkl12', 'scoring': 'pkl', 'legs': '1', 'pools': 'two', 'cross': 'yes',
        'third_place': 'yes'}
for team, (pool, seed, _c, _s) in MEN.items():
    data[f'pool_{men[team]}'], data[f'seed_{men[team]}'] = pool, str(seed)
assert spoc.post(f'/tournament/{men_id}/generate', data=data).status_code == 302
t = tournament(men_id)
names = services_sports.names(t)
for m, (h, a) in zip(t['matches'][:3], [(38, 31), (29, 33), (41, 27)]):
    final(coord, men_id, m, h, a)
    print(f"  {services_sports.match_no(m)} {names[m['home']]} {h}–{a} {names[m['away']]}")

# M-04 live: line-ups, the toss, a few raids
m = t['matches'][3]
squad = {side: MEN[names[m[side]]][3] for side in ('home', 'away')}
assert coord.get(f"/tournament/{men_id}/match/{m['id']}/score").status_code == 200
tap(coord, men_id, m, op='lineup', home=squad['home'][:7], away=squad['away'][:7])
tap(coord, men_id, m, op='phase', action='start', first='home')
tap(coord, men_id, m, op='raid', team='home', outcome='touch', raider=squad['home'][0], touched=[squad['away'][1]])
tap(coord, men_id, m, op='raid', team='away', outcome='tackled', raider=squad['away'][0], touched=[squad['home'][2]])
tap(coord, men_id, m, op='raid', team='home', outcome='empty', raider=squad['home'][1], touched=[])
state = tap(coord, men_id, m, op='raid', team='away', outcome='touch', raider=squad['away'][3],
            touched=[squad['home'][3], squad['home'][4]])['state']
print(f"  {services_sports.match_no(m)} live: {state['home']['name']} {state['home']['total']}–"
      f"{state['away']['total']} {state['away']['name']} ({state['phase']})")

# ── Women: a triangular series ────────────────────────────────────────────
print("Women's league")
women_id = make_event(spoc, 'Sample Kabaddi League (Women)', 'Women',
                      '3 teams: each plays the other two, then 1st v 2nd in the final.')
women = register(women_id, WOMEN, 20)
assert spoc.post(f'/tournament/{women_id}/generate',
                 data={'format': 'triangular', 'rules': 'pkl12', 'scoring': 'pkl'}).status_code == 302
t = tournament(women_id)
names = services_sports.names(t)
m = t['matches'][0]
final(coord, women_id, m, 26, 22)
print(f"  {services_sports.format_name(t)}: {len(t['matches'])} matches; "
      f"{services_sports.match_no(m)} {names[m['home']]} 26–22 {names[m['away']]}")

print(f"""
Done. Start the site with:  zsh scripts/sample_data.sh serve
Then open http://localhost:5001/login  (password for every login: {PASSWORD})
  Super Admin        {ADMIN}
  Club SPOC          {SPOC}
  Event Coordinator  {COORD}
Men:    http://localhost:5001/tournament/{men_id}
Women:  http://localhost:5001/tournament/{women_id}
Public: http://localhost:5001/tournament/fixtures/{men_id}
""")
