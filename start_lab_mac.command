#!/usr/bin/env bash
# Launch the Fantasy Football Lab (Mac).
# Double-click this file. If macOS blocks it the first time,
# right-click it, choose "Open", then click "Open" in the dialog.
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
exec uv run jupyter lab --notebook-dir=notebooks
