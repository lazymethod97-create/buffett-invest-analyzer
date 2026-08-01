def calculate_buffett_score(data: dict) -> dict:
    """バフェット流の採点を行う。100点満点。"""

    scores = []
    details = []

    # ── 1. ROE ── 20点
    roe = data.get("roe")
    if roe is not None:
        if roe >= 0.20:
            scores.append(20)
            details.append({"item": "ROE（自己資本利益率）", "value": f"{roe*100:.1f}%",
                             "score": 20, "max_score": 20, "passed": True,
                             "comment": "優秀。バフェットが最重視する指標です。"})
        elif roe >= 0.15:
            scores.append(12)
            details.append({"item": "ROE（自己資本利益率）", "value": f"{roe*100:.1f}%",
                             "score": 12, "max_score": 20, "passed": True,
                             "comment": "合格ライン。もう少し高いと理想的です。"})
        else:
            scores.append(0)
            details.append({"item": "ROE（自己資本利益率）", "value": f"{roe*100:.1f}%",
                             "score": 0, "max_score": 20, "passed": False,
                             "comment": "バフェット基準に届いていません。"})
    else:
        details.append({"item": "ROE（自己資本利益率）", "value": "データなし",
                         "score": 0, "max_score": 20, "passed": False,
                         "comment": "データを取得できませんでした。"})

    # ── 2. 営業利益率 ── 15点
    op = data.get("operating_margin")
    if op is not None:
        if op >= 0.20:
            scores.append(15); details.append({"item": "営業利益率", "value": f"{op*100:.1f}%",
                "score": 15, "max_score": 15, "passed": True, "comment": "高い競争優位性（経済的堀）があります。"})
        elif op >= 0.15:
            scores.append(10); details.append({"item": "営業利益率", "value": f"{op*100:.1f}%",
                "score": 10, "max_score": 15, "passed": True, "comment": "良好な水準です。"})
        elif op >= 0.10:
            scores.append(5); details.append({"item": "営業利益率", "value": f"{op*100:.1f}%",
                "score": 5, "max_score": 15, "passed": True, "comment": "業種によっては許容範囲です。"})
        else:
            scores.append(0); details.append({"item": "営業利益率", "value": f"{op*100:.1f}%",
                "score": 0, "max_score": 15, "passed": False, "comment": "収益性が低い。バフェットは敬遠します。"})
    else:
        details.append({"item": "営業利益率", "value": "データなし",
                         "score": 0, "max_score": 15, "passed": False, "comment": "データを取得できませんでした。"})

    # ── 3. 負債比率（D/E）── 15点
    de = data.get("debt_to_equity")
    if de is not None:
        if de > 100:  # yfinanceが%表記(150.0)で返す場合があるため補正
            de = de / 100
        if de <= 0.5:
            scores.append(15); details.append({"item": "負債比率（D/E）", "value": f"{de:.2f}",
                "score": 15, "max_score": 15, "passed": True, "comment": "財務が非常に健全です。"})
        elif de <= 1.0:
            scores.append(10); details.append({"item": "負債比率（D/E）", "value": f"{de:.2f}",
                "score": 10, "max_score": 15, "passed": True, "comment": "許容範囲内です。"})
        elif de <= 2.0:
            scores.append(5); details.append({"item": "負債比率（D/E）", "value": f"{de:.2f}",
                "score": 5, "max_score": 15, "passed": False, "comment": "やや負債が多い。注意が必要です。"})
        else:
            scores.append(0); details.append({"item": "負債比率（D/E）", "value": f"{de:.2f}",
                "score": 0, "max_score": 15, "passed": False, "comment": "負債が多すぎます。バフェットは避けます。"})
    else:
        details.append({"item": "負債比率（D/E）", "value": "データなし",
                         "score": 0, "max_score": 15, "passed": False, "comment": "データを取得できませんでした。"})

    # ── 4. PER ── 10点
    pe = data.get("pe_ratio")
    if pe is not None and pe > 0:
        if pe <= 15:
            scores.append(10); details.append({"item": "PER（株価収益率）", "value": f"{pe:.1f}倍",
                "score": 10, "max_score": 10, "passed": True, "comment": "割安水準。バフェットが好む価格帯です。"})
        elif pe <= 25:
            scores.append(7); details.append({"item": "PER（株価収益率）", "value": f"{pe:.1f}倍",
                "score": 7, "max_score": 10, "passed": True, "comment": "許容範囲。企業の質次第です。"})
        elif pe <= 35:
            scores.append(3); details.append({"item": "PER（株価収益率）", "value": f"{pe:.1f}倍",
                "score": 3, "max_score": 10, "passed": False, "comment": "やや割高。相応の成長が必要です。"})
        else:
            scores.append(0); details.append({"item": "PER（株価収益率）", "value": f"{pe:.1f}倍",
                "score": 0, "max_score": 10, "passed": False, "comment": "割高すぎます。"})
    else:
        details.append({"item": "PER（株価収益率）", "value": "データなし",
                         "score": 0, "max_score": 10, "passed": False, "comment": "赤字企業またはデータなし。"})

    # ── 5. フリーキャッシュフロー ── 15点
    fcf = data.get("free_cashflow")
    if fcf is not None:
        if fcf > 0:
            scores.append(15); details.append({"item": "フリーキャッシュフロー", "value": "プラス",
                "score": 15, "max_score": 15, "passed": True, "comment": "実際に現金を生み出しています。"})
        else:
            scores.append(0); details.append({"item": "フリーキャッシュフロー", "value": "マイナス",
                "score": 0, "max_score": 15, "passed": False, "comment": "現金を消費しています。"})
    else:
        details.append({"item": "フリーキャッシュフロー", "value": "データなし",
                         "score": 0, "max_score": 15, "passed": False, "comment": "データを取得できませんでした。"})

    # ── 6. 売上成長率 ── 10点
    rg = data.get("revenue_growth")
    if rg is not None:
        if rg >= 0.10:
            scores.append(10); details.append({"item": "売上成長率", "value": f"{rg*100:.1f}%",
                "score": 10, "max_score": 10, "passed": True, "comment": "力強い成長です。"})
        elif rg >= 0.05:
            scores.append(7); details.append({"item": "売上成長率", "value": f"{rg*100:.1f}%",
                "score": 7, "max_score": 10, "passed": True, "comment": "安定した成長です。"})
        elif rg >= 0:
            scores.append(3); details.append({"item": "売上成長率", "value": f"{rg*100:.1f}%",
                "score": 3, "max_score": 10, "passed": True, "comment": "成長は緩やか。横ばいです。"})
        else:
            scores.append(0); details.append({"item": "売上成長率", "value": f"{rg*100:.1f}%",
                "score": 0, "max_score": 10, "passed": False, "comment": "売上が減少しています。"})
    else:
        details.append({"item": "売上成長率", "value": "データなし",
                         "score": 0, "max_score": 10, "passed": False, "comment": "データを取得できませんでした。"})

    # ── 7. PBR ── 10点
    pb = data.get("pb_ratio")
    if pb is not None and pb > 0:
        if pb <= 1.5:
            scores.append(10); details.append({"item": "PBR（株価純資産倍率）", "value": f"{pb:.2f}倍",
                "score": 10, "max_score": 10, "passed": True, "comment": "資産に対して割安です。"})
        elif pb <= 3.0:
            scores.append(7); details.append({"item": "PBR（株価純資産倍率）", "value": f"{pb:.2f}倍",
                "score": 7, "max_score": 10, "passed": True, "comment": "許容範囲です。"})
        elif pb <= 5.0:
            scores.append(3); details.append({"item": "PBR（株価純資産倍率）", "value": f"{pb:.2f}倍",
                "score": 3, "max_score": 10, "passed": False, "comment": "やや割高ですが、高ROEなら許容できます。"})
        else:
            scores.append(0); details.append({"item": "PBR（株価純資産倍率）", "value": f"{pb:.2f}倍",
                "score": 0, "max_score": 10, "passed": False, "comment": "割高すぎます。"})
    else:
        details.append({"item": "PBR（株価純資産倍率）", "value": "データなし",
                         "score": 0, "max_score": 10, "passed": False, "comment": "データを取得できませんでした。"})

    # ── 8. ROA ── 5点
    roa = data.get("roa")
    if roa is not None:
        if roa >= 0.10:
            scores.append(5); details.append({"item": "ROA（総資産利益率）", "value": f"{roa*100:.1f}%",
                "score": 5, "max_score": 5, "passed": True, "comment": "資産を効率的に活用しています。"})
        elif roa >= 0.05:
            scores.append(3); details.append({"item": "ROA（総資産利益率）", "value": f"{roa*100:.1f}%",
                "score": 3, "max_score": 5, "passed": True, "comment": "普通の水準です。"})
        else:
            scores.append(0); details.append({"item": "ROA（総資産利益率）", "value": f"{roa*100:.1f}%",
                "score": 0, "max_score": 5, "passed": False, "comment": "資産効率が低い。"})
    else:
        details.append({"item": "ROA（総資産利益率）", "value": "データなし",
                         "score": 0, "max_score": 5, "passed": False, "comment": "データを取得できませんでした。"})

    total_score = sum(scores)

    if total_score >= 75:
        verdict, color, comment = "✅ 投資推奨", "green", "バフェット基準を高水準でクリアしています。長期投資の有力候補です。"
    elif total_score >= 55:
        verdict, color, comment = "🟡 条件付き検討", "orange", "一部の基準を満たしています。追加調査の上で判断してください。"
    elif total_score >= 35:
        verdict, color, comment = "⚠️ 要注意", "red", "バフェット基準を多く下回っています。慎重に検討してください。"
    else:
        verdict, color, comment = "❌ 投資非推奨", "darkred", "バフェット基準を大きく下回っています。現時点では推奨しません。"

    return {
        "total_score": total_score,
        "max_score": 100,
        "verdict": verdict,
        "verdict_color": color,
        "verdict_comment": comment,
        "details": details,
    }
