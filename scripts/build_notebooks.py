"""Generate the five mission notebooks.

The notebooks are authored here as (kind, source) cell lists and written out
with nbformat, which guarantees valid .ipynb files. Cell kinds:

    md(text)                — a markdown cell
    code(src)               — a runnable code cell
    magic(src)              — same as code; marks a "just run it" wow cell
    try_it(student, solution, show_answer=True)
        — an exercise. The student notebook gets `student` (with ____ blanks
          or values to tweak) plus a commented 🔑 ANSWER cell. Building with
          --solutions swaps in `solution` so tests prove every answer works.

Usage:
    python scripts/build_notebooks.py                  # student notebooks
    python scripts/build_notebooks.py --solutions -o <dir>   # solved variants
"""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat as nbf


def md(source: str):
    return ("md", source)


def code(source: str):
    return ("code", source)


def magic(source: str):
    return ("code", source)


def try_it(student: str, solution: str, show_answer: bool = True):
    return ("try", student, solution, show_answer)


def build(cells: list, path: Path, solutions: bool = False) -> None:
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3",
    }
    out = []
    for cell in cells:
        kind = cell[0]
        if kind == "md":
            out.append(nbf.v4.new_markdown_cell(cell[1]))
        elif kind == "code":
            out.append(nbf.v4.new_code_cell(cell[1]))
        elif kind == "try":
            _, student, solution, show_answer = cell
            out.append(nbf.v4.new_code_cell(solution if solutions else student))
            if show_answer:
                hidden = "\n".join("# " + line for line in solution.splitlines())
                out.append(nbf.v4.new_code_cell(
                    "# 🔑 ANSWER — peek only if you're stuck! "
                    "(remove the # marks to run it)\n" + hidden
                ))
    nb["cells"] = out
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, str(path))
    print(f"  📓 wrote {path}")


# ===========================================================================
# Mission 1 — Rookie Camp
# ===========================================================================

