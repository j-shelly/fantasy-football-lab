"""Draft helper: turn past seasons into projections, then into a Big Board.

The big ideas, in kid terms:
  1. PROJECTION — guess how many points a player will score this season,
     by blending their past seasons (YOU choose how much each year matters).
  2. VALUE OVER REPLACEMENT (VOR) — a player is only valuable compared to
     the best player you could grab off the bench pile instead. That's why
     the #1 RB can be worth more than a QB who scores more raw points.
"""

from __future__ import annotations

import re

import pandas as pd

from .scoring import ScoringRules, score_players, score_team_defense

# Positions a fantasy roster can actually use, per defense style
OFFENSE_POSITIONS = ["QB", "RB", "WR", "TE", "K"]
IDP_POSITIONS = ["DL", "LB", "DB"]

# Which positions can fill each lineup slot
SLOT_ELIGIBILITY = {
    "QB": ["QB"], "RB": ["RB"], "WR": ["WR"], "TE": ["TE"], "K": ["K"],
    "DST": ["DST"], "DL": ["DL"], "LB": ["LB"], "DB": ["DB"],
    "FLEX": ["RB", "WR", "TE"],
}


def _pos_key(row_position: str, row_group: str) -> str:
    """Collapse detailed positions (MLB, CB, FS, DE...) into fantasy slots."""
    if row_group in IDP_POSITIONS:
        return row_group
    return row_position


def build_player_pool(
    weekly: pd.DataFrame, schedules: pd.DataFrame, rules: ScoringRules
) -> pd.DataFrame:
    """Every draftable player-week, scored by YOUR league's rules.

    In a team-defense league this includes 32 'players' named after each
    team's defense (position DST) instead of individual defenders.
    """
    scored = score_players(weekly, rules)
    scored = scored.copy()
    scored["pos"] = [
        _pos_key(p, g)
        for p, g in zip(scored["position"], scored["position_group"])
    ]
    keep = OFFENSE_POSITIONS + (
        IDP_POSITIONS if rules.defense_style == "idp" else []
    )
    pool = scored[scored["pos"].isin(keep)][
        ["player_id", "player_display_name", "pos", "team", "opponent_team",
         "headshot_url", "season", "week", "fantasy_points"]
    ].copy()

    if rules.defense_style == "team":
        dst = score_team_defense(weekly, schedules, rules)
        dst_pool = pd.DataFrame({
            "player_id": "DST_" + dst["team"],
            "player_display_name": dst["team"] + " D/ST",
            "pos": "DST",
            "team": dst["team"],
            "opponent_team": None,
            "headshot_url": None,
            "season": dst["season"],
            "week": dst["week"],
            "fantasy_points": dst["fantasy_points"],
        })
        pool = pd.concat([pool, dst_pool], ignore_index=True)
    return pool


def season_stats(pool: pd.DataFrame) -> pd.DataFrame:
    """One row per player per season: games, totals, average, best/worst."""
    g = pool.groupby(["player_id", "player_display_name", "pos", "season"])
    out = g["fantasy_points"].agg(
        games="count", total="sum", per_game="mean", steady="std",
        best_week="max", worst_week="min",
    ).reset_index()
    out["total"] = out["total"].round(1)
    out["per_game"] = out["per_game"].round(2)
    out["steady"] = out["steady"].round(2)
    # keep each player's most recent team + headshot for display
    latest = (
        pool.sort_values(["season", "week"])
        .groupby("player_id")[["team", "headshot_url"]]
        .last()
    )
    return out.merge(latest, on="player_id", how="left")


def make_projections(
    pool: pd.DataFrame,
    past_matters: float = 0.5,
    durability: float = 0.5,
    steady_bonus: float = 0.0,
    seasons: tuple[int, ...] = (2023, 2024, 2025),
    games_in_season: int = 17,
) -> pd.DataFrame:
    """Project this season's points from past seasons.

    past_matters (0 to 1): how much older seasons count.
        0 = only last season matters, 1 = every season counts equally.
        In between, each older season counts past_matters as much as the
        one after it (0.5 -> weights 1, 0.5, 0.25).
    durability (0 to 1): how much missed games worry you.
        0 = assume everyone plays all 17, 1 = assume they miss as many
        games as they usually do.
    steady_bonus (-1 to 1): your taste in players.
        Positive = prefer steady every-week scorers,
        negative = prefer boom-or-bust players with huge best weeks,
        0 = just use the average.
    """
    from .training import is_blank, nudge

    if is_blank(past_matters):
        nudge("past_matters", "Using 0.5. Try 0.0 (only last season) or 1.0!")
        past_matters = 0.5
    if is_blank(durability):
        nudge("durability", "Using 0.5. Try 0.0 or 1.0!")
        durability = 0.5
    if is_blank(steady_bonus):
        nudge("steady_bonus", "Using 0. Try +1 (steady) or -1 (boom-bust)!")
        steady_bonus = 0.0

    stats = season_stats(pool[pool["season"].isin(seasons)])
    newest = max(seasons)
    stats["weight"] = [past_matters ** (newest - s) for s in stats["season"]]

    def project(grp: pd.DataFrame) -> pd.Series:
        w = grp["weight"]
        ppg = (grp["per_game"] * w).sum() / w.sum()
        wobble = (grp["steady"].fillna(0) * w).sum() / w.sum()
        games_rate = (grp["games"].clip(upper=games_in_season) * w).sum() / (
            w.sum() * games_in_season
        )
        proj_games = games_in_season * (1 - durability * (1 - games_rate))
        adj_ppg = ppg + steady_bonus * (ppg * 0.15 - wobble * 0.5)
        return pd.Series({
            "proj_per_game": round(adj_ppg, 2),
            "proj_games": round(proj_games, 1),
            "proj_points": round(adj_ppg * proj_games, 1),
            "wobble": round(wobble, 2),
            "last_season_ppg": grp.loc[grp["season"].idxmax(), "per_game"],
        })

    proj = (
        stats.groupby(["player_id", "player_display_name", "pos"])
        .apply(project, include_groups=False)
        .reset_index()
    )
    latest = (
        stats.sort_values("season")
        .groupby("player_id")[["team", "headshot_url"]]
        .last()
    )
    proj = proj.merge(latest, on="player_id", how="left")
    # Skip players who have basically left the league (no games last season)
    active_ids = set(stats[stats["season"] == newest]["player_id"])
    proj = proj[proj["player_id"].isin(active_ids)]
    return proj


