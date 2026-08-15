"""
overall_eval.py (Sprint18)

Buffett Investment Analyzer の総合評価エンジン

役割
---------------------------------
・Buffett Score
・DCF
・MOAT
・ブランド
・経営者
・Red Team

を統合して

Overall Grade(S〜D)
Overall Score(100点)
Risk Level
Confidence
Action
Decision(BUY / WATCH / PASS)

を返す。
AIは使用しない。

総合判定（BUY / WATCH / PASS）はこのモジュールだけで決定する（ルール13）。
"""

from typing import Dict


def _score_buffett(score: float) -> int:
    if score >= 90:
        return 40
    elif score >= 80:
        return 35
    elif score >= 70:
        return 30
    elif score >= 60:
        return 20
    elif score >= 50:
        return 10
    return 0


def _score_dcf(margin: float) -> int:
    if margin >= 30:
        return 20
    elif margin >= 15:
        return 15
    elif margin >= 0:
        return 10
    elif margin >= -20:
        return 5
    return 0


def _score_moat(moat: Dict) -> int:
    rating = moat.get("rating", "").lower()

    if rating == "wide":
        return 15

    if rating == "narrow":
        return 10

    return 0


def _score_brand(brand: Dict) -> int:
    stars = brand.get("stars", 0)
    return min(stars * 2, 10)


def _score_management(mgmt: Dict) -> int:
    stars = mgmt.get("stars", 0)
    return min(stars * 2, 10)


def _score_redteam(red_team: Dict) -> int:

    text = (
        red_team.get("conclusion", "")
        + red_team.get("summary", "")
    ).lower()

    if "重大" in text:
        return 0

    if "注意" in text:
        return 2

    return 5


def _score_roic(roic: Dict) -> int:
    """Sprint19: ROICスコア（15点満点）"""
    score = roic.get("score", 0) if roic else 0
    return min(score, 15)


def _score_owner_earnings(owner_earnings: Dict) -> int:
    """Sprint20: Owner Earningsスコア（10点満点）"""
    score = owner_earnings.get("score", 0) if owner_earnings else 0
    return min(score, 10)


def _score_intrinsic_value(intrinsic_value: Dict) -> int:
    """Sprint21: Intrinsic Valueスコア（15点満点）"""
    score = intrinsic_value.get("score", 0) if intrinsic_value else 0
    return min(score, 15)


def _score_capital_allocation(capital_allocation: Dict) -> int:
    """Sprint22: Capital Allocationスコア（10点満点）"""
    score = capital_allocation.get("score", 0) if capital_allocation else 0
    return min(score, 10)


def _score_share_buyback(share_buyback: Dict) -> int:
    """Sprint23: Share Buybackスコア（10点満点）"""
    score = share_buyback.get("score", 0) if share_buyback else 0
    return min(score, 10)


def _score_debt_quality(debt_quality: Dict) -> int:
    """Sprint24: Debt Qualityスコア（10点満点）"""
    score = debt_quality.get("score", 0) if debt_quality else 0
    return min(score, 10)


def _score_moat_strength(moat_strength: Dict) -> int:
    """Sprint25: Economic Moat強化スコア（10点満点）"""
    score = moat_strength.get("score", 0) if moat_strength else 0
    return min(score, 10)


def _score_backtest(backtest: Dict) -> int:
    """Sprint26: Backtestスコア（10点満点）"""
    score = backtest.get("score", 0) if backtest else 0
    return min(score, 10)


def _grade(score):
    """
    Sprint26: 190点満点（Buffett40+DCF20+MOAT15+ブランド10+経営者10
    +RedTeam5+ROIC15+OwnerEarnings10+IntrinsicValue15+CapitalAllocation10
    +ShareBuyback10+DebtQuality10+EconomicMoat強化10+Backtest10）に合わせた判定基準。
    """

    if score >= 167:
        return "S"

    if score >= 138:
        return "A"

    if score >= 115:
        return "B"

    if score >= 92:
        return "C"

    return "D"


def _stars(score):

    if score >= 167:
        return 5

    if score >= 138:
        return 4

    if score >= 115:
        return 3

    if score >= 92:
        return 2

    return 1


