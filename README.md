# 🏈 The Fantasy Football Lab

Five interactive Jupyter notebook "missions" that teach kids (ages ~10–12) real
data analysis through fantasy football — with real NFL data, their own league's
scoring rules, a draft-day Big Board, and a weekly lineup helper.

## What's inside

| Mission | What the kids do | ~Time |
|---|---|---|
| **1 · Rookie Camp** | Run their first code, meet 5 seasons of real NFL data, build a leaderboard | 20 min |
| **2 · The Scouting Report** | Scout players: totals vs per-game, steady vs boom-or-bust, player cards | 25 min |
| **3 · Your League's Rulebook** | PPR, IDP vs Team D/ST — and dial in *your* league's exact scoring | 25 min |
| **4 · Draft Day** | Build projections with sliders, rank everyone by value (VOR), print a cheat sheet, argue with the experts | 30 min |
| **5 · Set Your Lineup** | Weekly start/sit: recent form + matchups + bye-week radar | 25 min |

Cell markers the kids will see: ⭐ **TRY IT** (fill in a blank or tweak a value —
unfilled blanks never crash, they print a friendly nudge), 🔑 **ANSWER**
(commented-out solution right below), 🪄 **MAGIC** (fancy visualization — "just
run it").

## Setup on a new computer (parent, one time, ~5 min)

The NFL data ships with the repo (`data/`, ~4 MB), so after these steps
everything works offline — no downloads needed.

**1. Get the lab.** Either clone it:

```bash
git clone https://github.com/j-shelly/fantasy-football-lab.git
```

…or on GitHub click the green **Code** button → **Download ZIP**, then unzip
it somewhere easy to find (like the Desktop).

**2. Install [uv](https://docs.astral.sh/uv/)** (it installs Python too — no
separate Python setup):

```powershell
# Windows (paste into PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# Mac / Linux (paste into Terminal)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then close and reopen the terminal so `uv` is found.

**3. Install the lab's packages.** In a terminal, from the lab folder:

```bash
uv sync
```

## Launching the lab (kids can do this part)

- **Windows**: double-click `start_lab.bat`
- **Mac**: double-click `start_lab_mac.command` (first time: right-click →
  **Open** → **Open**, to get past the security prompt)
- **Linux / WSL**: `./start_lab.sh`

Your browser opens JupyterLab in the `notebooks/` folder. Kids double-click a
mission, then run cells top-to-bottom with **Shift+Enter**. If a notebook gets
into a weird state: `Kernel → Restart Kernel and Run All Cells…`.

## During the 2026 season

nflverse data updates nightly during the season. Each week:

```bash
uv run python -c "import ffkit; ffkit.refresh_all()"
```

(or run the refresh cell at the bottom of Mission 5), then use `season=2026`
and the current week number in Mission 5.

## Getting lab updates with git (for terminal-curious kids 🧑‍💻)

Stats come from the refresh cell above — but if the lab itself gets new
missions or fixes, `git pull` downloads them. In a terminal, from the lab
folder:

```bash
git status
```

That shows what *you* have changed — and once you've worked through a mission,
your notebook counts as a change. **To keep your progress**, duplicate the
notebooks you care about first (in JupyterLab: right-click the file →
**Duplicate** — the copy, like `04_draft_day-Copy1.ipynb`, is yours and git
won't touch it). Then:

```bash
git restore .   # reset the lab to factory settings (your copies are safe!)
git pull        # download the newest version of the lab
uv sync         # in case the update added new packages
```

Heads up: `git restore .` also rewinds `data/` to the stats that shipped with
the lab, so run the refresh cell again if you're mid-season.

(Downloaded as a ZIP instead? Grab a fresh ZIP and copy your duplicated
notebooks over.)

## League scoring

The lab is platform-agnostic. Presets included:

- **NFL Standard + IDP** — the family league (individual defensive players)
- **ESPN Full PPR** — ESPN's default (1 pt/catch, team D/ST)
- **Half PPR**
- **Standard + Team Defense** — non-PPR with one D/ST slot

Mission 3's 🎛️ picker (or plain code) tweaks any value — points per catch,
per sack, roster slots, league size — to match your league's settings screen
exactly. Rankings, boards, and lineups all follow whatever rules are chosen.

## Parent tools

```bash
# Restore pristine notebooks (wipes the kids' edits in notebooks/!)
uv run python scripts/build_notebooks.py

# Build fully-solved copies for yourself (great for helping when they're stuck)
uv run python scripts/build_notebooks.py --solutions -o solutions/
```

The notebooks are generated from `scripts/build_notebooks.py` — edit that file
to add your own missions or change wording, then rebuild.

## How it's built

- **Data**: free [nflverse](https://nflverse.nflverse.com/) via `nflreadpy` —
  weekly player stats 2021–2025 (offense *and* individual defenders), schedules,
  team colors, and FantasyPros expert consensus draft rankings. Cached as
  parquet in `data/` (included in the repo) so everything works offline;
  `uv run python scripts/warm_cache.py` re-downloads it from scratch if needed.
- **`ffkit/`**: the toolkit the notebooks import — scoring engine
  (`scoring.py`), projections + value-over-replacement (`draft.py`), start/sit
  (`lineup.py`), plotly charts (`viz.py`), sliders (`widgets.py`).
- The scoring engine was validated against nflverse's own precomputed fantasy
  points (96% of players match to the penny; the rest differ only on
  special-teams fumble edge cases where platforms differ anyway).

## Troubleshooting

- **Charts don't show** → run the cell again, or restart the kernel; make sure
  you launched via `./start_lab.sh` (it uses the project's environment).
- **"Couldn't find player X"** → the lab suggests close spellings; rookies with
  no NFL games yet won't exist in past-season data (Mission 4 explains this).
- **Data feels stale** → run the refresh command above (needs internet).
