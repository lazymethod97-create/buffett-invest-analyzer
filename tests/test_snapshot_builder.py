"""Sprint36 snapshot_builder tests (analysis_bundle output -> ScoreSnapshot)."""

from __future__ import annotations

from services.src.storage import build_score_snapshot, resolve_snapshot_mode


def test_resolve_snapshot_mode_quick() -> None:
    assert resolve_snapshot_mode("⚡ クイック（財務スコアのみ）") == "quick"


def test_resolve_snapshot_mode_standard() -> None:
    assert resolve_snapshot_mode("📊 標準（+AI定性分析・要約）") == "standard"


def test_resolve_snapshot_mode_full() -> None:
    assert resolve_snapshot_mode("🔎 フル（すべて）") == "full"


def test_build_score_snapshot_from_bundle_overall() -> None:
    overall = {
        "overall_score": 152,
        "grade": "A",
        "decision": "BUY",
        "risk": "low",
        "action": "買い",
    }
    score_result = {"total_score": 82}

    snapshot = build_score_snapshot(
        ticker="AAPL",
        mode_label="🔎 フル（すべて）",
        overall=overall,
        score_result=score_result,
    )

    assert snapshot.ticker == "AAPL"
    assert snapshot.mode == "full"
    assert snapshot.overall_score == 152
    assert snapshot.grade == "A"
    assert snapshot.decision == "BUY"
    assert snapshot.buffett_score == 82


def test_build_score_snapshot_without_score_result() -> None:
    overall = {"overall_score": 60, "grade": "D", "decision": "PASS"}

    # score_result省略時（Noneでも{}相当として扱われる）、buffett_scoreはNoneになる。
    snapshot = build_score_snapshot(
        ticker="7203",
        mode_label="⚡ クイック（財務スコアのみ）",
        overall=overall,
        score_result=None,
    )

    assert snapshot.mode == "quick"
    assert snapshot.buffett_score is None


def test_build_score_snapshot_ignores_non_int_total_score() -> None:
    # scoring_engine側の異常値混入で万一total_scoreが数値以外になっても、
    # overall_score/grade/decisionの保存自体は落とさない（buffett_scoreのみ省略）。
    overall = {"overall_score": 100, "grade": "B", "decision": "WATCH"}
    score_result = {"total_score": "N/A"}

    snapshot = build_score_snapshot(
        ticker="MSFT",
        mode_label="📊 標準（+AI定性分析・要約）",
        overall=overall,
        score_result=score_result,
    )

    assert snapshot.buffett_score is None
    assert snapshot.overall_score == 100
