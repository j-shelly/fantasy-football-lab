"""Sliders and dropdowns for the notebooks.

Everything here also works without touching a widget: each panel starts from
sensible defaults, and every notebook shows the plain-code way too.
"""

from __future__ import annotations

import copy

import pandas as pd
from IPython.display import display

from . import draft as _draft
from . import viz as _viz
from .scoring import get_rules, preset_names, ScoringRules

_current_rules: ScoringRules | None = None


def current_rules() -> ScoringRules:
    """The rules chosen in the scoring picker (or the family default)."""
    global _current_rules
    if _current_rules is None:
        _current_rules = get_rules("NFL Standard + IDP")
    return copy.deepcopy(_current_rules)


def scoring_picker():
    """Pick a preset and tweak the numbers kids argue about most."""
    global _current_rules
    import ipywidgets as w

    _current_rules = current_rules()

    preset = w.Dropdown(options=preset_names(), value=_current_rules.name,
                        description="League:", style={"description_width": "110px"})
    catch = w.FloatText(description="Per catch:", step=0.5,
                        value=_current_rules.offense["receptions"],
                        style={"description_width": "110px"})
    pass_td = w.FloatText(description="Passing TD:", step=1,
                          value=_current_rules.offense["passing_tds"],
                          style={"description_width": "110px"})
    intercept = w.FloatText(description="INT thrown:", step=1,
                            value=_current_rules.offense["passing_interceptions"],
                            style={"description_width": "110px"})
    teams = w.IntSlider(description="Teams:", min=6, max=14,
                        value=_current_rules.num_teams,
                        style={"description_width": "110px"})
    out = w.Output()

    def rebuild(_change=None):
        global _current_rules
        rules = get_rules(preset.value)
        if _change and _change["owner"] is preset:
            # switching preset: refresh the tweak boxes to its values
            catch.value = rules.offense["receptions"]
            pass_td.value = rules.offense["passing_tds"]
            intercept.value = rules.offense["passing_interceptions"]
            teams.value = rules.num_teams
        rules.offense["receptions"] = catch.value
        rules.offense["passing_tds"] = pass_td.value
        rules.offense["passing_interceptions"] = intercept.value
        rules.num_teams = teams.value
        _current_rules = rules
        out.clear_output()
        with out:
            rules.describe()

    for control in (preset, catch, pass_td, intercept, teams):
        control.observe(rebuild, names="value")
    rebuild()
    display(w.VBox([
        w.HTML("<b>🎛️ Your league's rules</b> "
               "<span style='color:#898781'>(pick a preset, then tweak)</span>"),
        preset, catch, pass_td, intercept, teams, out,
    ]))


def _blue_shading(col: pd.Series) -> list[str]:
    """Shade a numeric column light-to-dark blue.

    pandas' built-in background_gradient needs matplotlib, which the lab
    doesn't install — so we mix the colors ourselves.
    """
    lo, hi = col.min(), col.max()
    span = hi - lo
    styles = []
    for v in col:
        if pd.isna(v) or pd.isna(span):
            styles.append("")
            continue
        t = 0.0 if span == 0 else (v - lo) / span
        r = round(247 + t * (8 - 247))
        g = round(251 + t * (48 - 251))
        b = round(255 + t * (107 - 255))
        text = "#f1f1f1" if t > 0.55 else "#000000"
        styles.append(f"background-color: rgb({r},{g},{b}); color: {text}")
    return styles


def draft_dashboard(pool: pd.DataFrame, rules: ScoringRules, top: int = 15):
    """The Draft Machine: move a slider, watch the whole board re-rank."""
    import ipywidgets as w

    def update(past_matters, durability, taste, teams):
        my_rules = copy.deepcopy(rules)
        my_rules.num_teams = teams
        proj = _draft.make_projections(
            pool, past_matters=past_matters, durability=durability,
            steady_bonus=taste,
        )
        board = _draft.big_board(proj, my_rules)
        show = board.head(top)[
            ["rank", "player_display_name", "pos", "team", "tier",
             "proj_per_game", "proj_points", "value"]
        ].rename(columns={"player_display_name": "player"})
        display(show.style.hide(axis="index").apply(
            _blue_shading, subset=["value"]))
        _viz.big_board_chart(board, top=top).show()

    w.interact(
        update,
        past_matters=w.FloatSlider(
            value=0.5, min=0.0, max=1.0, step=0.1,
            description="Old seasons count:", continuous_update=False,
            style={"description_width": "150px"}, readout_format=".1f",
        ),
        durability=w.FloatSlider(
            value=0.5, min=0.0, max=1.0, step=0.1,
            description="Worry about injuries:", continuous_update=False,
            style={"description_width": "150px"}, readout_format=".1f",
        ),
        taste=w.FloatSlider(
            value=0.0, min=-1.0, max=1.0, step=0.25,
            description="Steady ↔ Boom-bust:", continuous_update=False,
            style={"description_width": "150px"}, readout_format=".2f",
        ),
        teams=w.IntSlider(
            value=rules.num_teams, min=6, max=14,
            description="Teams in league:", continuous_update=False,
            style={"description_width": "150px"},
        ),
    )