def mission_1() -> list:
    return [
        md("""\
# 🏈 Mission 1: Rookie Camp

**Welcome to the Fantasy Football Lab!** Over five missions you'll go from
rookie to the family's data analyst — building your own draft rankings and
setting your lineup like the pros do, with real NFL data.

⏱️ *This mission takes about 20 minutes.*

## How this place works

This page is a **notebook** — it mixes words (like these) with **code cells**
you can run yourself. The gray boxes are code. To run one:

1. Click on it
2. Hold **Shift** and press **Enter**

The result appears right below the cell. Try it on the cell below! 👇

**Lab rules:**
- 🟢 Run cells **top to bottom** — each one builds on the one before it
- 🧪 You can't break anything. Worst case, use the menu:
  `Kernel → Restart Kernel and Run All Cells…` and you're back
- Watch for these signs:
  - ⭐ **TRY IT** — your turn to change or fill in some code
  - 🔑 **ANSWER** — the answer, hiding behind `#` marks (peek if stuck!)
  - 🪄 **MAGIC** — fancy code that makes something awesome. You do **not**
    need to understand it yet — just run it and enjoy the show!\
"""),
        code('print("Touchdown! 🏈  You just ran your first line of code.")'),
        md("""\
## Variables: labeled boxes

Code remembers things with **variables** — imagine a labeled box you can put
a value in. Below we put the word `"Rookie"` in a box labeled `my_name`.
Anywhere we use `my_name` later, Python opens the box.\
"""),
        try_it(
            '''\
my_name = "Rookie"        # ⭐ TRY IT: put YOUR name between the quotes
favorite_team = "Lions"   #    ...and your favorite team here, then run me!
print("Welcome to camp,", my_name, "— go", favorite_team + "!")\
''',
            '''\
my_name = "Jordan"
favorite_team = "Eagles"
print("Welcome to camp,", my_name, "— go", favorite_team + "!")\
''',
            show_answer=False,
        ),
        md("""\
## Fantasy points are just math

Every fantasy league turns real football plays into points. If a touchdown is
worth 6 and every 10 rushing yards is worth 1, then code is your calculator:\
"""),
        try_it(
            '''\
touchdowns = 2
rushing_yards = 87

points = touchdowns * 6 + rushing_yards * 0.1
print("That running back scored", points, "fantasy points!")

# ⭐ TRY IT: what's a MONSTER 3-touchdown, 150-yard game worth?
# Change the numbers above and run the cell again.\
''',
            '''\
touchdowns = 3
rushing_yards = 150

points = touchdowns * 6 + rushing_yards * 0.1
print("That running back scored", points, "fantasy points!")\
''',
            show_answer=False,
        ),
        md("""\
## 📡 Meet the data

Enough warm-up — time for the real thing. The next cell loads **every NFL
player's real game stats from the 2021–2025 seasons**, from the same free
community dataset the pros use (it's called *nflverse*).\
"""),
        code('''\
import ffkit as ff        # our toolbox for the whole lab
from ffkit import ____    # the fill-in-the-blank marker for TRY IT cells

players = ff.load_players()
print(f"Loaded {len(players):,} real player-game performances! 🎉")\
'''),
        code('players.head(8)   # .head(8) means "show me the first 8 rows"'),
        md("""\
That's a **table** (data people call it a *DataFrame*). Every **row** is one
player in one real game. Every **column** is a stat: `passing_yards`,
`rushing_tds`, `receptions`... even `def_sacks` for defensive players.

90,000 rows is way too many to read. So we let the computer do the reading.\
"""),
        md("""\
## 🏆 Your first leaderboard

Raw stats become **points** when we apply scoring rules (Mission 3 is all
about rules — for now we'll use our family league's settings).\
"""),
        code('''\
rules = ff.rules("NFL Standard + IDP")   # our league's scoring settings
scored = ff.score(players, rules)        # turn every stat line into points
ff.top_players(scored, season=2025)\
'''),
        md("""\
**Reading the table:** `total` = points for the whole season, `per_game` =
average per week, `best_week` = their single biggest explosion.

Notice anything? Quarterbacks tend to crowd the top — they touch the ball on
every single play. Remember that for draft day... 🤔\
"""),
        try_it(
            '''\
# ⭐ TRY IT: which players ruled a DIFFERENT season?
# Replace the ____ with a year. We have 2021, 2022, 2023, 2024 and 2025.
ff.top_players(scored, season=____)\
''',
            'ff.top_players(scored, season=2022)',
        ),
        try_it(
            '''\
# ⭐ TRY IT: who were the 10 best running backs of 2025?
# Positions you can use: "QB", "RB", "WR", "TE", "K" — and on defense:
# "DL" (line), "LB" (linebackers), "DB" (backs)
ff.top_players(scored, season=2025, position=____)\
''',
            'ff.top_players(scored, season=2025, position="RB")',
        ),
        md("""\
## 🪄 MAGIC: a whole season at a glance

You do **not** need to understand this code yet — just run it! Hover your
mouse over the squares. Each row is a player, each column is a week, and
**dark blue squares are monster games**.\
"""),
        magic('ff.viz.weekly_heatmap(scored, season=2025, top=15)'),
        md("""\
## 🎉 Mission complete!

Look what you just did:
- ✅ Ran real Python code
- ✅ Used variables and math
- ✅ Loaded **five seasons** of real NFL data
- ✅ Built a leaderboard — and controlled what it shows

**Next → Mission 2: The Scouting Report.** You'll learn to tell a true
superstar from a one-week wonder — the #1 skill of every great drafter.\
"""),
    ]


# ===========================================================================
# Mission 2 — The Scouting Report
# ===========================================================================

