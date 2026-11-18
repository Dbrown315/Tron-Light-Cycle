#
# File: __init.py
# Group: Group 9
# Purpose: Resolve import conflicts and path dependencies.

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_ROOT = REPO_ROOT / "Matrix"

for path in (REPO_ROOT, MATRIX_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
