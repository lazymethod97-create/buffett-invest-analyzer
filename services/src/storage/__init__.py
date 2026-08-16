"""Persistence layer for Buffett Investment Analyzer.

Sprint35 introduces the storage package as an independent persistence layer.
"""

from .models import ScoreSnapshot
from .json_storage import JsonScoreStorage

__all__ = [
    "ScoreSnapshot",
    "JsonScoreStorage",
]