def mission_2() -> list:
    return [
        md("""\
# 🕵️ Mission 2: The Scouting Report

Anyone can read a leaderboard. A **scout** knows the story behind the
numbers: Who shows up every week? Who disappears? Whose big season was real,
and whose was one lucky game?

⏱️ *About 25 minutes.*\
"""),
        code('''\
import ffkit as ff
from ffkit import ____

players = ff.load_players()
rules = ff.rules("NFL Standard + IDP")
scored = ff.score(players, rules)
print("Scouting station ready! 🕵️")\
'''),
        md("""\
## One player under the microscope

`ff.player_weeks` shows one player's real week-by-week scores. Let's scout
Bijan Robinson's 2025:\
"""),
        code('ff.player_weeks(scored, "Bijan Robinson", season=2025)'),
        try_it(
            '''\
# ⭐ TRY IT: scout YOUR favorite player!
# Put their name between quotes: "Josh Allen", "CeeDee Lamb", anyone.
# (If the spelling is a little off, the lab will suggest names.)
ff.player_weeks(scored, ____, season=2025)\
''',
            'ff.player_weeks(scored, "Josh Allen", season=2025)',
        ),
        md("""\
## 🪄 MAGIC: the player card

Run this to print a trading-card profile — photo, team colors, and their
last 10 games as a mini-chart. Then ⭐ swap in any player you want!\
"""),
        try_it(
            '''\
teams = ff.load_teams()
ff.viz.player_card(scored, "Bijan Robinson", teams)   # ⭐ change the name!\
''',
            '''\
teams = ff.load_teams()
ff.viz.player_card(scored, "Puka Nacua", teams)\
''',
            show_answer=False,
        ),
        md("""\
## Totals can trick you

Imagine two receivers:

| | games played | season total | per game |
|---|---|---|---|
| **Marathon Mike** | 17 | 170 pts | 10.0 |
| **Rocket Raj** | 10 | 140 pts | 14.0 |

Mike scored more **total** points. But when Raj actually played, he was way
better! Who would you rather draft? (Careful — will Raj get hurt again?)

There's no single right answer — but a scout always checks **both** numbers:\
"""),
        code('''\
print("Wide receivers sorted by TOTAL season points:")
display(ff.top_players(scored, season=2025, position="WR", n=5, by="total"))

print("The same season, sorted by points PER GAME:")
display(ff.top_players(scored, season=2025, position="WR", n=5, by="per_game"))\
'''),
        md("""\
👀 Compare the two lists. Anyone high on the second list but missing from the
first probably **missed games** — huge when healthy, but risky.\
"""),
        try_it(
            '''\
# ⭐ TRY IT: which tight ends (TE) had the biggest single BOOM week in 2025?
# Your choices for by= are "total", "per_game", or "best_week"
ff.top_players(scored, season=2025, position="TE", by=____)\
''',
            'ff.top_players(scored, season=2025, position="TE", by="best_week")',
        ),
        md("""\
## Steady... or a rollercoaster? 🎢

Two players can average the SAME points per game in totally different ways:

- **Steady Eddie**: 12, 14, 13, 12, 14 — you know what you're getting
- **Boom-or-Bust Bobby**: 2, 31, 4, 28, 3 — hero one week, zero the next

The next 🪄 MAGIC chart shows **every week as a dot**. The box is where most
of their weeks land; dots way above it are boom games.\
"""),
        magic('ff.viz.boom_bust_box(scored, '
              '["Derrick Henry", "De\'Von Achane", "Jahmyr Gibbs"])'),
        try_it(
            '''\
# ⭐ TRY IT: put any three players you're curious about in the list
ff.viz.boom_bust_box(scored, ["Derrick Henry", "De'Von Achane", "Jahmyr Gibbs"])\
''',
            '''\
ff.viz.boom_bust_box(scored, ["Ja'Marr Chase", "Tyreek Hill", "Puka Nacua"])\
''',
            show_answer=False,
        ),
        md("""\
## 🪄 MAGIC: the season as a race

One more scouting tool: watch total points climb week by week, like a race.
A flat part in a player's line = injured or quiet weeks.\
"""),
        magic('ff.viz.season_race(scored, '
              '["Puka Nacua", "Ja\'Marr Chase", "Amon-Ra St. Brown"], season=2025)'),
        md("""\
## 🎉 Mission complete!

You now scout like a pro:
- ✅ Week-by-week deep dives (`ff.player_weeks`)
- ✅ Totals **and** per-game (totals can trick you!)
- ✅ Steady vs. boom-or-bust (the box chart)

**Think about it:** if two players average the same points, is the steady one
or the boom-or-bust one better for YOUR team? (Hint: are you the favorite in
your matchup, or the underdog who needs a miracle?)

**Next → Mission 3: Your League's Rulebook** — where we discover the same
players can be worth totally different amounts, depending on the rules.\
"""),
    ]


