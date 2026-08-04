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


def _grade(score):
    """
    Sprint21: 140点満点（Buffett40+DCF20+MOAT15+ブランド10+経営者10
    +RedTeam5+ROIC15+OwnerEarnings10+IntrinsicValue15）に合わせた判定基準。
    """

    if score >= 122:
        return "S"

    if score >= 103:
        return "A"

    if score >= 85:
        return "B"

    if score >= 67:
        return "C"

    return "D"


def _stars(score):

    if score >= 122:
        return 5

    if score >= 103:
        return 4

    if score >= 85:
        return 3

    if score >= 67:
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

    total = s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9

    grade = _grade(total)

    risk = _risk(s6)

    return {

        "overall_score": total,

        "grade": grade,

        "stars": _stars(total),

        "risk": risk,

        "confidence": _confidence(buffett_score),

        "action": _action(grade),

        "decision": _decision(grade, risk),

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

        }

    }

