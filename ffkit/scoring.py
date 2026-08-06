"""The scoring engine — the heart of the Fantasy Football Lab.

Every fantasy platform (NFL.com, ESPN, Yahoo, Sleeper...) counts the same
real-life stats; they just award different points for them. A ScoringRules
object holds one league's point values, so the same notebooks work for ANY
league: pick a preset that matches yours, then tweak any number.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field

import pandas as pd

from .training import is_blank, nudge

# ---------------------------------------------------------------------------
# The rules object
# ---------------------------------------------------------------------------


@dataclass
class ScoringRules:
    """One league's scoring settings.

    Each dict maps a real stat column -> points per unit of that stat.
    defense_style is "idp" (draft individual defensive players, like the
    family NFL.com league) or "team" (draft one team defense / D-ST).
    """

    name: str
    defense_style: str  # "idp" or "team"
    offense: dict[str, float] = field(default_factory=dict)
    kicking: dict[str, float] = field(default_factory=dict)
    idp: dict[str, float] = field(default_factory=dict)
    dst: dict[str, float] = field(default_factory=dict)
    # (highest points allowed in tier, fantasy points) — checked in order
    dst_points_allowed: list[tuple[float, float]] = field(default_factory=list)
    roster: dict[str, int] = field(default_factory=dict)
    num_teams: int = 10

    def describe(self) -> None:
        """Print the rules in kid-friendly form."""
        print(f"🏆 League: {self.name}  ({self.num_teams} teams)")
        style = (
            "Individual defensive players (IDP)"
            if self.defense_style == "idp"
            else "One team defense (D/ST)"
        )
        print(f"🛡️  Defense style: {style}")
        print("\n--- Offense ---")
        for stat, pts in self.offense.items():
            print(f"  {STAT_LABELS.get(stat, stat)}: {pts:+g}")
        print("\n--- Kicking ---")
        for stat, pts in self.kicking.items():
            print(f"  {STAT_LABELS.get(stat, stat)}: {pts:+g}")
        if self.defense_style == "idp":
            print("\n--- Defensive players ---")
            for stat, pts in self.idp.items():
                print(f"  {STAT_LABELS.get(stat, stat)}: {pts:+g}")
        else:
            print("\n--- Team defense ---")
            for stat, pts in self.dst.items():
                print(f"  {STAT_LABELS.get(stat, stat)}: {pts:+g}")
            print("  Points allowed tiers:")
            low = 0
            for hi, pts in self.dst_points_allowed:
                label = f"{low:g}" if hi == low else (
                    f"{low:g}+" if hi == float("inf") else f"{low:g}-{hi:g}"
                )
                print(f"    {label} points allowed: {pts:+g}")
                low = hi + 1
        print("\n--- Starting lineup ---")
        print("  " + ", ".join(f"{n}× {slot}" for slot, n in self.roster.items()))


STAT_LABELS = {
    "passing_yards": "Passing yards",
    "passing_tds": "Passing TD",
    "passing_interceptions": "Interception thrown",
    "rushing_yards": "Rushing yards",
    "rushing_tds": "Rushing TD",
    "receptions": "Catch (reception)",
    "receiving_yards": "Receiving yards",
    "receiving_tds": "Receiving TD",
    "fumbles_lost_total": "Fumble lost",
    "passing_2pt_conversions": "2-pt conversion (pass)",
    "rushing_2pt_conversions": "2-pt conversion (run)",
    "receiving_2pt_conversions": "2-pt conversion (catch)",
    "special_teams_tds": "Kick/punt return TD",
    "fg_made_0_19": "Field goal 0-19 yds",
    "fg_made_20_29": "Field goal 20-29 yds",
    "fg_made_30_39": "Field goal 30-39 yds",
    "fg_made_40_49": "Field goal 40-49 yds",
    "fg_made_50_59": "Field goal 50-59 yds",
    "fg_made_60_": "Field goal 60+ yds",
    "fg_missed": "Missed field goal",
    "pat_made": "Extra point",
    "pat_missed": "Missed extra point",
    "def_tackles_solo": "Solo tackle",
    "def_tackle_assists": "Assisted tackle",
    "def_sacks": "Sack",
    "def_interceptions": "Interception caught",
    "def_pass_defended": "Pass defended",
    "def_fumbles_forced": "Forced fumble",
    "fumble_recovery_opp": "Fumble recovery",
    "def_tds": "Defensive TD",
    "def_safeties": "Safety",
    "sacks": "Sack",
    "interceptions": "Interception",
    "fumble_recoveries": "Fumble recovery",
    "safeties": "Safety",
    "tds": "Defensive/return TD",
}


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

_STANDARD_OFFENSE = {
    "passing_yards": 0.04,          # 1 point per 25 passing yards
    "passing_tds": 4,
    "passing_interceptions": -2,
    "rushing_yards": 0.1,           # 1 point per 10 rushing yards
    "rushing_tds": 6,
    "receptions": 0,                # PPR leagues change this!
    "receiving_yards": 0.1,
    "receiving_tds": 6,
    "fumbles_lost_total": -2,
    "passing_2pt_conversions": 2,
    "rushing_2pt_conversions": 2,
    "receiving_2pt_conversions": 2,
    "special_teams_tds": 6,
}

_NFL_KICKING = {
    "fg_made_0_19": 3, "fg_made_20_29": 3, "fg_made_30_39": 3,
    "fg_made_40_49": 3, "fg_made_50_59": 5, "fg_made_60_": 5,
    "fg_missed": 0, "pat_made": 1, "pat_missed": 0,
}

_ESPN_KICKING = {
    "fg_made_0_19": 3, "fg_made_20_29": 3, "fg_made_30_39": 3,
    "fg_made_40_49": 4, "fg_made_50_59": 5, "fg_made_60_": 5,
    "fg_missed": -1, "pat_made": 1, "pat_missed": -1,
}

_NFL_IDP = {
    "def_tackles_solo": 1,
    "def_tackle_assists": 0.5,
    "def_sacks": 2,
    "def_interceptions": 2,
    "def_pass_defended": 1,
    "def_fumbles_forced": 2,
    "fumble_recovery_opp": 2,
    "def_tds": 6,
    "def_safeties": 2,
}

_DST_STATS = {
    "sacks": 1,
    "interceptions": 2,
    "fumble_recoveries": 2,
    "safeties": 2,
    "tds": 6,
}

# NFL.com-style points-allowed tiers: (up to this many points, fantasy pts)
_NFL_PA_TIERS = [
    (0, 10), (6, 7), (13, 4), (20, 1), (27, 0), (34, -1), (float("inf"), -4),
]
# ESPN-style tiers
_ESPN_PA_TIERS = [
    (0, 5), (6, 4), (13, 3), (17, 1), (27, 0), (34, -1), (45, -3), (float("inf"), -5),
]

_PRESETS: dict[str, ScoringRules] = {}


def _add_preset(rules: ScoringRules) -> None:
    _PRESETS[rules.name] = rules


_add_preset(ScoringRules(
    name="NFL Standard + IDP",
    defense_style="idp",
    offense=_STANDARD_OFFENSE,
    kicking=_NFL_KICKING,
    idp=_NFL_IDP,
    roster={"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1,
            "DL": 2, "LB": 2, "DB": 2},
    num_teams=10,
))

_add_preset(ScoringRules(
    name="ESPN Full PPR",
    defense_style="team",
    offense={**_STANDARD_OFFENSE, "receptions": 1},
    kicking=_ESPN_KICKING,
    dst=_DST_STATS,
    dst_points_allowed=_ESPN_PA_TIERS,
    roster={"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1},
    num_teams=10,
))

_add_preset(ScoringRules(
    name="Half PPR",
    defense_style="team",
    offense={**_STANDARD_OFFENSE, "receptions": 0.5},
    kicking=_NFL_KICKING,
    dst=_DST_STATS,
    dst_points_allowed=_NFL_PA_TIERS,
    roster={"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1},
    num_teams=10,
))

_add_preset(ScoringRules(
    name="Standard + Team Defense",
    defense_style="team",
    offense=_STANDARD_OFFENSE,
    kicking=_NFL_KICKING,
    dst=_DST_STATS,
    dst_points_allowed=_NFL_PA_TIERS,
    roster={"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DST": 1},
    num_teams=10,
))


def preset_names() -> list[str]:
    return list(_PRESETS)


def get_rules(name: str) -> ScoringRules:
    """Get a copy of a preset you can safely customize."""
    if name not in _PRESETS:
        options = "', '".join(_PRESETS)
        raise KeyError(f"No preset called '{name}'. Try one of: '{options}'")
    return copy.deepcopy(_PRESETS[name])


# ---------------------------------------------------------------------------
# The actual scoring
# ---------------------------------------------------------------------------


def score_players(weekly: pd.DataFrame, rules: ScoringRules) -> pd.DataFrame:
    """Add a fantasy_points column: every player-week scored by YOUR rules."""
    df = weekly.copy()
    mappings: dict[str, float] = {**rules.offense, **rules.kicking}
    if rules.defense_style == "idp":
        mappings.update(rules.idp)
    pts = pd.Series(0.0, index=df.index)
    for col, per_unit in mappings.items():
        if is_blank(per_unit):
            nudge(f"points for '{STAT_LABELS.get(col, col)}'",
                  "Counting it as 0 for now.")
            continue
        if per_unit and col in df.columns:
            pts += df[col].fillna(0) * per_unit
    df["fantasy_points"] = pts.round(2)
    return df


def _points_allowed_pts(pa: float, tiers: list[tuple[float, float]]) -> float:
    for hi, pts in tiers:
        if pa <= hi:
            return pts
    return 0.0


def score_team_defense(
    weekly: pd.DataFrame, schedules: pd.DataFrame, rules: ScoringRules
) -> pd.DataFrame:
    """Fantasy points per team defense (D/ST) per week.

    Adds up every defender's stats for each team-week, then applies the
    points-allowed tiers using the real final scores from the schedule.
    """
    stat_cols = {
        "sacks": "def_sacks",
        "interceptions": "def_interceptions",
        "fumble_recoveries": "fumble_recovery_opp",
        "safeties": "def_safeties",
        "tds": "def_tds",
    }
    defenders = weekly[weekly["position_group"].isin(["DL", "LB", "DB"])]
    agg = (
        defenders.groupby(["season", "week", "team"])[list(set(stat_cols.values()))]
        .sum()
        .reset_index()
    )

    games = schedules[schedules["game_type"] == "REG"]
    home = games[["season", "week", "home_team", "away_score"]].rename(
        columns={"home_team": "team", "away_score": "points_allowed"}
    )
    away = games[["season", "week", "away_team", "home_score"]].rename(
        columns={"away_team": "team", "home_score": "points_allowed"}
    )
    pa = pd.concat([home, away], ignore_index=True)

    dst = agg.merge(pa, on=["season", "week", "team"], how="inner")
    pts = dst["points_allowed"].apply(
        lambda x: _points_allowed_pts(x, rules.dst_points_allowed)
    )
    for stat, per_unit in rules.dst.items():
        col = stat_cols.get(stat)
        if per_unit and col is not None:
            pts = pts + dst[col].fillna(0) * per_unit
    dst["fantasy_points"] = pts.astype(float).round(2)
    return dst.sort_values(["season", "week", "fantasy_points"], ascending=[True, True, False])
