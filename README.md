# 🏈 The Fantasy Football Lab

Five interactive Jupyter notebook "missions" that teach kids (ages ~10–12)
real data analysis through fantasy football — with real NFL data, your own
league's scoring rules, a draft-day Big Board, and a weekly lineup helper.

## What's inside

| Mission | What the kids do | ~Time |
|---|---|---|
| **1 · Rookie Camp** | Run their first code, meet 5 seasons of real NFL data, build a leaderboard | 20 min |
| **2 · The Scouting Report** | Scout players: totals vs per-game, steady vs boom-or-bust, player cards | 25 min |
| **3 · Your League's Rulebook** | PPR, IDP vs Team D/ST — and dial in *your* league's exact scoring | 25 min |
| **4 · Draft Day** | Build projections with sliders, rank everyone by value (VOR), print a cheat sheet, argue with the experts | 30 min |
| **5 · Set Your Lineup** | Weekly start/sit: recent form + matchups + bye-week radar | 25 min |

Inside the notebooks, cells are marked:

- ⭐ **TRY IT** — fill in a blank or tweak a number. Unfilled blanks never
  crash — they print a friendly hint instead.
- 🔑 **ANSWER** — the solution, commented out right below.
- 🪄 **MAGIC** — a fancy chart. Just run it.

## Setup (parent, one time, ~5 minutes)

Three steps: **get the lab → install `uv` → install the packages.**
After that, everything works offline — the NFL data (~4 MB) already ships
inside the lab. No accounts, no downloads.

> **How to open a terminal** (you'll need one for steps 2 and 3):
>
> - **Windows**: press the Windows key, type `powershell`, press Enter.
> - **Mac**: press Cmd+Space, type `terminal`, press Enter.
> - **Ubuntu Linux**: press Ctrl+Alt+T.

### Step 1 — Get the lab

Pick either way:

- **With git:**

  ```bash
  git clone https://github.com/j-shelly/fantasy-football-lab.git
  ```

  Never used git? It's a free tool that downloads the lab *and* makes
  getting updates easy later. GitHub's official
  [Set up Git guide](https://docs.github.com/en/get-started/git-basics/set-up-git)
  walks you through installing it — then come back and run the command
  above.

- **Without git:** on the GitHub page, click the green **Code** button →
  **Download ZIP**, then unzip it somewhere easy to find (like the Desktop).

### Step 2 — Install uv

[uv](https://docs.astral.sh/uv/) is one small tool that handles everything
else — it even installs Python for you.

**Windows** — paste into PowerShell and press Enter:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Mac and Ubuntu Linux** — same command for both. Paste into the terminal
and press Enter:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

*(Ubuntu only: if it says `curl: command not found`, run
`sudo apt install curl` first, then try again.)*

Then **close the terminal and open a new one**, so it knows about `uv`.

### Step 3 — Install the lab's packages

In the new terminal, go into the lab folder and run one command:

```bash
cd fantasy-football-lab
uv sync
```

Two tips:

- If you used the ZIP, the folder may be called `fantasy-football-lab-main`.
- Not sure how `cd` works? Type `cd ` (with a space), **drag the lab folder
  onto the terminal window**, and press Enter.

Done! You never have to do this part again.

## Starting the lab (kids can do this part)

- **Windows**: double-click `start_lab.bat`
- **Mac**: double-click `start_lab_mac.command`. The very first time, macOS
  will complain — right-click the file → **Open** → **Open** to get past it.
- **Ubuntu Linux (or WSL)**: double-clicking won't work here. Open a
  terminal in the lab folder (in the Files app: right-click →
  **Open in Terminal**), then type:

  ```bash
  ./start_lab.sh
  ```

  If it says "Permission denied", type `bash start_lab.sh` instead.

Your web browser opens JupyterLab showing the missions. Double-click a
mission, then run the cells from top to bottom by pressing **Shift+Enter**.

If a notebook gets weird or stuck: menu → **Kernel → Restart Kernel and Run
All Cells…** fixes almost everything.

## Fresh stats during the 2026 season

nflverse (our data source) updates every night during the season. Once a
week, run this in a terminal from the lab folder:

```bash
uv run python -c "import ffkit; ffkit.refresh_all()"
```

(Or run the refresh cell at the bottom of Mission 5 — same thing.) Then use
`season=2026` and the current week number in Mission 5.

## Getting lab updates with git (for terminal-curious kids 🧑‍💻)

The command above refreshes *stats*. If the lab itself gets new missions or
fixes, `git pull` downloads those. (No git on your computer yet? GitHub's
[Set up Git guide](https://docs.github.com/en/get-started/git-basics/set-up-git)
shows how to install it.)

**First, protect your progress.** Once you've worked through a mission, git
sees your notebook as "changed" — and updating resets it. So in JupyterLab,
right-click any notebook you want to keep → **Duplicate**. The copy (like
`04_draft_day-Copy1.ipynb`) is yours forever; git won't touch it.

Then, in a terminal from the lab folder:

```bash
git status      # see what you changed (just looking — changes nothing)
git restore .   # reset the lab to factory settings (your copies are safe!)
git pull        # download the newest version of the lab
uv sync         # in case the update added new packages
```

Heads-up: `git restore .` also rewinds the stats in `data/` to the ones that
shipped with the lab. Mid-season, just run the refresh command again.

(Got the lab as a ZIP instead? Download a fresh ZIP and copy your duplicated
notebooks over.)

## League scoring

The lab works with any fantasy platform. Presets included:

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

The notebooks are generated from `scripts/build_notebooks.py` — edit that
file to add your own missions or change wording, then rebuild.

## How it's built

- **Data**: free [nflverse](https://nflverse.nflverse.com/) via `nflreadpy` —
  weekly player stats 2021–2025 (offense *and* individual defenders),
  schedules, team colors, and FantasyPros expert consensus draft rankings.
  Cached as parquet in `data/` (included in the repo) so everything works
  offline; `uv run python scripts/warm_cache.py` re-downloads it from scratch
  if needed.
- **`ffkit/`**: the toolkit the notebooks import — scoring engine
  (`scoring.py`), projections + value-over-replacement (`draft.py`),
  start/sit (`lineup.py`), plotly charts (`viz.py`), sliders (`widgets.py`).
- The scoring engine was validated against nflverse's own precomputed fantasy
  points (96% of players match to the penny; the rest differ only on
  special-teams fumble edge cases where platforms differ anyway).

## Troubleshooting

- **Charts don't show** → run the cell again, or restart the kernel; make
  sure you started the lab with the launcher for your computer (see
  [Starting the lab](#starting-the-lab-kids-can-do-this-part)).
- **"Couldn't find player X"** → the lab suggests close spellings; rookies
  with no NFL games yet won't exist in past-season data (Mission 4 explains
  this).
- **Data feels stale** → run the refresh command above (needs internet).