# ===========================================================================
# Mission 3 — Your League's Rulebook
# ===========================================================================

def mission_3() -> list:
    return [
        md("""\
# 📜 Mission 3: Your League's Rulebook

Here's a secret most kids in your league don't know: **the same games make
different champions under different rules.** A player who's a superstar in
one league can be just okay in another. Learn your league's rules and you're
already ahead.

⏱️ *About 25 minutes.*\
"""),
        code('''\
import ffkit as ff
from ffkit import ____

players = ff.load_players()
print("Rule presets in the lab:", ff.preset_names())\
'''),
        code('''\
rules = ff.rules("NFL Standard + IDP")   # our family league
rules.describe()\
'''),
        md("""\
## The PPR effect

The biggest rule difference between leagues is **PPR — Points Per Reception**:
does a player get points just for *catching* the ball?

- **Standard** (like NFL.com's default): a catch = 0 points
- **Full PPR** (like ESPN's default): every catch = 1 whole point

Who does that help? Receivers who catch a TON of short passes. Watch the
same 2025 season under both rules: 👇\
"""),
        code('''\
standard = ff.score(players, ff.rules("Standard + Team Defense"))
full_ppr = ff.score(players, ff.rules("ESPN Full PPR"))

print("WRs under STANDARD rules (catches worth 0):")
display(ff.top_players(standard, season=2025, position="WR", n=5))

print("Exact same season under FULL PPR (each catch = 1 point):")
display(ff.top_players(full_ppr, season=2025, position="WR", n=5))\
'''),
        md("""\
🔍 Compare the `total` columns — everyone jumped, but catch-machines jumped
the MOST. Some players even swap places. **Same games. Different rules.
Different heroes.**\
"""),
        try_it(
            '''\
# ⭐ TRY IT: invent a SILLY league where one catch is worth FIVE points!
# (Put a number in the blank. Then try other numbers. Go wild.)
crazy_rules = ff.rules("ESPN Full PPR")
crazy_rules.offense["receptions"] = ____
crazy_scored = ff.score(players, crazy_rules)
ff.top_players(crazy_scored, season=2025, n=10)\
''',
            '''\
crazy_rules = ff.rules("ESPN Full PPR")
crazy_rules.offense["receptions"] = 5
crazy_scored = ff.score(players, crazy_rules)
ff.top_players(crazy_scored, season=2025, n=10)\
''',
        ),
        md("""\
Every number in the rulebook works like that. `crazy_rules.offense`,
`.kicking`, `.idp` — they're all just dictionaries of *stat → points* that
you can change.

## Two ways to play defense 🛡️

This is the big difference between our two family leagues:

1. **IDP (Individual Defensive Players)** — our family league on NFL.com.
   You draft real defenders (linebackers, linemen, defensive backs) and they
   earn points for tackles, sacks, and interceptions.
2. **Team Defense (D/ST)** — the other style (and ESPN's default). You draft
   one whole team's defense, which earns points for sacks and turnovers and
   *loses* points when it gives up lots of scoring.\
"""),
        code('''\
idp_scored = ff.score(players, ff.rules("NFL Standard + IDP"))
print("Best LINEBACKERS to draft in an IDP league like ours:")
ff.top_players(idp_scored, season=2025, position="LB")\
'''),
        try_it(
            '''\
# ⭐ TRY IT: now find the best defensive BACKS ("DB")... or linemen ("DL")
ff.top_players(idp_scored, season=2025, position=____)\
''',
            'ff.top_players(idp_scored, season=2025, position="DB")',
        ),
        md("""\
And here's team-defense scoring — every defender's stats added together,
plus a bonus (or penalty!) for the points the team allowed:\
"""),
        try_it(
            '''\
schedules = ff.load_schedules()
dst = ff.score_team_defense(players, schedules, ff.rules("Standard + Team Defense"))

season = dst[dst["season"] == 2025]      # ⭐ TRY IT: peek at another season!
season.groupby("team")["fantasy_points"].sum().sort_values(ascending=False).head(10)\
''',
            '''\
schedules = ff.load_schedules()
dst = ff.score_team_defense(players, schedules, ff.rules("Standard + Team Defense"))

season = dst[dst["season"] == 2023]
season.groupby("team")["fantasy_points"].sum().sort_values(ascending=False).head(10)\
''',
            show_answer=False,
        ),
        md("""\
## 🎛️ Dial in YOUR league

Now make the lab match **your** league exactly. Ask a grown-up to open your
league's settings page and copy the numbers into this panel:

- **NFL.com:** League → Settings → Scoring
- **ESPN:** League → League Settings → Scoring

(If you skip this, the lab keeps using the family preset — that's fine too.)\
"""),
        code('ff.widgets.scoring_picker()'),
        code('''\
my_rules = ff.widgets.current_rules()
print(f"Locked in: {my_rules.name} — {my_rules.num_teams} teams ✅")\
'''),
        md("""\
## 🎉 Mission complete!

- ✅ You know what PPR is (and why catch-machines love it)
- ✅ You changed a league's rules with one line of code
- ✅ You've seen both defense styles: IDP and Team D/ST
- ✅ The lab now speaks YOUR league's language

**Next → Mission 4: DRAFT DAY.** Time to build the machine that ranks every
player for your draft. This is the big one. 🚀\
"""),
    ]


