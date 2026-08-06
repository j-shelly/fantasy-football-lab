"""Pre-download all NFL data so the kids never wait for a download.

Run from the project root:
    uv run python scripts/warm_cache.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ffkit import data

if __name__ == "__main__":
    print("🏈 Downloading NFL data from nflverse (this takes a minute)...")
    data.refresh_all()
    print("🎉 All data cached in data/ — the notebooks are ready to go!")
