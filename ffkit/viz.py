"""The 🪄 magic charts.

Interactive plotly visualizations the kids just *run* — the code in here is
deliberately hidden away so the notebooks stay friendly. Colors follow the
lab's validated palette: each position always wears the same color, identity
is never carried by color alone (names are printed on/next to marks), and
sequential scales use a single blue ramp.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# --- palette (validated: see project notes) --------------------------------
POSITION_COLORS = {
    "QB": "#1baf7a",   # aqua
    "RB": "#2a78d6",   # blue
    "WR": "#eb6834",   # orange
    "TE": "#4a3aa7",   # violet
    "K": "#eda100",    # yellow
    "DL": "#008300",   # green
    "DST": "#008300",  # green (never on screen with DL)
    "LB": "#e87ba4",   # magenta
    "DB": "#e34948",   # red
}
SEQ_BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
             "#256abf", "#184f95", "#0d366b"]

_SURFACE = "#fcfcfb"
_INK = "#0b0b0b"
_INK2 = "#52514e"
_MUTED = "#898781"
_GRID = "#e1e0d9"
_BASE = "#c3c2b7"
_FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'

_template = go.layout.Template(
    layout=dict(
        font=dict(family=_FONT, color=_INK2, size=13),
        title=dict(font=dict(color=_INK, size=17)),
        paper_bgcolor=_SURFACE,
        plot_bgcolor=_SURFACE,
        xaxis=dict(gridcolor=_GRID, linecolor=_BASE, zerolinecolor=_BASE,
                   tickfont=dict(color=_MUTED)),
        yaxis=dict(gridcolor=_GRID, linecolor=_BASE, zerolinecolor=_BASE,
                   tickfont=dict(color=_MUTED)),
        legend=dict(font=dict(color=_INK2)),
        margin=dict(l=70, r=30, t=60, b=50),
        hoverlabel=dict(font=dict(family=_FONT)),
    )
)
pio.templates["fflab"] = _template


def _pos_color(pos: str) -> str:
    return POSITION_COLORS.get(pos, _MUTED)


# ---------------------------------------------------------------------------
# Draft charts
# ---------------------------------------------------------------------------


def big_board_chart(board: pd.DataFrame, top: int = 25) -> go.Figure:
    """The Big Board: best draft values, best at the top."""
    df = board.head(top).iloc[::-1]
    labels = [
        f"{r}. {n}  ({p})"
        for r, n, p in zip(df["rank"], df["player_display_name"], df["pos"])
    ]
    fig = go.Figure()
    for pos in df["pos"].unique():
        sub = df[df["pos"] == pos]
        fig.add_bar(
            x=sub["value"],
            y=[labels[i] for i, ok in enumerate(df["pos"] == pos) if ok],
            orientation="h",
            name=pos,
            marker=dict(color=_pos_color(pos)),
            customdata=sub[["proj_per_game", "proj_points", "pos_rank", "tier"]],
            hovertemplate=(
                "<b>%{y}</b><br>Draft value: %{x:.0f}"
                "<br>Projected: %{customdata[1]:.0f} pts"
                " (%{customdata[0]:.1f}/game)"
                "<br>Position rank: #%{customdata[2]} · Tier %{customdata[3]}"
                "<extra></extra>"
            ),
        )
    fig.update_layout(
        template="fflab",
        title=f"🏈 Your Big Board — top {len(df)} draft values",
        xaxis_title="Value over a replacement player (season points)",
        yaxis=dict(categoryorder="array", categoryarray=labels,
                   tickfont=dict(color=_INK2, size=12)),
        bargap=0.35,
        height=max(420, 26 * len(df) + 120),
        legend_title_text="Position",
    )
    return fig


def value_scatter(board: pd.DataFrame,
                  positions: tuple[str, ...] = ("QB", "RB", "WR", "TE"),
                  label_top: int = 8) -> go.Figure:
    """Points-per-game vs. weekly up-and-down. Up & left = steady star."""
    df = board[board["pos"].isin(positions)].copy()
    fig = go.Figure()
    labeled = set(df.nlargest(label_top, "value")["player_display_name"])
    for pos in positions:
        sub = df[df["pos"] == pos]
        if len(sub) == 0:
            continue
        text = [n if n in labeled else "" for n in sub["player_display_name"]]
        fig.add_scatter(
            x=sub["proj_per_game"], y=sub["wobble"],
            mode="markers+text", name=pos, text=text,
            textposition="top center",
            textfont=dict(color=_INK2, size=11),
            marker=dict(color=_pos_color(pos), size=9, opacity=0.85,
                        line=dict(color=_SURFACE, width=1)),
            customdata=sub[["player_display_name", "proj_points"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b> (" + pos + ")"
                "<br>Projected per game: %{x:.1f}"
                "<br>Weekly up-and-down: %{y:.1f}"
                "<br>Season projection: %{customdata[1]:.0f} pts"
                "<extra></extra>"
            ),
        )
    fig.update_layout(
        template="fflab",
        title="⚖️ Steady stars vs. boom-or-bust",
        xaxis_title="Projected points per game →",
        yaxis_title="Weekly up-and-down (higher = wilder weeks)",
        height=520,
        legend_title_text="Position",
    )
    return fig


def experts_scatter(compared: pd.DataFrame, positions: tuple[str, ...] | None = None,
                    label_top: int = 6) -> go.Figure:
    """Your position ranks vs. the experts'. On the line = you agree."""
    df = compared.dropna(subset=["expert_rank"]).copy()
    if positions:
        df = df[df["pos"].isin(positions)]
    df = df[df["pos_rank"] <= 40]
    hot = df.reindex(
        df["we_disagree_by"].astype(float).abs().nlargest(label_top).index
    )
    labeled = set(hot["player_display_name"])
    lim = max(df["pos_rank"].max(), df["expert_rank"].max()) + 2
    fig = go.Figure()
    fig.add_scatter(
        x=[0, lim], y=[0, lim], mode="lines",
        line=dict(color=_BASE, width=2, dash="dot"),
        name="You agree", hoverinfo="skip",
    )
    for pos in df["pos"].unique():
        sub = df[df["pos"] == pos]
        text = [n if n in labeled else "" for n in sub["player_display_name"]]
        fig.add_scatter(
            x=sub["expert_rank"], y=sub["pos_rank"],
            mode="markers+text", name=pos, text=text,
            textposition="top center", textfont=dict(color=_INK2, size=11),
            marker=dict(color=_pos_color(pos), size=9, opacity=0.85,
                        line=dict(color=_SURFACE, width=1)),
            customdata=sub[["player_display_name"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b> (" + pos + ")"
                "<br>Experts say: #%{x}"
                "<br>You say: #%{y}"
                "<extra></extra>"
            ),
        )
    fig.update_layout(
        template="fflab",
        title="🧑‍⚖️ You vs. the experts (position ranks)",
        xaxis_title="Expert consensus rank →",
        yaxis_title="Your rank →",
        yaxis=dict(autorange="reversed"),
        xaxis=dict(autorange="reversed", side="top"),
        height=560,
        legend_title_text="Position",
        annotations=[dict(
            text="⬆ above the line = you like them MORE than the experts",
            xref="paper", yref="paper", x=0.02, y=0.02, showarrow=False,
            font=dict(color=_MUTED, size=12),
        )],
    )
    return fig


# ---------------------------------------------------------------------------
# Player deep-dives
# ---------------------------------------------------------------------------


def boom_bust_box(pool: pd.DataFrame, names: list[str],
                  seasons: tuple[int, ...] = (2024, 2025)) -> go.Figure:
    """Every week as a dot: see each player's whole range, not just the average."""
    df = pool[pool["season"].isin(seasons)]
    fig = go.Figure()
    found = []
    for name in names:
        sub = df[df["player_display_name"].str.lower() == name.lower()]
        if len(sub) == 0:
            print(f"🤔 Couldn't find '{name}' — check the spelling?")
            continue
        found.append(name)
        real_name = sub["player_display_name"].iloc[0]
        pos = sub["pos"].iloc[0] if "pos" in sub.columns else sub["position"].iloc[0]
        fig.add_box(
            y=sub["fantasy_points"],
            name=f"{real_name} ({pos})",
            boxpoints="all", jitter=0.4, pointpos=0,
            marker=dict(color=_pos_color(pos), size=6, opacity=0.7),
            line=dict(color=_pos_color(pos), width=2),
            fillcolor="rgba(0,0,0,0)",
            customdata=sub[["season", "week"]],
            hovertemplate=(
                "<b>%{y:.1f} pts</b> — "
                "week %{customdata[1]}, %{customdata[0]}<extra></extra>"
            ),
        )
    fig.update_layout(
        template="fflab",
        title="🎢 Boom or bust? Every single week, as a dot",
        yaxis_title="Fantasy points that week",
        showlegend=False,
        height=500,
    )
    return fig


def season_race(pool: pd.DataFrame, names: list[str], season: int) -> go.Figure:
    """A season as a race: total points climbing week by week."""
    df = pool[pool["season"] == season]
    fig = go.Figure()
    for name in names:
        sub = df[df["player_display_name"].str.lower() == name.lower()]
        if len(sub) == 0:
            print(f"🤔 Couldn't find '{name}' in {season} — check the spelling?")
            continue
        sub = sub.sort_values("week")
        real_name = sub["player_display_name"].iloc[0]
        pos = sub["pos"].iloc[0] if "pos" in sub.columns else sub["position"].iloc[0]
        totals = sub["fantasy_points"].cumsum()
        fig.add_scatter(
            x=sub["week"], y=totals, mode="lines+markers",
            name=f"{real_name} ({pos})",
            line=dict(color=_pos_color(pos), width=2),
            marker=dict(size=6),
            hovertemplate=(
                f"<b>{real_name}</b><br>Week %{{x}}: "
                "%{y:.0f} total points<extra></extra>"
            ),
        )
        fig.add_annotation(
            x=sub["week"].iloc[-1], y=totals.iloc[-1],
            text=real_name.split()[-1], showarrow=False,
            xanchor="left", xshift=6, font=dict(color=_INK2, size=11),
        )
    fig.update_layout(
        template="fflab",
        title=f"🏁 The {season} season as a race",
        xaxis_title="Week",
        yaxis_title="Total fantasy points so far",
        height=500,
        legend_title_text="Player",
    )
    return fig


def weekly_heatmap(pool: pd.DataFrame, season: int, top: int = 20) -> go.Figure:
    """Player-by-week grid — dark blue squares are monster games."""
    df = pool[pool["season"] == season]
    totals = (
        df.groupby("player_display_name")["fantasy_points"].sum()
        .nlargest(top)
    )
    sub = df[df["player_display_name"].isin(totals.index)]
    grid = sub.pivot_table(index="player_display_name", columns="week",
                           values="fantasy_points", aggfunc="sum")
    grid = grid.reindex(totals.index[::-1])
    fig = go.Figure(go.Heatmap(
        z=grid.values, x=[f"W{w}" for w in grid.columns], y=grid.index,
        colorscale=[[i / (len(SEQ_BLUES) - 1), c] for i, c in enumerate(SEQ_BLUES)],
        hoverongaps=False, xgap=2, ygap=2,
        hovertemplate="<b>%{y}</b><br>Week %{x}: %{z:.1f} pts<extra></extra>",
        colorbar=dict(title="Points", tickfont=dict(color=_MUTED)),
    ))
    fig.update_layout(
        template="fflab",
        title=f"🔥 Week-by-week scoring, top {top} players of {season}",
        height=max(440, 24 * top + 140),
        xaxis=dict(side="top"),
        yaxis=dict(tickfont=dict(color=_INK2, size=12)),
    )
    return fig


def lineup_chart(rated: pd.DataFrame) -> go.Figure:
    """Your players this week, best matchups first."""
    df = rated.sort_values("expected").copy()
    labels = [f"{p}  ({pos})" for p, pos in zip(df["player"], df["pos"])]
    fig = go.Figure()
    for pos in df["pos"].unique():
        mask = df["pos"] == pos
        sub = df[mask]
        fig.add_bar(
            x=sub["expected"],
            y=[l for l, ok in zip(labels, mask) if ok],
            orientation="h", name=pos,
            marker=dict(color=_pos_color(pos)),
            customdata=sub[["opponent", "last3_avg", "matchup_score"]],
            hovertemplate=(
                "<b>%{y}</b><br>Expected: %{x:.1f} pts"
                "<br>Opponent: %{customdata[0]}"
                "<br>Last 3 games: %{customdata[1]:.1f}/game"
                "<br>Matchup ease: %{customdata[2]}/10"
                "<extra></extra>"
            ),
        )
    fig.update_layout(
        template="fflab",
        title="📋 This week's expected points",
        xaxis_title="Expected fantasy points",
        yaxis=dict(categoryorder="array", categoryarray=labels,
                   tickfont=dict(color=_INK2, size=12)),
        bargap=0.35, height=max(380, 28 * len(df) + 130),
        legend_title_text="Position",
    )
    return fig


# ---------------------------------------------------------------------------
# The player card (HTML, with headshot + team colors)
# ---------------------------------------------------------------------------


def player_card(pool: pd.DataFrame, name: str, teams: pd.DataFrame | None = None):
    """A trading-card style profile for one player."""
    from IPython.display import HTML

    sub = pool[pool["player_display_name"].str.lower() == name.lower()]
    if len(sub) == 0:
        print(f"🤔 Couldn't find '{name}' — check the spelling?")
        return None
    sub = sub.sort_values(["season", "week"])
    real_name = sub["player_display_name"].iloc[0]
    pos = sub["pos"].iloc[0] if "pos" in sub.columns else sub["position"].iloc[0]
    team = sub["team"].dropna().iloc[-1]
    headshot = sub["headshot_url"].dropna()
    headshot = headshot.iloc[-1] if len(headshot) else ""
    color1, color2 = "#2a3f5f", "#c3c2b7"
    team_name = team
    if teams is not None:
        trow = teams[teams["team_abbr"] == team]
        if len(trow):
            color1 = trow["team_color"].iloc[0] or color1
            color2 = trow["team_color2"].iloc[0] or color2
            team_name = trow["team_name"].iloc[0]

    latest_season = int(sub["season"].max())
    this = sub[sub["season"] == latest_season]["fantasy_points"]
    last10 = sub["fantasy_points"].tail(10).tolist()
    hi, lo = (max(last10), min(last10)) if last10 else (1, 0)
    span = (hi - lo) or 1
    pts = " ".join(
        f"{i * (160 / max(len(last10) - 1, 1)):.0f},"
        f"{36 - (v - lo) / span * 30:.0f}"
        for i, v in enumerate(last10)
    )
    spark = (
        f'<svg width="170" height="42" style="overflow:visible">'
        f'<polyline points="{pts}" fill="none" stroke="{color1}" '
        f'stroke-width="2" stroke-linecap="round"/></svg>'
    )
    img = (
        f'<img src="{headshot}" alt="{real_name}" '
        'style="height:96px;border-radius:8px;background:#fff">'
        if headshot else ""
    )
    stats = {
        f"{latest_season} total": f"{this.sum():.0f} pts",
        "Per game": f"{this.mean():.1f}",
        "Best week": f"{this.max():.1f}",
        "Games": f"{len(this)}",
    }
    cells = "".join(
        f'<div style="text-align:center;padding:0 12px">'
        f'<div style="font-size:20px;font-weight:700;color:#0b0b0b">{v}</div>'
        f'<div style="font-size:11px;color:#898781">{k}</div></div>'
        for k, v in stats.items()
    )
    return HTML(f"""
<div style='font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
     max-width:520px;border:1px solid rgba(11,11,11,.1);border-radius:14px;
     overflow:hidden;background:#fcfcfb'>
  <div style="background:{color1};height:10px"></div>
  <div style="display:flex;gap:16px;padding:16px;align-items:center">
    {img}
    <div>
      <div style="font-size:22px;font-weight:800;color:#0b0b0b">{real_name}</div>
      <div style="font-size:13px;color:#52514e">{pos} · {team_name}</div>
      <div style="margin-top:6px">{spark}
        <div style="font-size:10px;color:#898781">last 10 games</div></div>
    </div>
  </div>
  <div style="display:flex;justify-content:space-around;
       border-top:1px solid #e1e0d9;padding:10px 4px">{cells}</div>
</div>""")