# ===========================================================================
# Mission 4 — Draft Day
# ===========================================================================

def mission_4() -> list:
    return [
        md("""\
# 🚀 Mission 4: Draft Day!

This is the mission everything else was building toward. Today you build a
**ranking machine**: it guesses how every player will do THIS season, works
out who's truly valuable, and prints your own cheat sheet for draft day.

⏱️ *About 30 minutes — worth every second.*\
"""),
        code('''\
import ffkit as ff
from ffkit import ____

players = ff.load_players()
schedules = ff.load_schedules()

rules = ff.rules("NFL Standard + IDP")   # ⭐ or any preset from Mission 3
pool = ff.build_player_pool(players, schedules, rules)
print(f"Draft pool ready: {pool['player_id'].nunique():,} draftable players 🏈")\
'''),
        md("""\
## 🔮 Step 1: The crystal ball (projections)

Nobody knows the future — but the past gives clues. Say Bijan averaged 20
points per game last season and 15 the season before. What will he do this
year? **It depends on how much you trust each clue.** That's YOUR call, with
three knobs:

| knob | 0 means... | 1 means... |
|---|---|---|
| `past_matters` | only last season counts | every season counts equally |
| `durability` | assume everyone plays all 17 games | expect missed games to happen again |
| `steady_bonus` | *(0 = just use averages)* | +1 loves steady players, **-1** loves boom-or-bust |

There is no "correct" setting — this is where YOUR football brain comes in.\
"""),
        code('''\
projections = ff.make_projections(
    pool,
    past_matters=0.5,   # half-trust older seasons
    durability=0.5,     # worry a medium amount about missed games
    steady_bonus=0.0,   # no taste adjustment... yet
)
projections.sort_values("proj_points", ascending=False).head(10)\
'''),
        md("""\
## 🧠 Step 2: The draft secret (value over replacement)

Look at your projections: the top QB probably out-scores the top RB. So why
do smart drafters take running backs first?!

**Because value = how much better a player is than the FREE replacement.**

Say every team already started a QB and the best *undrafted* QB would still
score 280 — but the best undrafted RB only scores 150. Then a 380-point QB is
really worth 380 − 280 = **100**, while a 280-point RB is worth 280 − 150 =
**130**. The RB wins, even with fewer points!

That difference is called **VOR** (Value Over Replacement) — the `value`
column below. It's the single smartest number on your whole cheat sheet:\
"""),
        code('''\
board = ff.big_board(projections, rules)
board.head(15)\
'''),
        md('## 🪄 MAGIC: your Big Board, as a chart'),
        magic('ff.viz.big_board_chart(board, top=25)'),
        try_it(
            '''\
# ⭐ TRY IT: what happens when ONLY last season matters?
# Set past_matters to 0.0 and see who jumps up or crashes down.
# Then try 1.0 (all seasons equal). Watch the board reshuffle!
test_projections = ff.make_projections(pool, past_matters=____)
ff.big_board(test_projections, rules).head(10)\
''',
            '''\
test_projections = ff.make_projections(pool, past_matters=0.0)
ff.big_board(test_projections, rules).head(10)\
''',
        ),
        md("""\
## 🪄 MAGIC: steady stars vs. boom-or-bust

Every dot is a player. **Right = scores more.** **Higher = wilder weeks.**
So the bottom-right corner is where the steady superstars live. Hover to see
who's who!\
"""),
        magic('ff.viz.value_scatter(board)'),
        md("""\
## 🎛️ The Draft Machine

All three knobs as sliders. Move one — the whole board re-ranks before your
eyes. Argue with your siblings about the right settings. That's the point. 😄\
"""),
        code('ff.widgets.draft_dashboard(pool, rules)'),
        md("""\
## 🧑‍⚖️ Step 3: You vs. the experts

Real fantasy experts publish draft rankings. The lab downloaded today's
expert consensus — let's see where your math **disagrees** with them:\
"""),
        code('''\
experts = ff.load_rankings()
compared = ff.compare_with_experts(board, experts)

sleepers = compared.dropna(subset=["we_disagree_by"]).nlargest(6, "we_disagree_by")
print("😴 SLEEPERS — players YOUR math likes way more than the experts do:")
sleepers[["player_display_name", "pos", "pos_rank", "expert_rank", "we_disagree_by"]]\
'''),
        magic('ff.viz.experts_scatter(compared)'),
        md("""\
**Who should you believe?** Honestly — both. Your math only knows the past.
Experts also know the *news*: injuries healing, trades, coaching changes, and
**rookies** (first-year players have no NFL stats, so your board can't see
them at all — check the expert list for those!). The best drafters use math
AND news.\
"""),
        md('## 📄 Step 4: Print your cheat sheet'),
        code('''\
cheat_sheet = board.head(150).drop(columns=["headshot_url", "player_id"])
cheat_sheet.to_csv("my_draft_cheat_sheet.csv", index=False)
print("Saved my_draft_cheat_sheet.csv — open it, print it, win your draft! 🏆")\
'''),
        try_it(
            '''\
# ⭐ FINAL CHALLENGE: build a Big Board for a totally different league style!
# Presets: 'NFL Standard + IDP', 'ESPN Full PPR', 'Half PPR',
#          'Standard + Team Defense'
other_rules = ff.rules(____)
other_pool = ff.build_player_pool(players, schedules, other_rules)
other_board = ff.big_board(ff.make_projections(other_pool), other_rules)
other_board.head(15)\
''',
            '''\
other_rules = ff.rules("ESPN Full PPR")
other_pool = ff.build_player_pool(players, schedules, other_rules)
other_board = ff.big_board(ff.make_projections(other_pool), other_rules)
other_board.head(15)\
''',
        ),
        md("""\
Compare that board to your league's board. Different rules → different top
picks. **That's why you never copy a random internet ranking** — it might be
for a league with different rules than yours!

## 🎉 Mission complete — you built a draft machine!

Quick draft-day wisdom from the data:
- 💎 Draft **value**, not just points (that's your VOR column)
- 🏃 The drop-off from great RBs to okay RBs is a cliff — mind the tiers
- 🦵 Never draft a kicker early (check where kickers sit on your board 😅)
- 📰 Check expert lists for rookies your math can't see

**Next → Mission 5: Set Your Lineup** — because after the draft, you have to
win every single week.\
"""),
    ]


