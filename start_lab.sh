#!/usr/bin/env bash
# Launch the Fantasy Football Lab.
# From this folder, run:  ./start_lab.sh
# Then open the link it prints (or your browser opens automatically).
cd "$(dirname "$0")"
exec uv run jupyter lab --notebook-dir=notebooks
