"""Data loading for the Fantasy Football Lab.

Downloads real NFL data from nflverse (the free, community-maintained dataset
that powers most analytics sites) and caches it as parquet files in data/ so
the notebooks load instantly and work offline after the first fetch.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# The seasons we keep locally. Projections use the most recent three;
# the extra history is there for exploring.
SEASONS = [2021, 2022, 2023, 2024, 2025]

# The kid-facing subset of the 145 stat columns. The full table is still
# available via load_weekly(slim=False).
FRIENDLY_COLUMNS = [
    "player_id", "player_display_name", "position", "position_group",
    "headshot_url", "team", "opponent_team", "season", "week",
    # offense
    "passing_yards", "passing_tds", "passing_interceptions",
    "carries", "rushing_yards", "rushing_tds",
    "targets", "receptions", "receiving_yards", "receiving_tds",
    "fumbles_lost_total",
    "passing_2pt_conversions", "rushing_2pt_conversions",
    "receiving_2pt_conversions", "special_teams_tds",
    # kicking
    "fg_made", "fg_made_0_19", "fg_made_20_29", "fg_made_30_39",
    "fg_made_40_49", "fg_made_50_59", "fg_made_60_", "fg_missed",
    "pat_made", "pat_missed",
    # individual defense (IDP)
    "def_tackles_solo", "def_tackle_assists", "def_tackles_for_loss",
    "def_sacks", "def_interceptions", "def_pass_defended",
    "def_fumbles_forced", "fumble_recovery_opp", "def_tds", "def_safeties",
]


def _cache_path(name: str) -> Path:
    return DATA_DIR / f"{name}.parquet"


def _cached(name: str, fetch, refresh: bool = False) -> pd.DataFrame:
    """Return the cached parquet if present, otherwise fetch and cache it."""
    path = _cache_path(name)
    if path.exists() and not refresh:
        return pd.read_parquet(path)
    df = fetch().to_pandas()
    DATA_DIR.mkdir(exist_ok=True)
    df.to_parquet(path, index=False)
    return df


def load_weekly(refresh: bool = False, slim: bool = True) -> pd.DataFrame:
    """Weekly stats for every player (offense, kickers, and defenders),
    regular season only."""
    import nflreadpy as nfl

    df = _cached(
        "weekly_stats",
        lambda: nfl.load_player_stats(SEASONS, summary_level="week"),
        refresh,
    )
    df = df[df["season_type"] == "REG"].copy()
    if slim:
        df = df[[c for c in FRIENDLY_COLUMNS if c in df.columns]].copy()
    return df


def load_schedules(refresh: bool = False) -> pd.DataFrame:
    """Game schedules and final scores (used for team-defense points allowed
    and bye weeks)."""
    import nflreadpy as nfl

    return _cached("schedules", lambda: nfl.load_schedules(SEASONS), refresh)


def load_teams(refresh: bool = False) -> pd.DataFrame:
    """Team names, divisions, colors, and logos."""
    import nflreadpy as nfl

    return _cached("teams", lambda: nfl.load_teams(), refresh)


def load_rankings(refresh: bool = False) -> pd.DataFrame:
    """Current expert consensus draft rankings from FantasyPros
    (via the nflverse/dynastyprocess mirror)."""
    import nflreadpy as nfl

    return _cached("expert_rankings", lambda: nfl.load_ff_rankings("draft"), refresh)


def refresh_all() -> None:
    """Re-download everything. Run before draft day / each week in-season."""
    for name, fn in [
        ("weekly stats", lambda: load_weekly(refresh=True, slim=False)),
        ("schedules", lambda: load_schedules(refresh=True)),
        ("teams", lambda: load_teams(refresh=True)),
        ("expert rankings", lambda: load_rankings(refresh=True)),
    ]:
        df = fn()
        print(f"  ✅ {name}: {len(df):,} rows")


def cache_ready() -> bool:
    return all(
        _cache_path(n).exists()
        for n in ["weekly_stats", "schedules", "teams", "expert_rankings"]
    )