def _risk(redteam_score):

    if redteam_score == 5:
        return "Low"

    if redteam_score >= 2:
        return "Medium"

    return "High"


def _confidence(buffett_score):

    if buffett_score >= 85:
        return "High"

    if buffett_score >= 70:
        return "Medium"

    return "Low"


def _action(grade):

    if grade == "S":
        return "積極的に投資候補"

    if grade == "A":
        return "買い候補"

    if grade == "B":
        return "監視継続"

    if grade == "C":
        return "慎重に様子見"

    return "見送り"


def _decision(grade, risk):
    """
    Sprint18: 総合判定 BUY / WATCH / PASS はここだけで決定する。
    - S または A かつ リスクが High でない → BUY
    - B かつ リスクが High でない          → WATCH
    - それ以外                             → PASS
    """

    if grade in ("S", "A") and risk != "High":
        return "BUY"

    if grade == "B" and risk != "High":
        return "WATCH"

    return "PASS"


def _apply_news_risk(decision, grade, news_impact):
    """
    Sprint34-4: 190点満点のスコアは変更せず、重大かつ信頼度の高い
    ネガティブニュースだけで最終Decisionを一段階下げる。

    ニュースが無い・AI失敗・confidence不足・severity不足の場合は
    既存判定をそのまま返す。ニュースでBUYへ昇格させることもしない。
    """
    if not news_impact or not news_impact.get("available"):
        return decision, False

    if (
        news_impact.get("impact") == "negative"
        and news_impact.get("severity") == "high"
        and news_impact.get("confidence") == "high"
    ):
        if decision == "BUY":
            return "WATCH", True
        if decision == "WATCH":
            return "PASS", True

    return decision, False


def calculate_overall_grade(
    score_result,
    dcf_result,
    moat,
    brand,
    mgmt,
    red_team,
    roic=None,
    owner_earnings=None,
    intrinsic_value=None,
    capital_allocation=None,
    share_buyback=None,
    debt_quality=None,
    moat_strength=None,
    backtest=None,
    news_impact=None,
):

    buffett_score = score_result["total_score"]

    dcf_margin = 0

    if dcf_result.get("success"):
        dcf_margin = dcf_result["margin_of_safety_pct"]

    s1 = _score_buffett(buffett_score)
    s2 = _score_dcf(dcf_margin)
    s3 = _score_moat(moat)
    s4 = _score_brand(brand)
    s5 = _score_management(mgmt)
    s6 = _score_redteam(red_team)
    s7 = _score_roic(roic) if roic else 0
    s8 = _score_owner_earnings(owner_earnings) if owner_earnings else 0
    s9 = _score_intrinsic_value(intrinsic_value) if intrinsic_value else 0
    s10 = _score_capital_allocation(capital_allocation) if capital_allocation else 0
    s11 = _score_share_buyback(share_buyback) if share_buyback else 0
    s12 = _score_debt_quality(debt_quality) if debt_quality else 0
    s13 = _score_moat_strength(moat_strength) if moat_strength else 0
    s14 = _score_backtest(backtest) if backtest else 0

    total = s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9 + s10 + s11 + s12 + s13 + s14

    grade = _grade(total)

    risk = _risk(s6)
    base_decision = _decision(grade, risk)
    decision, news_adjusted = _apply_news_risk(
        base_decision, grade, news_impact or {}
    )

    action = _action(grade)
    if news_adjusted:
        action = (
            "ニュース重大リスクを考慮し様子見"
            if decision == "WATCH"
            else "ニュース重大リスクを考慮し見送り"
        )

    return {

        "overall_score": total,

        "grade": grade,

        "stars": _stars(total),

        "risk": risk,

        "confidence": _confidence(buffett_score),

        "action": action,

        "decision": decision,

        "base_decision": base_decision,

        "news_adjusted": news_adjusted,

        "news_impact": news_impact or {},

        "detail":{

            "buffett":s1,

            "dcf":s2,

            "moat":s3,

            "brand":s4,

            "management":s5,

            "redteam":s6,
            "roic":s7,
            "owner_earnings":s8,
            "intrinsic_value":s9,
            "capital_allocation":s10,
            "share_buyback":s11,
            "debt_quality":s12,
            "moat_strength":s13,
            "backtest":s14,

        }

    }

