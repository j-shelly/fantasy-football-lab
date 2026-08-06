"""🏈 The Fantasy Football Lab toolkit.

Everything the notebooks need, in one friendly import:

    import ffkit as ff

    players = ff.load_players()
    rules   = ff.rules("NFL Standard + IDP")
    scored  = ff.score(players, rules)
    ff.top_players(scored, season=2025, position="RB")
"""

from __future__ import annotations

import pandas as pd

from .data import (  # noqa: F401
    SEASONS,
    cache_ready,
    load_rankings,
    load_schedules,
    load_teams,
    load_weekly,
    refresh_all,
)
from .scoring import (  # noqa: F401
    ScoringRules,
    get_rules,
    preset_names,
    score_players,
    score_team_defense,
)
from .draft import (  # noqa: F401
    big_board,
    build_player_pool,
    compare_with_experts,
    make_projections,
    season_stats,
)
from .lineup import (  # noqa: F401
    find_players,
    load_my_team,
    pick_lineup,
    points_allowed_to_position,
    rate_my_players,
    save_my_team,
)
from .training import ____, Blank, is_blank, nudge  # noqa: F401
from . import viz, widgets  # noqa: F401

score = score_players  # friendlier alias used in the notebooks


def load_players() -> pd.DataFrame:
    """Every player's real weekly stats, 2021-2025 (kid-sized columns)."""
    if not cache_ready():
        print("📡 First time here — downloading NFL data (about a minute)...")
    df = load_weekly()
    return df


def rules(preset_name) -> ScoringRules:
    """Get a league scoring preset by name (see ff.preset_names())."""
    if is_blank(preset_name):
        nudge("which league preset?",
              "Using 'NFL Standard + IDP' for now — try ff.preset_names()")
        preset_name = "NFL Standard + IDP"
    return get_rules(preset_name)


def _pos_column(df: pd.DataFrame) -> pd.Series:
    if "pos" in df.columns:
        return df["pos"]
    if "position_group" in df.columns:
        idp = df["position_group"].isin(["DL", "LB", "DB"])
        return df["position"].where(~idp, df["position_group"])
    return df["position"]


def top_players(
    scored: pd.DataFrame,
    season=None,
    position=None,
    n: int = 10,
    by: str = "total",
) -> pd.DataFrame:
    """The leaderboard: best fantasy players by your league's scoring.

    by can be "total" (season points), "per_game", or "best_week".
    """
    if "fantasy_points" not in scored.columns:
        print("🤔 Score the players first: scored = ff.score(players, rules)")
        return pd.DataFrame()
    df = scored.copy()
    df["pos"] = _pos_column(df)

    if is_blank(season):
        nudge("which season?", "Showing 2025. Try season=2024!")
        season = 2025
    if is_blank(position):
        nudge("which position?",
              'Showing every position. Try position="RB", "WR", "QB", "TE", '
              '"K", "DL", "LB", or "DB"')
        position = None
    if is_blank(n):
        nudge("how many players?", "Showing 10.")
        n = 10
    if is_blank(by):
        nudge("sorted by what?", 'Using "total". Try "per_game" or "best_week"')
        by = "total"

    if season is not None:
        df = df[df["season"] == season]
    if position is not None:
        want = str(position).upper()
        df = df[df["pos"] == want]
        if len(df) == 0:
            print(f"🤔 No players at position '{position}'. "
                  'Try "QB", "RB", "WR", "TE", "K", "DL", "LB", or "DB".')
            return pd.DataFrame()

    table = (
        df.groupby(["player_display_name", "pos"])
        .agg(
            team=("team", "last"),
            games=("fantasy_points", "count"),
            total=("fantasy_points", "sum"),
            per_game=("fantasy_points", "mean"),
            best_week=("fantasy_points", "max"),
        )
        .reset_index()
        .rename(columns={"player_display_name": "player"})
    )
    if by not in ("total", "per_game", "best_week"):
        print(f'🤔 by="{by}" isn\'t a choice — using "total". '
              '(Choices: "total", "per_game", "best_week")')
        by = "total"
    table = table.sort_values(by, ascending=False).head(n).reset_index(drop=True)
    table.insert(0, "rank", range(1, len(table) + 1))
    return table.round({"total": 1, "per_game": 2, "best_week": 1})


def player_weeks(scored: pd.DataFrame, name, season=None) -> pd.DataFrame:
    """One player's week-by-week scores."""
    if is_blank(name):
        nudge("which player?", 'Try name="Bijan Robinson"')
        return pd.DataFrame()
    df = scored.copy()
    sub = df[df["player_display_name"].str.lower() == str(name).lower()]
    if len(sub) == 0:
        close = df[df["player_display_name"].str.lower().str.contains(
            str(name).lower().split()[-1], na=False)]
        hint = ""
        if len(close):
            names = "', '".join(close["player_display_name"].unique()[:3])
            hint = f" Did you mean: '{names}'?"
        print(f"🤔 Couldn't find '{name}'.{hint}")
        return pd.DataFrame()
    if season is not None and not is_blank(season):
        sub = sub[sub["season"] == season]
    cols = [c for c in ["season", "week", "team", "opponent_team",
                        "fantasy_points"] if c in sub.columns]
    return sub.sort_values(["season", "week"])[cols].reset_index(drop=True)
