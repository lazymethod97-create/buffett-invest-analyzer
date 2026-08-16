"""Sprint38 tests: score comparison display (previous vs current ScoreSnapshot -> markdown)."""

from __future__ import annotations

from services.src.report.report import create_score_comparison_display
from services.src.storage import ScoreSnapshot


def _snapshot(
    overall_score: int,
    evaluated_at: str,
    grade: str = "A",
    decision: str = "BUY",
    mode: str = "full",
    buffett_score: int = 80,
) -> ScoreSnapshot:
    return ScoreSnapshot.create(
        ticker="AAPL",
        mode=mode,
        overall_score=overall_score,
        grade=grade,
        decision=decision,
        buffett_score=buffett_score,
        evaluated_at=evaluated_at,
    )


def test_less_than_two_snapshots_returns_no_comparison_message() -> None:
    result_empty = create_score_comparison_display([])
    result_one = create_score_comparison_display(
        [_snapshot(150, "2026-08-16T09:00:00+00:00")]
    )

    assert "比較対象となる過去の記録がありません" in result_empty
    assert "比較対象となる過去の記録がありません" in result_one


def test_score_increase_is_reported_with_up_arrow() -> None:
    history = [
        _snapshot(120, "2026-08-01T09:00:00+00:00", grade="B", decision="WATCH"),
        _snapshot(150, "2026-08-10T09:00:00+00:00", grade="A", decision="BUY"),
    ]

    result = create_score_comparison_display(history)

    assert "+30点" in result
    assert "⬆️" in result


def test_score_decrease_is_reported_with_down_arrow() -> None:
    history = [
        _snapshot(150, "2026-08-01T09:00:00+00:00"),
        _snapshot(130, "2026-08-10T09:00:00+00:00"),
    ]

    result = create_score_comparison_display(history)

    assert "-20点" in result
    assert "⬇️" in result


def test_unchanged_score_is_reported_as_flat() -> None:
    history = [
        _snapshot(150, "2026-08-01T09:00:00+00:00"),
        _snapshot(150, "2026-08-10T09:00:00+00:00"),
    ]

    result = create_score_comparison_display(history)

    assert "±0点" in result
    assert "➡️" in result


def test_grade_and_decision_change_are_reported() -> None:
    history = [
        _snapshot(115, "2026-08-01T09:00:00+00:00", grade="B", decision="WATCH"),
        _snapshot(140, "2026-08-10T09:00:00+00:00", grade="A", decision="BUY"),
    ]

    result = create_score_comparison_display(history)

    assert "グレード変化:** B → A" in result
    assert "判定変化:** WATCH → BUY" in result


def test_no_grade_or_decision_change_reports_unchanged() -> None:
    history = [
        _snapshot(140, "2026-08-01T09:00:00+00:00", grade="A", decision="BUY"),
        _snapshot(145, "2026-08-10T09:00:00+00:00", grade="A", decision="BUY"),
    ]

    result = create_score_comparison_display(history)

    assert "グレード変化:** 変化なし（A）" in result
    assert "判定変化:** 変化なし（BUY）" in result


def test_buffett_score_diff_is_reported_when_both_present() -> None:
    history = [
        _snapshot(140, "2026-08-01T09:00:00+00:00", buffett_score=70),
        _snapshot(150, "2026-08-10T09:00:00+00:00", buffett_score=85),
    ]

    result = create_score_comparison_display(history)

    assert "Buffett Score差分:** +15点" in result
    assert "前回 70 → 今回 85" in result


def test_mode_mismatch_adds_caution_note() -> None:
    history = [
        _snapshot(120, "2026-08-01T09:00:00+00:00", mode="quick"),
        _snapshot(150, "2026-08-10T09:00:00+00:00", mode="full"),
    ]

    result = create_score_comparison_display(history)

    assert "注意" in result
    assert "quick → full" in result


def test_same_mode_has_no_caution_note() -> None:
    history = [
        _snapshot(120, "2026-08-01T09:00:00+00:00", mode="full"),
        _snapshot(150, "2026-08-10T09:00:00+00:00", mode="full"),
    ]

    result = create_score_comparison_display(history)

    assert "注意" not in result


def test_uses_only_the_two_most_recent_snapshots() -> None:
    history = [
        _snapshot(80, "2026-07-01T09:00:00+00:00", grade="D", decision="PASS"),
        _snapshot(120, "2026-08-01T09:00:00+00:00", grade="B", decision="WATCH"),
        _snapshot(150, "2026-08-10T09:00:00+00:00", grade="A", decision="BUY"),
    ]

    result = create_score_comparison_display(history)

    assert "+30点" in result
    assert "グレード変化:** B → A" in result
    assert "80点" not in result
