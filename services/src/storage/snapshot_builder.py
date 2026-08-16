"""Sprint36: Build ScoreSnapshot instances from create_analysis_bundle() output.

This module keeps app.py a thin controller (PROJECT_RULES.md Rule 4) by moving
the "UI mode label -> storage mode" mapping and ScoreSnapshot construction
logic out of app.py and into the storage package, next to the models it
produces.

This module does not know about Streamlit, analysis_bundle, or overall_eval
internals beyond the plain dict shapes they already return. It only maps
those shapes onto ScoreSnapshot.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .models import ScoreSnapshot


def resolve_snapshot_mode(mode_label: str) -> str:
    """Map app.py's analysis-mode radio label to storage's mode value.

    app.py's analysis_mode is one of:
        "⚡ クイック（財務スコアのみ）"
        "📊 標準（+AI定性分析・要約）"
        "🔎 フル（すべて）"

    ScoreSnapshot only accepts "quick" / "standard" / "full" (models.py).
    """

    label = str(mode_label)

    if label.startswith("⚡"):
        return "quick"
    if label.startswith("🔎"):
        return "full"
    return "standard"


def build_score_snapshot(
    ticker: str,
    mode_label: str,
    overall: Dict[str, Any],
    score_result: Optional[Dict[str, Any]] = None,
) -> ScoreSnapshot:
    """Build one ScoreSnapshot from a single create_analysis_bundle() run.

    Parameters
    ----------
    ticker:
        The ticker that was analyzed (e.g. data["ticker"]).
    mode_label:
        app.py's analysis_mode radio value (see resolve_snapshot_mode).
    overall:
        bundle["overall"], i.e. the dict returned by
        overall_eval.calculate_overall_grade(). Must contain
        "overall_score" / "grade" / "decision".
    score_result:
        calculate_buffett_score()'s return value, used only to fill the
        optional buffett_score (0-100) field. Safe to omit or pass {}.

    This function does not persist anything; call JsonScoreStorage.save()
    with the returned ScoreSnapshot to do that.
    """

    score_result = score_result or {}

    buffett_score = score_result.get("total_score")
    if isinstance(buffett_score, bool) or not isinstance(buffett_score, int):
        # ScoreSnapshot.buffett_score is optional (Sprint35 design). Rather
        # than raising here for an unexpected/missing shape, omit it -
        # overall_score/grade/decision are the fields that matter for
        # history (docs/DESIGN_HISTORY_AND_SCREENING.md 原則D).
        buffett_score = None

    return ScoreSnapshot.create(
        ticker=ticker,
        mode=resolve_snapshot_mode(mode_label),
        overall_score=overall["overall_score"],
        grade=overall["grade"],
        decision=overall["decision"],
        buffett_score=buffett_score,
    )
