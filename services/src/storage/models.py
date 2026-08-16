"""Data models for the persistence layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


VALID_MODES = {"quick", "standard", "full"}
VALID_GRADES = {"S", "A", "B", "C", "D"}
VALID_DECISIONS = {"BUY", "WATCH", "PASS"}


@dataclass(frozen=True)
class ScoreSnapshot:
    """A lightweight snapshot of one single-ticker evaluation.

    This model intentionally stores only the information required for
    future score-history features. It does not contain Portfolio Risk,
    Watchlist Insights, or any additional score axis.
    """

    ticker: str
    evaluated_at: str
    mode: str
    overall_score: int
    grade: str
    decision: str
    buffett_score: Optional[int] = None

    def __post_init__(self) -> None:
        ticker = str(self.ticker).strip()
        mode = str(self.mode).strip()
        grade = str(self.grade).strip()
        decision = str(self.decision).strip()

        if not ticker:
            raise ValueError("ticker must not be empty")

        if mode not in VALID_MODES:
            raise ValueError(
                f"mode must be one of: {', '.join(sorted(VALID_MODES))}"
            )

        if grade not in VALID_GRADES:
            raise ValueError(
                f"grade must be one of: {', '.join(sorted(VALID_GRADES))}"
            )

        if decision not in VALID_DECISIONS:
            raise ValueError(
                f"decision must be one of: {', '.join(sorted(VALID_DECISIONS))}"
            )

        if isinstance(self.overall_score, bool):
            raise ValueError("overall_score must be an integer")

        if not isinstance(self.overall_score, int):
            raise ValueError("overall_score must be an integer")

        if not 0 <= self.overall_score <= 190:
            raise ValueError("overall_score must be between 0 and 190")

        if self.buffett_score is not None:
            if isinstance(self.buffett_score, bool):
                raise ValueError("buffett_score must be an integer")

            if not isinstance(self.buffett_score, int):
                raise ValueError("buffett_score must be an integer")

            if not 0 <= self.buffett_score <= 100:
                raise ValueError("buffett_score must be between 0 and 100")

        object.__setattr__(self, "ticker", ticker)
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "grade", grade)
        object.__setattr__(self, "decision", decision)

    @classmethod
    def create(
        cls,
        ticker: str,
        mode: str,
        overall_score: int,
        grade: str,
        decision: str,
        buffett_score: Optional[int] = None,
        evaluated_at: Optional[str] = None,
    ) -> "ScoreSnapshot":
        """Create a snapshot using the current UTC time when omitted."""

        timestamp = evaluated_at

        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        return cls(
            ticker=ticker,
            evaluated_at=timestamp,
            mode=mode,
            overall_score=overall_score,
            grade=grade,
            decision=decision,
            buffett_score=buffett_score,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary."""

        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoreSnapshot":
        """Create a snapshot from a dictionary."""

        if not isinstance(data, dict):
            raise TypeError("ScoreSnapshot data must be a dictionary")

        required = {
            "ticker",
            "evaluated_at",
            "mode",
            "overall_score",
            "grade",
            "decision",
            "buffett_score",
        }

        missing = required.difference(data)
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"missing ScoreSnapshot fields: {missing_text}")

        return cls(
            ticker=data["ticker"],
            evaluated_at=data["evaluated_at"],
            mode=data["mode"],
            overall_score=data["overall_score"],
            grade=data["grade"],
            decision=data["decision"],
            buffett_score=data["buffett_score"],
        )