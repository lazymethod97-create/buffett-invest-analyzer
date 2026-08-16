"""Sprint37 tests: score history chart (ScoreSnapshot list -> plotly Figure)."""

from __future__ import annotations

from services.src.report.report import create_score_history_chart
from services.src.storage import ScoreSnapshot


def _snapshot(overall_score: int, evaluated_at: str, grade: str = "A", decision: str = "BUY", mode: str = "full") -> ScoreSnapshot:
    return ScoreSnapshot.create(
        ticker="AAPL",
        mode=mode,
        overall_score=overall_score,
        grade=grade,
        decision=decision,
        buffett_score=80,
        evaluated_at=evaluated_at,
    )


def test_empty_history_returns_empty_figure() -> None:
    fig = create_score_history_chart([])

    assert len(fig.data) == 0


def test_chart_plots_overall_score_over_time() -> None:
    history = [
        _snapshot(120, "2026-08-01T09:00:00+00:00", grade="B", decision="WATCH"),
        _snapshot(150, "2026-08-10T09:00:00+00:00", grade="A", decision="BUY"),
    ]

    fig = create_score_history_chart(history)

    assert len(fig.data) == 1
    trace = fig.data[0]
    assert list(trace.x) == ["2026-08-01T09:00:00+00:00", "2026-08-10T09:00:00+00:00"]
    assert list(trace.y) == [120, 150]


def test_chart_hover_text_includes_grade_decision_mode() -> None:
    history = [_snapshot(160, "2026-08-16T09:00:00+00:00", grade="S", decision="BUY", mode="full")]

    fig = create_score_history_chart(history)

    trace = fig.data[0]
    assert "S" in trace.text[0]
    assert "BUY" in trace.text[0]
    assert "full" in trace.text[0]


def test_chart_yaxis_fixed_to_190_point_scale() -> None:
    history = [_snapshot(80, "2026-08-16T09:00:00+00:00", grade="D", decision="PASS")]

    fig = create_score_history_chart(history)

    assert list(fig.layout.yaxis.range) == [0, 190]
