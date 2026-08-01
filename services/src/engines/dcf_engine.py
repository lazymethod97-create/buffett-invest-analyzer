"""
DCF（ディスカウント・キャッシュフロー）分析モジュール（Sprint9）
フリーキャッシュフローを将来に投影し、現在価値に割り引いて
理論株価（Intrinsic Value）を算出する。
すべてルールベースの計算のみで、AIは使用しない。
"""

from typing import Dict, Any, Optional


def calculate_dcf(
    data: Dict[str, Any],
    growth_rate: Optional[float] = None,
    discount_rate: float = 0.10,
    terminal_growth: float = 0.025,
    projection_years: int = 5,
) -> Dict[str, Any]:
    """
    シンプルなDCFモデルで理論株価を算出する。

    引数
    ----
    data: get_stock_data() が返す企業データ辞書
          （free_cashflow, market_cap, current_price を使用）
    growth_rate: FCFの年平均成長率（未指定時は revenue_growth を参考に自動設定）
    discount_rate: 割引率（WACCの簡易代用値。デフォルト10%）
    terminal_growth: 永久成長率（デフォルト2.5%）
    projection_years: 予測年数（デフォルト5年）

    戻り値
    ----
    成功時: success=True, projections, intrinsic_value_per_share,
            current_price, margin_of_safety_pct, verdict などを含む辞書
    失敗時: success=False, error（データ不足・計算不能の理由）
    """
    free_cashflow = data.get("free_cashflow")
    market_cap = data.get("market_cap")
    current_price = data.get("current_price")

    # 必須データの検証
    if not free_cashflow or free_cashflow <= 0:
        return {
            "success": False,
            "error": "フリーキャッシュフローがマイナス、またはデータがないためDCF評価できません。",
        }
    if not market_cap or not current_price or current_price <= 0:
        return {
            "success": False,
            "error": "時価総額または株価データが不足しているためDCF評価できません。",
        }

    # 発行済株式数を時価総額と株価から逆算（簡易近似）
    shares_outstanding = market_cap / current_price
    if shares_outstanding <= 0:
        return {
            "success": False,
            "error": "発行済株式数を算出できませんでした。",
        }

    fcf_per_share = free_cashflow / shares_outstanding

    # 成長率の自動設定（未指定時）
    if growth_rate is None:
        rg = data.get("revenue_growth")
        if rg is None:
            growth_rate = 0.05
        else:
            # 極端な値は5%〜15%にクリップして保守的に見積もる
            growth_rate = max(0.05, min(rg, 0.15))

    # 割引率は永久成長率より必ず大きくする（数式破綻防止）
    if discount_rate <= terminal_growth:
        discount_rate = terminal_growth + 0.01

    # 将来FCFを予測し、現在価値に割り引く
    projections = []
    discounted_sum = 0.0
    fcf = fcf_per_share
    for year in range(1, projection_years + 1):
        fcf = fcf * (1 + growth_rate)
        discount_factor = (1 + discount_rate) ** year
        pv = fcf / discount_factor
        discounted_sum += pv
        projections.append({
            "year": year,
            "fcf_per_share": fcf,
            "present_value": pv,
        })

    # ターミナルバリュー（Gordon Growth Model）
    terminal_fcf = fcf * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)
    terminal_value_pv = terminal_value / ((1 + discount_rate) ** projection_years)

    intrinsic_value_per_share = discounted_sum + terminal_value_pv

    margin_of_safety_pct = (
        (intrinsic_value_per_share - current_price) / current_price * 100
    )

    if margin_of_safety_pct >= 30:
        verdict = "🟢 大幅に割安（安全余裕30%以上）"
    elif margin_of_safety_pct >= 0:
        verdict = "🟡 やや割安〜適正水準"
    elif margin_of_safety_pct >= -20:
        verdict = "🟠 やや割高"
    else:
        verdict = "🔴 大幅に割高（安全余裕なし）"

    return {
        "success": True,
        "assumptions": {
            "growth_rate": growth_rate,
            "discount_rate": discount_rate,
            "terminal_growth": terminal_growth,
            "projection_years": projection_years,
        },
        "fcf_per_share_base": fcf_per_share,
        "shares_outstanding": shares_outstanding,
        "projections": projections,
        "terminal_value_pv": terminal_value_pv,
        "intrinsic_value_per_share": intrinsic_value_per_share,
        "current_price": current_price,
        "margin_of_safety_pct": margin_of_safety_pct,
        "verdict": verdict,
    }
