"""
Intrinsic Value（内在価値）計算エンジン（Sprint21）

バフェットの「価格はあなたが払うもの、価値はあなたが得るもの」に基づき、
複数の評価方式のコンセンサスから内在価値を算出する。

方式1: DCF（フリーキャッシュフロー割引）     重み 40%
       既存の dcf_engine.calculate_dcf() を利用
方式2: Owner Earnings方式                    重み 30%
       Sprint20の owner_earnings_engine を利用し、簡易2段階成長で割引
方式3: Earnings Power方式（収益還元）        重み 30%
       当期純利益 × バフェット基準の保守的PER（デフォルト12倍）

データ不足の方式はスキップし、利用可能な方式のみで重みを再正規化する。
すべてルールベース。AIは使用しない。
"""

from typing import Dict, Any, List, Optional
from .dcf_engine import calculate_dcf
from .owner_earnings_engine import calculate_owner_earnings


DEFAULT_FAIR_PE = 12.0          # 保守的な適正PER（バフェット基準）
DEFAULT_DISCOUNT_RATE = 0.10    # 割引率（WACC簡易代用）
DEFAULT_OE_GROWTH = 0.05        # Owner Earnings成長率（保守的）
DEFAULT_TERMINAL_GROWTH = 0.025 # 永久成長率


def _weighted_average(estimates: List[Dict[str, Any]]) -> Optional[float]:
    """各方式の推定値を重み付き平均する。"""
    total_weight = sum(e["weight"] for e in estimates)
    if total_weight <= 0:
        return None
    total_value = sum(e["value"] * e["weight"] for e in estimates)
    return total_value / total_weight


def calculate_intrinsic_value(
    data: Dict[str, Any],
    dcf_result: Optional[Dict[str, Any]] = None,
    owner_earnings_result: Optional[Dict[str, Any]] = None,
    fair_pe: float = DEFAULT_FAIR_PE,
    discount_rate: float = DEFAULT_DISCOUNT_RATE,
    oe_growth: float = DEFAULT_OE_GROWTH,
    terminal_growth: float = DEFAULT_TERMINAL_GROWTH,
    projection_years: int = 5,
) -> Dict[str, Any]:
    """
    複数方式でIntrinsic Valueを算出し、コンセンサスを返す。

    引数
    ----
    data: get_stock_data() が返す企業データ辞書
    dcf_result: 既存DCF計算結果（省略時は内部でdcf_engineを呼ぶ）
    owner_earnings_result: OE計算結果（省略時は内部でowner_earnings_engineを呼ぶ）
    fair_pe: Earnings Power方式で使用する適正PER
    discount_rate: 割引率
    oe_growth: Owner Earningsの成長率（2段階成長の前半）
    terminal_growth: 永久成長率
    projection_years: 予測年数

    戻り値
    ----
    成功時: success=True, estimates, consensus_intrinsic_value_per_share,
            current_price, margin_of_safety_pct, rating, summary, verdict
    失敗時: success=False, error（データ不足の理由）
    """
    current_price = data.get("current_price")
    market_cap = data.get("market_cap")
    shares_outstanding = data.get("shares_outstanding") or (
        market_cap / current_price if market_cap and current_price else None
    )

    # --- 方式1: DCF（FCF割引）---
    dcf = dcf_result or calculate_dcf(
        data,
        discount_rate=discount_rate,
        terminal_growth=terminal_growth,
        projection_years=projection_years,
    )
    estimates: List[Dict[str, Any]] = []
    if dcf.get("success") and dcf.get("intrinsic_value_per_share"):
        estimates.append({
            "method": "dcf",
            "label": "DCF（FCF割引）",
            "value": dcf["intrinsic_value_per_share"],
            "weight": 0.4,
            "detail": (
                f"FCF 1株 {dcf.get('fcf_per_share_base', 0):,.2f} を "
                f"{dcf.get('assumptions', {}).get('growth_rate', 0) * 100:.1f}% 成長で割引"
            ),
        })

    # --- 方式2: Owner Earnings方式 ---
    oe = owner_earnings_result or calculate_owner_earnings(data)
    oe_value = oe.get("owner_earnings")
    if oe_value is not None and oe_value > 0 and shares_outstanding and shares_outstanding > 0:
        oe_per_share = oe_value / shares_outstanding
        pv_sum = 0.0
        oe_f = oe_per_share
        for year in range(1, projection_years + 1):
            oe_f = oe_f * (1 + oe_growth)
            pv_sum += oe_f / ((1 + discount_rate) ** year)
        terminal_oe = oe_f * (1 + terminal_growth)
        terminal_pv = (
            terminal_oe
            / (discount_rate - terminal_growth)
            / ((1 + discount_rate) ** projection_years)
        )
        oe_intrinsic = pv_sum + terminal_pv
        estimates.append({
            "method": "owner_earnings",
            "label": "Owner Earnings方式",
            "value": oe_intrinsic,
            "weight": 0.3,
            "detail": f"OE 1株 {oe_per_share:,.2f} を {oe_growth * 100:.1f}% 成長で割引",
        })

    # --- 方式3: Earnings Power方式（収益還元）---
    net_income = data.get("net_income")
    if net_income is not None and net_income > 0 and shares_outstanding and shares_outstanding > 0:
        eps = net_income / shares_outstanding
        ep_value = eps * fair_pe
        estimates.append({
            "method": "earnings_power",
            "label": "Earnings Power方式",
            "value": ep_value,
            "weight": 0.3,
            "detail": f"純利益 1株 {eps:,.2f} × 適正PER {fair_pe:.1f}倍",
        })

    if not estimates:
        return {
            "success": False,
            "error": "内在価値を計算するためのデータが不足しています（FCF / Owner Earnings / 純利益が必要）。",
        }
    if not current_price or current_price <= 0:
        return {
            "success": False,
            "error": "現在株価が不明なため安全余裕を計算できません。",
        }

    consensus = _weighted_average(estimates)
    if consensus is None or consensus <= 0:
        return {
            "success": False,
            "error": "内在価値を算出できませんでした。",
        }

    margin_of_safety_pct = (consensus - current_price) / current_price * 100

    # --- 判定 ---
    if margin_of_safety_pct >= 30:
        rating = "excellent"
        summary = f"安全余裕{margin_of_safety_pct:.0f}%以上。大幅に割安です。"
        verdict = "Excellent（大幅割安）"
    elif margin_of_safety_pct >= 15:
        rating = "good"
        summary = f"安全余裕{margin_of_safety_pct:.0f}%。良好な割安水準です。"
        verdict = "Good（割安）"
    elif margin_of_safety_pct >= 0:
        rating = "fair"
        summary = "内在価値と現在価格はほぼ均衡しています。"
        verdict = "Fair（適正）"
    elif margin_of_safety_pct >= -20:
        rating = "overvalued"
        summary = "現在価格が内在価値を上回っています。"
        verdict = "Overvalued（やや割高）"
    else:
        rating = "significantly_overvalued"
        summary = "現在価格が内在価値を大きく上回っています。"
        verdict = "Significantly Overvalued（大幅割高）"

    return {
        "success": True,
        "estimates": estimates,
        "consensus_intrinsic_value_per_share": consensus,
        "current_price": current_price,
        "shares_outstanding": shares_outstanding,
        "margin_of_safety_pct": margin_of_safety_pct,
        "fair_pe_used": fair_pe,
        "discount_rate": discount_rate,
        "oe_growth": oe_growth,
        "terminal_growth": terminal_growth,
        "projection_years": projection_years,
        "rating": rating,
        "summary": summary,
        "verdict": verdict,
        "warnings": [],
    }
