"""Sprint35 persistence layer tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from services.src.storage import JsonScoreStorage, ScoreSnapshot


def test_snapshot_round_trip() -> None:
    snapshot = ScoreSnapshot.create(
        ticker="AAPL",
        mode="full",
        overall_score=152,
        grade="A",
        decision="BUY",
        buffett_score=82,
        evaluated_at="2026-08-16T12:00:00+00:00",
    )

    restored = ScoreSnapshot.from_dict(snapshot.to_dict())

    assert restored == snapshot


def test_json_storage_save_and_load() -> None:
    with tempfile.TemporaryDirectory() as temporary_dir:
        storage = JsonScoreStorage(temporary_dir)

        first = ScoreSnapshot.create(
            ticker="AAPL",
            mode="full",
            overall_score=152,
            grade="A",
            decision="BUY",
            buffett_score=82,
            evaluated_at="2026-08-16T12:00:00+00:00",
        )

        second = ScoreSnapshot.create(
            ticker="AAPL",
            mode="full",
            overall_score=149,
            grade="A",
            decision="BUY",
            buffett_score=80,
            evaluated_at="2026-08-17T12:00:00+00:00",
        )

        storage.save(first)
        storage.save(second)

        history = storage.load_history("AAPL")

        assert len(history) == 2
        assert history[0] == first
        assert history[1] == second


def test_storage_creates_one_file_per_ticker() -> None:
    with tempfile.TemporaryDirectory() as temporary_dir:
        storage = JsonScoreStorage(temporary_dir)

        snapshot = ScoreSnapshot.create(
            ticker="7203",
            mode="full",
            overall_score=160,
            grade="S",
            decision="BUY",
            buffett_score=85,
        )

        storage.save(snapshot)

        expected = Path(temporary_dir) / "7203.json"

        assert expected.exists()

        with expected.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        assert len(payload) == 1
        assert payload[0]["ticker"] == "7203"


def test_invalid_snapshot_is_rejected() -> None:
    try:
        ScoreSnapshot(
            ticker="",
            evaluated_at="2026-08-16T12:00:00+00:00",
            mode="full",
            overall_score=100,
            grade="B",
            decision="WATCH",
            buffett_score=50,
        )
    except ValueError:
        return

    raise AssertionError("empty ticker must raise ValueError")


def test_portfolio_and_watchlist_are_not_part_of_snapshot() -> None:
    snapshot = ScoreSnapshot.create(
        ticker="MSFT",
        mode="full",
        overall_score=140,
        grade="A",
        decision="BUY",
        buffett_score=78,
    )

    data = snapshot.to_dict()

    assert "portfolio_risk" not in data
    assert "watchlist_insights" not in data
    assert "score" not in data
    assert "max_score" not in data

def test_snapshot_validates_design_values() -> None:
    try:
        ScoreSnapshot.create(
            ticker="AAPL",
            mode="invalid",
            overall_score=150,
            grade="A",
            decision="BUY",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("invalid mode must raise ValueError")

    try:
        ScoreSnapshot.create(
            ticker="AAPL",
            mode="full",
            overall_score=191,
            grade="A",
            decision="BUY",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("overall_score above 190 must raise ValueError")

    try:
        ScoreSnapshot.create(
            ticker="AAPL",
            mode="full",
            overall_score=150,
            grade="A",
            decision="INVALID",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("invalid decision must raise ValueError")