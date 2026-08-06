"""Support for the ⭐ TRY IT exercises.

The special value ____ (four underscores) marks a blank for kids to fill in.
If they run a cell without filling it, nothing crashes — the lab prints a
friendly nudge and falls back to something sensible so the notebook keeps
working top-to-bottom.
"""

from __future__ import annotations


class Blank:
    """The ✏️ fill-me-in marker used in TRY IT cells."""

    def __repr__(self) -> str:
        return "✏️ ____  ← replace this blank with your answer!"

    def __bool__(self) -> bool:
        return False


____ = Blank()


def is_blank(value) -> bool:
    return isinstance(value, Blank)


def nudge(what: str, fallback_msg: str) -> None:
    print(f"✏️ You still have a blank to fill in ({what})! {fallback_msg}")