# ===========================================================================
# Mission 5 — Set Your Lineup
# ===========================================================================

def mission_5() -> list:
    return [
        md("""\
# 📋 Mission 5: Set Your Lineup

The draft is over — now you play a new game **every single week**: who
starts, and who rides the bench? Bad lineup calls lose more matchups than
bad drafts do. Let's make sure that's not you.

⏱️ *About 25 minutes.*

> 🏋️ **Practice mode:** until the 2026 season kicks off, we practice on
> 2025's real weeks. Once games start, one command switches the lab to live
> data — instructions at the bottom!\
"""),
        code('''\
import ffkit as ff
from ffkit import ____

players = ff.load_players()
schedules = ff.load_schedules()
rules = ff.rules("NFL Standard + IDP")
pool = ff.build_player_pool(players, schedules, rules)
print("Lineup lab ready! 📋")\
'''),
        md("""\
## Your squad

Type your team's players into the list below (after your real draft, put
YOUR team here — the lab is typo-friendly and will suggest names if you're
close). Then give your team a name and save it:\
"""),
        try_it(
            '''\
my_players = [
    "Josh Allen",                                     # QB
    "Bijan Robinson", "Jahmyr Gibbs", "De'Von Achane",  # RBs
    "Puka Nacua", "Jaxon Smith-Njigba", "Nico Collins", # WRs
    "Trey McBride",                                   # TE
    "Jason Myers",                                    # K
    "Myles Garrett", "Maxx Crosby",                   # DL
    "Jack Campbell", "Jordyn Brooks",                 # LB
    "Kerby Joseph", "Brian Branch",                   # DB
]
ff.save_my_team(my_players, owner="The Turbo Turtles")  # ⭐ your team name!\
''',
            '''\
my_players = [
    "Josh Allen",
    "Bijan Robinson", "Jahmyr Gibbs", "De'Von Achane",
    "Puka Nacua", "Jaxon Smith-Njigba", "Nico Collins",
    "Trey McBride",
    "Jason Myers",
    "Myles Garrett", "Maxx Crosby",
    "Jack Campbell", "Jordyn Brooks",
    "Kerby Joseph", "Brian Branch",
]
ff.save_my_team(my_players, owner="The Data Dragons")\
''',
            show_answer=False,
        ),
        code('''\
mine = ff.find_players(ff.load_my_team(), pool)
mine   # your roster, matched to the real players in the data\
'''),
        md("""\
## Matchups: the weekly secret weapon 🍖

Not all opponents are equal! Some defenses are brick walls; others give up
points like a broken vending machine. The lab measures **how many fantasy
points each defense allows to each position**:\
"""),
        try_it(
            '''\
allowed = ff.points_allowed_to_position(pool, season=2025)
matchups = allowed[allowed["pos"] == "RB"]     # ⭐ TRY IT: try "WR" or "QB"!

print("🍖 JUICIEST defenses to face (they leak the most RB points):")
display(matchups.sort_values("allowed_per_game", ascending=False).head(5))

print("🧱 BRICK WALLS (good luck...):")
display(matchups.sort_values("allowed_per_game").head(5))\
''',
            '''\
allowed = ff.points_allowed_to_position(pool, season=2025)
matchups = allowed[allowed["pos"] == "WR"]

print("🍖 JUICIEST defenses to face (they leak the most WR points):")
display(matchups.sort_values("allowed_per_game", ascending=False).head(5))

print("🧱 BRICK WALLS (good luck...):")
display(matchups.sort_values("allowed_per_game").head(5))\
''',
            show_answer=False,
        ),
        md("""\
## Rate my players 📊

Now the lab rates YOUR whole roster for one week, combining:
- **Form** — last 3 games (60%) + whole season (40%)
- **Matchup** — a boost for juicy opponents, a penalty for brick walls
- **Byes** — a week off = 0 points, flagged with 😴

`matchup_score` reads like a video game: **10 = dream matchup, 1 = brick
wall.**\
"""),
        code('''\
week = 10    # practice on week 10 of 2025
rated = ff.rate_my_players(mine, pool, schedules, season=2025, week=week)
rated\
'''),
        md("""\
## The lab picks your lineup

...and now it fills every slot in your lineup with your best option, and
benches the rest:\
"""),
        code('''\
lineup = ff.pick_lineup(rated, rules)
lineup\
'''),
        magic('ff.viz.lineup_chart(rated)'),
        try_it(
            '''\
# ⭐ TRY IT: fast-forward to a different week — try week 8, or 14.
# Watch for BYE 😴 flags: would your lineup survive?
rated = ff.rate_my_players(mine, pool, schedules, season=2025, week=____)
ff.pick_lineup(rated, rules)\
''',
            '''\
rated = ff.rate_my_players(mine, pool, schedules, season=2025, week=8)
ff.pick_lineup(rated, rules)\
''',
        ),
        md("""\
> ⚠️ The lab's pick is **advice, not orders**. It can't know that a player is
> "questionable" for Sunday or that snow is coming. Check the news before you
> lock in — you're the coach. 🧢

## 🔴 Going LIVE for the 2026 season

Once the season starts, do this each week (internet needed):

1. Run the refresh cell below (remove the `#` first)
2. Change `season=2025` to `season=2026` in the cells above
3. Set `week=` to the current NFL week
4. Rate, pick, and set your lineup on your league's website — BEFORE the
   first game kicks off (usually Thursday night!)\
"""),
        code('''\
# Remove the # below and run this once a week during the season:
# ff.refresh_all()\
'''),
        md("""\
## 🏆 FINAL MISSION COMPLETE — you finished the Lab!

You can now:
- ✅ Load and explore five seasons of real NFL data (Mission 1)
- ✅ Scout players like a pro — form, totals, boom-or-bust (Mission 2)
- ✅ Speak any league's scoring language, IDP or D/ST (Mission 3)
- ✅ Build a projection machine and a Big Board with VOR (Mission 4)
- ✅ Set a smart lineup with matchups and bye-week radar (Mission 5)

**Your weekly routine in one cell:** refresh → rate → pick → set it on the
website. Total time: about 2 minutes to look like a genius. 😎

Go win the league. 🏈🏆\
"""),
    ]


# ===========================================================================


MISSIONS = {
    "01_rookie_camp.ipynb": mission_1,
    "02_scouting_report.ipynb": mission_2,
    "03_league_rules.ipynb": mission_3,
    "04_draft_day.ipynb": mission_4,
    "05_set_your_lineup.ipynb": mission_5,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solutions", action="store_true",
                        help="fill every TRY IT blank with its answer")
    parser.add_argument("-o", "--out", default=None,
                        help="output directory (default: notebooks/)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    out_dir = Path(args.out) if args.out else root / "notebooks"
    label = "SOLUTION" if args.solutions else "student"
    print(f"Building {label} notebooks → {out_dir}")
    for filename, mission in MISSIONS.items():
        build(mission(), out_dir / filename, solutions=args.solutions)
    print("Done! 🎉")


if __name__ == "__main__":
    main()
