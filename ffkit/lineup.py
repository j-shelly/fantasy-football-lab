"""Weekly lineup helper: who should you start this week?

The recipe, in kid terms:
  FORM     — how good has this player been lately (last 3 games) and all season?
  MATCHUP  — is this week's opponent easy or tough against their position?
  EXPECTED — form, nudged up for easy matchups and down for tough ones.
Players on a bye week score zero, so the helper flags them loudly.
"""

from __future__ import annotations

import difflib
import json
from pathlib import Path

import pandas as pd

from .data import DATA_DIR
from .draft import SLOT_ELIGIBILITY
from .scoring import ScoringRules

MY_TEAM_FILE = DATA_DIR / "my_team.json"


# ---------------------------------------------------------------------------
# Saving your roster
# ---------------------------------------------------------------------------


def save_my_team(names: list[str], owner: str = "My Team") -> None:
    """Remember your roster so you don't have to retype it every week."""
    MY_TEAM_FILE.parent.mkdir(exist_ok=True)
    MY_TEAM_FILE.write_text(json.dumps({"owner": owner, "players": names}, indent=2))
    print(f"💾 Saved {len(names)} players for '{owner}'!")


def load_my_team() -> list[str]:
    if not MY_TEAM_FILE.exists():
        print("🤔 No saved team yet — use save_my_team([...]) first!")
        return []
    saved = json.loads(MY_TEAM_FILE.read_text())
    print(f"📋 Loaded '{saved['owner']}': {len(saved['players'])} players")
    return saved["players"]


def find_players(names: list[str], pool: pd.DataFrame) -> pd.DataFrame:
    """Match typed names to real players (typo-friendly)."""
    known = pool[["player_id", "player_display_name", "pos"]].drop_duplicates(
        "player_id"
    )
    lookup = {n.lower(): i for n, i in
              zip(known["player_display_name"], known["player_id"])}
    rows = []
    for name in names:
        key = name.lower().strip()
        if key in lookup:
            rows.append(lookup[key])
            continue
        close = difflib.get_close_matches(key, lookup.keys(), n=3, cutoff=0.6)
        if len(close) == 1:
            rows.append(lookup[close[0]])
        elif close:
            pretty = "', '".join(
                known.set_index("player_id").loc[lookup[c], "player_display_name"]
                for c in close
            )
            print(f"🤔 Couldn't find '{name}'. Did you mean: '{pretty}'?")
        else:
            print(f"🤔 Couldn't find '{name}' — check the spelling?")
    return known[known["player_id"].isin(rows)].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Matchups
# ---------------------------------------------------------------------------


def bye_teams(schedules: pd.DataFrame, season: int, week: int) -> set[str]:
    games = schedules[
        (schedules["season"] == season)
        & (schedules["week"] == week)
        & (schedules["game_type"] == "REG")
    ]
    playing = set(games["home_team"]) | set(games["away_team"])
    all_teams = set(schedules[schedules["season"] == season]["home_team"]) | set(
        schedules[schedules["season"] == season]["away_team"]
    )
    return all_teams - playing


def week_opponents(schedules: pd.DataFrame, season: int, week: int) -> dict[str, str]:
    games = schedules[
        (schedules["season"] == season)
        & (schedules["week"] == week)
        & (schedules["game_type"] == "REG")
    ]
    opp: dict[str, str] = {}
    for _, g in games.iterrows():
        opp[g["home_team"]] = g["away_team"]
        opp[g["away_team"]] = g["home_team"]
    return opp


def points_allowed_to_position(
    pool: pd.DataFrame, season: int, through_week: int | None = None
) -> pd.DataFrame:
    """How many fantasy points each defense gives up to each position, per game.

    A high number = a juicy matchup for your player!
    """
    df = pool[(pool["season"] == season) & pool["opponent_team"].notna()]
    if through_week:
        df = df[df["week"] < through_week]
    per_game = (
        df.groupby(["opponent_team", "pos", "week"])["fantasy_points"]
        .sum()
        .groupby(["opponent_team", "pos"])
        .mean()
        .rename("allowed_per_game")
        .reset_index()
        .rename(columns={"opponent_team": "defense"})
    )
    per_game["matchup_score"] = (
        per_game.groupby("pos")["allowed_per_game"]
        .rank(pct=True)
        .mul(10)
        .round(1)
    )  # 10 = easiest defense to score on, 1 = toughest
    return per_game


