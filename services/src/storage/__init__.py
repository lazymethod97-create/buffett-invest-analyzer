"""Persistence layer for Buffett Investment Analyzer.

Sprint35 introduces the storage package as an independent persistence layer.
Sprint36 adds snapshot_builder, which maps create_analysis_bundle() output
onto ScoreSnapshot so app.py can auto-save without embedding that logic
itself (PROJECT_RULES.md Rule 4).
"""

from .models import ScoreSnapshot
from .json_storage import JsonScoreStorage
from .snapshot_builder import build_score_snapshot, resolve_snapshot_mode

__all__ = [
    "ScoreSnapshot",
    "JsonScoreStorage",
    "build_score_snapshot",
    "resolve_snapshot_mode",
]