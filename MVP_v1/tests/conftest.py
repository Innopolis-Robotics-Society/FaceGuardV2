"""Pytest configuration: insert the project root on sys.path so that
`from app...` works without installing the package."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