# ---------------------------------------------------------------------------
# The start/sit engine
# ---------------------------------------------------------------------------


def rate_my_players(
    my_players: pd.DataFrame,
    pool: pd.DataFrame,
    schedules: pd.DataFrame,
    season: int,
    week: int,
) -> pd.DataFrame:
    """Rate each of your players for one week: form + matchup = expected."""
    from .training import is_blank, nudge

    if is_blank(season):
        season = int(pool["season"].max())
        nudge("which season?", f"Using {season}.")
    if is_blank(week):
        nudge("which week?", "Using week 10. Try any week from 2 to 18!")
        week = 10

    season_pool = pool[pool["season"] == season]
    before = season_pool[season_pool["week"] < week]
    opponents = week_opponents(schedules, season, week)
    byes = bye_teams(schedules, season, week)
    allowed = points_allowed_to_position(pool, season, through_week=week)

    league_avg = (
        allowed.groupby("pos")["allowed_per_game"].mean().to_dict()
    )

    rows = []
    for _, p in my_players.iterrows():
        history = before[before["player_id"] == p["player_id"]].sort_values("week")
        team_rows = season_pool[season_pool["player_id"] == p["player_id"]]
        team = team_rows["team"].iloc[-1] if len(team_rows) else None
        last3 = history["fantasy_points"].tail(3).mean() if len(history) else 0.0
        season_avg = history["fantasy_points"].mean() if len(history) else 0.0
        opp = opponents.get(team)
        on_bye = team in byes

        multiplier = 1.0
        matchup_score = None
        if opp is not None:
            row = allowed[(allowed["defense"] == opp) & (allowed["pos"] == p["pos"])]
            if len(row) and league_avg.get(p["pos"]):
                ratio = row["allowed_per_game"].iloc[0] / league_avg[p["pos"]]
                multiplier = float(pd.Series(ratio).clip(0.75, 1.25).iloc[0])
                matchup_score = row["matchup_score"].iloc[0]

        form = 0.6 * last3 + 0.4 * season_avg
        expected = 0.0 if on_bye else round(form * multiplier, 1)
        rows.append({
            "player": p["player_display_name"],
            "pos": p["pos"],
            "team": team,
            "opponent": "BYE 😴" if on_bye else (opp or "?"),
            "last3_avg": round(last3, 1),
            "season_avg": round(season_avg, 1),
            "matchup_score": matchup_score,  # 10 = easiest opponent
            "expected": expected,
        })
    return (
        pd.DataFrame(rows)
        .sort_values("expected", ascending=False)
        .reset_index(drop=True)
    )


def pick_lineup(rated: pd.DataFrame, rules: ScoringRules) -> pd.DataFrame:
    """Fill your starting lineup with the best available player per slot."""
    available = rated.copy()
    picks = []
    # Fill single-position slots first, FLEX last, so the flex gets leftovers
    slots = sorted(
        rules.roster.items(),
        key=lambda kv: len(SLOT_ELIGIBILITY.get(kv[0], [])),
    )
    for slot, count in slots:
        eligible_pos = SLOT_ELIGIBILITY.get(slot, [])
        for _ in range(count):
            options = available[available["pos"].isin(eligible_pos)]
            if len(options) == 0:
                picks.append({"slot": slot, "player": "(empty — draft one!)"})
                continue
            best = options.iloc[0]
            picks.append({"slot": slot, **best.to_dict()})
            available = available.drop(best.name)
    lineup = pd.DataFrame(picks)
    bench = available.copy()
    bench.insert(0, "slot", "BENCH")
    return pd.concat([lineup, bench], ignore_index=True)