def replacement_ranks(rules: ScoringRules) -> dict[str, int]:
    """How many players at each position get started league-wide.

    The player ranked right after that is the 'replacement' — the best
    player who'd sit on waivers. FLEX spots are split among RB/WR/TE.
    """
    starters: dict[str, float] = {}
    for slot, count in rules.roster.items():
        eligible = SLOT_ELIGIBILITY.get(slot, [])
        if len(eligible) == 1:
            starters[eligible[0]] = starters.get(eligible[0], 0) + count
        else:  # FLEX
            for p in eligible:
                starters[p] = starters.get(p, 0) + count / len(eligible)
    return {
        pos: max(1, round(n * rules.num_teams)) for pos, n in starters.items()
    }


def big_board(
    proj: pd.DataFrame, rules: ScoringRules, top: int = 200
) -> pd.DataFrame:
    """Rank everyone on ONE list using value over replacement (VOR)."""
    board = proj.copy()
    board["pos_rank"] = board.groupby("pos")["proj_points"].rank(
        ascending=False, method="first"
    ).astype(int)

    repl = replacement_ranks(rules)
    repl_points = {}
    for pos, rank in repl.items():
        at_pos = board[board["pos"] == pos].sort_values(
            "proj_points", ascending=False
        )
        if len(at_pos) == 0:
            continue
        idx = min(rank, len(at_pos) - 1)
        repl_points[pos] = at_pos["proj_points"].iloc[idx]
    board = board[board["pos"].isin(repl_points)].copy()
    board["replacement"] = board["pos"].map(repl_points)
    board["value"] = (board["proj_points"] - board["replacement"]).round(1)

    board = board.sort_values("value", ascending=False).head(top).copy()
    board["rank"] = range(1, len(board) + 1)
    tier_edges = [3, 8, 15, 24, 999]
    board["tier"] = board["pos_rank"].apply(
        lambda r: next(i + 1 for i, edge in enumerate(tier_edges) if r <= edge)
    )
    cols = ["rank", "player_display_name", "pos", "team", "pos_rank", "tier",
            "proj_per_game", "proj_games", "proj_points", "value",
            "wobble", "headshot_url", "player_id"]
    return board[[c for c in cols if c in board.columns]].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Comparing with the experts
# ---------------------------------------------------------------------------

_SUFFIXES = re.compile(r"\s+(jr|sr|ii|iii|iv|v)\.?$")


def _mergename(name: str) -> str:
    n = re.sub(r"[^a-z ]", "", str(name).lower().strip())
    return _SUFFIXES.sub("", n).strip()


_EXPERT_PAGES = {
    "QB": "redraft-qb", "RB": "redraft-rb", "WR": "redraft-wr",
    "TE": "redraft-te", "K": "redraft-k", "DST": "redraft-dst",
    "DL": "redraft-dl", "LB": "redraft-lb", "DB": "redraft-db",
}


def expert_position_ranks(rankings: pd.DataFrame) -> pd.DataFrame:
    """Expert consensus rank within each position (FantasyPros)."""
    rk = rankings[rankings["page_type"].isin(_EXPERT_PAGES.values())].copy()
    page_to_pos = {v: k for k, v in _EXPERT_PAGES.items()}
    rk["pos"] = rk["page_type"].map(page_to_pos)
    rk["expert_rank"] = rk.groupby("pos")["ecr"].rank(method="first").astype(int)
    rk["join_name"] = rk["mergename"].map(_mergename)
    return rk[["join_name", "player", "pos", "tm", "expert_rank", "bye"]]


def compare_with_experts(
    board: pd.DataFrame, rankings: pd.DataFrame
) -> pd.DataFrame:
    """Your board vs the pros: who do YOU like more than they do?"""
    experts = expert_position_ranks(rankings)
    mine = board.copy()
    mine["join_name"] = mine["player_display_name"].map(_mergename)
    # Team defenses join on team abbreviation instead of name
    dst = mine["pos"] == "DST"
    mine.loc[dst, "join_name"] = mine.loc[dst, "team"]
    experts = experts.copy()
    edst = experts["pos"] == "DST"
    experts.loc[edst, "join_name"] = experts.loc[edst, "tm"]

    merged = mine.merge(
        experts[["join_name", "pos", "expert_rank", "bye"]],
        on=["join_name", "pos"], how="left",
    )
    merged["expert_rank"] = merged["expert_rank"].astype("Int64")
    merged["we_disagree_by"] = merged["expert_rank"] - merged["pos_rank"]
    return merged.drop(columns=["join_name"])
