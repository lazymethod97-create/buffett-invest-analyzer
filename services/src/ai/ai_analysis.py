import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

from engines.checklist_engine import generate_buffett_checklist_rule

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_ai_analysis(data, score_result):
    """
    GEMINI APIが設定されていればgeminiで分析、
    設定されていなければルールベース分析を返す。
    """

    api_key = os.getenv("GEMINI_API_KEY")

    # APIキーが無い場合
    if not api_key:
        return generate_rule_analysis(data, score_result)

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知した投資アナリストです。

以下の企業を分析してください。

会社名：{data.get("company_name")}

ROE：{data.get("roe")}
ROA：{data.get("roa")}
営業利益率：{data.get("operating_margin")}
D/E：{data.get("debt_to_equity")}
PER：{data.get("pe_ratio")}
PBR：{data.get("pb_ratio")}
フリーキャッシュフロー：{data.get("free_cashflow")}
売上成長率：{data.get("revenue_growth")}

Buffett Score：
{score_result["total_score"]}/100

300文字程度で

・強み
・懸念点
・長期投資向きか

を日本語で説明してください。
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception:

        return generate_rule_analysis(data, score_result)


def generate_rule_analysis(data, score_result):

    comments = []

    roe = data.get("roe")
    if roe is not None:
        if roe >= 0.20:
            comments.append("ROEが非常に高く、資本効率に優れています。")
        elif roe >= 0.15:
            comments.append("ROEは良好な水準です。")
        else:
            comments.append("ROEはバフェット基準を下回っています。")

    op = data.get("operating_margin")
    if op is not None:
        if op >= 0.20:
            comments.append("営業利益率が高く、競争優位性が期待できます。")
        elif op < 0.10:
            comments.append("営業利益率が低く、収益性に課題があります。")

    fcf = data.get("free_cashflow")
    if fcf is not None:
        if fcf > 0:
            comments.append("フリーキャッシュフローはプラスで、現金創出力があります。")
        else:
            comments.append("フリーキャッシュフローがマイナスです。")

    score = score_result["total_score"]

    if score >= 75:
        comments.append("総合的には長期投資候補として有望と考えられます。")
    elif score >= 55:
        comments.append("追加調査を行ったうえで投資判断することをおすすめします。")
    else:
        comments.append("現時点では慎重な判断が望まれます。")

    return "\n\n".join(comments)


def generate_news_summary(news):
    if not news:
        return "ニュースは取得できませんでした。"

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _generate_rule_news_summary(news)

    try:
        client = genai.Client(api_key=api_key)
        news_text = ""

        for article in news:
            news_text += f"""
タイトル
{article['title']}

本文
{article.get('content','')}

-----------------------
"""

        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知した長期投資アナリストです。

以下は企業に関する最新ニュースです。

{news_text}

以下のルールで日本語で分析してください。

【分析方針】

・短期的な株価変動より企業価値を重視する
・一時的なニュースと長期的な変化を区別する
・競争優位性（MOAT）を重視する
・ブランド力を評価する
・価格決定力を評価する
・経営陣の質を評価する
・財務への影響も考慮する

以下の形式で回答してください。

# ニュース要約
200文字以内

# 重要ニュース
★★★★★〜★☆☆☆☆で重要度を付ける

# ポジティブ要因
箇条書き

# ネガティブ要因
箇条書き

# MOAT（競争優位性）への影響

# ブランド力への影響

# 価格決定力への影響

# 経営陣への印象

# 短期的な株価への影響

# 長期投資への影響

# Buffettならどう考えるか

最後に

【結論】

買い

様子見

見送り

のいずれかを理由付きで示してください。

"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text

    except Exception:
        return _generate_rule_news_summary(news)


def _generate_rule_news_summary(news):
    """ルールベースでニュース要約を生成する（APIキー未設定時・クォータ超過時のフォールバック）"""
    lines = ["⚠️ AI要約は現在利用できません（APIクォータ超過、または未設定）。以下は取得済みニュースの一覧です。\n"]
    lines.append("# ニュース一覧\n")
    for article in news:
        title = article.get("title", "")
        publisher = article.get("publisher", "")
        lines.append(f"- {title}" + (f"（{publisher}）" if publisher else ""))
    lines.append("\n※ AI分析を利用するには、しばらく時間を置いてから再実行するか、Gemini APIのプラン・クォータをご確認ください。")
    return "\n".join(lines)

def generate_buffett_checklist(data, score_result):
    """
    Buffett Investment Checklist を生成する。
    APIキーがあればGeminiに依頼し、なければルールベースで返す。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_buffett_checklist_rule(data, score_result)

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知したアナリストです。
以下の企業について、バフェットの投資チェックリスト6項目を評価してください。

会社名：{data.get("company_name")}
ROE：{data.get("roe")}
ROA：{data.get("roa")}
営業利益率：{data.get("operating_margin")}
D/E：{data.get("debt_to_equity")}
PER：{data.get("pe_ratio")}
PBR：{data.get("pb_ratio")}
フリーキャッシュフロー：{data.get("free_cashflow")}
売上成長率：{data.get("revenue_growth")}
セクター：{data.get("sector")}
Buffett Score：{score_result["total_score"]}/100

以下の6項目について、それぞれ「pass」「warning」「fail」のいずれかを判定し、50文字以内で理由を述べてください。

1. 経営圏（Understandable Business）：事業モデルがシンプルで理解できるか
2. 競争優位性（MOAT）：持続的な競争優位性があるか
3. 財務健全性（Conservative Debt）：負債が少なく保守的な財務か
4. 収益性（High Margin）：高い利益率を維持しているか
5. 経営者（Management Quality）：優秀な経営者が利益を再投資できるか
6. 安全余裕（Margin of Safety）：株価に適正な安全余裕があるか

回答は以下のJSON形式のみで出力してください。余計な文章は不要です。
[
  {{"item": "経営圏", "status": "pass", "reason": "..."}},
  {{"item": "競争優位性", "status": "pass", "reason": "..."}},
  {{"item": "財務健全性", "status": "pass", "reason": "..."}},
  {{"item": "収益性", "status": "warning", "reason": "..."}},
  {{"item": "経営者", "status": "pass", "reason": "..."}},
  {{"item": "安全余裕", "status": "pass", "reason": "..."}}
]
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        return json.loads(text)

    except Exception:
        return generate_buffett_checklist_rule(data, score_result)


def _generate_rule_checklist(data, score_result):
    """ルールベースでチェックリストを生成する（APIキー未設定時のフォールバック）"""
    checklist = []

    # 1. 経営圏
    sector = data.get("sector", "")
    understandable_sectors = [
        "Consumer Defensive", "Consumer Cyclical", "Utilities",
        "Financial Services", "Industrials", "Real Estate"
    ]
    if sector in understandable_sectors:
        checklist.append({
            "item": "経営圏（Understandable Business）",
            "status": "pass",
            "reason": "シンプルで理解しやすい業種です。"
        })
    else:
        checklist.append({
            "item": "経営圏（Understandable Business）",
            "status": "warning",
            "reason": "専門的な業種のため、深い理解が必要です。"
        })

    # 2. 競争優位性（MOAT）
    roe = data.get("roe") or 0
    op = data.get("operating_margin") or 0
    if roe >= 0.15 and op >= 0.15:
        checklist.append({
            "item": "競争優位性（MOAT）",
            "status": "pass",
            "reason": "高いROEと利益率から、強い競争優位性が考えられます。"
        })
    elif roe >= 0.10 or op >= 0.10:
        checklist.append({
            "item": "競争優位性（MOAT）",
            "status": "warning",
            "reason": "一定の優位性はありますが、強いMOATは確認できません。"
        })
    else:
        checklist.append({
            "item": "競争優位性（MOAT）",
            "status": "fail",
            "reason": "利益率が低く、競争優位性が弱い可能性があります。"
        })

    # 3. 財務健全性
    de = data.get("debt_to_equity")
    if de is not None:
        if de > 100:
            de = de / 100
        if de <= 0.5:
            checklist.append({
                "item": "財務健全性（Conservative Debt）",
                "status": "pass",
                "reason": "負債が少なく、保守的な財務です。"
            })
        elif de <= 1.0:
            checklist.append({
                "item": "財務健全性（Conservative Debt）",
                "status": "warning",
                "reason": "負債は許容範囲ですが、やや注意が必要です。"
            })
        else:
            checklist.append({
                "item": "財務健全性（Conservative Debt）",
                "status": "fail",
                "reason": "負債が多く、バフェットの基準を超えています。"
            })
    else:
        checklist.append({
            "item": "財務健全性（Conservative Debt）",
            "status": "warning",
            "reason": "財務データが取得できませんでした。"
        })

    # 4. 収益性
    if op >= 0.20:
        checklist.append({
            "item": "収益性（High Margin）",
            "status": "pass",
            "reason": "営業利益率が高く、強い収益性です。"
        })
    elif op >= 0.10:
        checklist.append({
            "item": "収益性（High Margin）",
            "status": "warning",
            "reason": "利益率は平均的です。"
        })
    else:
        checklist.append({
            "item": "収益性（High Margin）",
            "status": "fail",
            "reason": "利益率が低く、収益性に課題があります。"
        })

    # 5. 経営者
    fcf = data.get("free_cashflow")
    if fcf is not None and fcf > 0 and roe >= 0.10:
        checklist.append({
            "item": "経営者（Management Quality）",
            "status": "pass",
            "reason": "FCFがプラスで資本効率も高く、優秀な経営と考えられます。"
        })
    elif fcf is not None and fcf > 0:
        checklist.append({
            "item": "経営者（Management Quality）",
            "status": "warning",
            "reason": "現金創出力はありますが、資本効率に改善余地があります。"
        })
    else:
        checklist.append({
            "item": "経営者（Management Quality）",
            "status": "fail",
            "reason": "FCFがマイナスまたは資本効率が低く、経営に懸念があります。"
        })

    # 6. 安全余裕
    pe = data.get("pe_ratio")
    pb = data.get("pb_ratio")
    if pe is not None and pb is not None and pe > 0 and pb > 0:
        if pe <= 15 and pb <= 1.5:
            checklist.append({
                "item": "安全余裕（Margin of Safety）",
                "status": "pass",
                "reason": "PERとPBR共に割安で、安全余裕があります。"
            })
        elif pe <= 25 and pb <= 3.0:
            checklist.append({
                "item": "安全余裕（Margin of Safety）",
                "status": "warning",
                "reason": "適正価格帯ですが、強い安全余裕はありません。"
            })
        else:
            checklist.append({
                "item": "安全余裕（Margin of Safety）",
                "status": "fail",
                "reason": "割高で、安全余裕が不足しています。"
            })
    else:
        checklist.append({
            "item": "安全余裕（Margin of Safety）",
            "status": "warning",
            "reason": "適正株価を評価するデータが不足しています。"
        })

    return checklist


def generate_moat_analysis(data, score_result):
    """
    MOAT（持続的競争優位性）を評価する。
    定量指標と定性分析の両面からWide / Narrow / Noneを判定する。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _generate_rule_moat(data, score_result)

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知したアナリストです。
以下の企業の「経済的堀（MOAT）」を評価してください。

会社名：{data.get("company_name")}
セクター：{data.get("sector")}
ROE：{data.get("roe")}
ROA：{data.get("roa")}
営業利益率：{data.get("operating_margin")}
PER：{data.get("pe_ratio")}
PBR：{data.get("pb_ratio")}
フリーキャッシュフロー：{data.get("free_cashflow")}
売上成長率：{data.get("revenue_growth")}
負債比率（D/E）：{data.get("debt_to_equity")}

以下の6つの観点で、それぞれ strong / moderate / weak のいずれかを判定し、40文字以内で理由を述べてください。
企業に当てはまらない観点は weak としてください。

1. ブランド力（Intangible Assets / Brand）：消費者がブランド名でプレミアムを支払うか
2. 規模の経済（Cost Advantages / Scale）：コスト面での絶対的優位性があるか
3. 価格決定力（Pricing Power）：値上げしても顧客が離れない力があるか
4. ネットワーク効果（Network Effect）：利用者が増えるほど価値が増すか
5. スイッチングコスト（Switching Costs）：乗り換えにコスト・手間がかかるか
6. 規制・ライセンス（Regulatory / Legal Barriers）：参入を規制する法的障壁があるか

さらに、総合判定として以下の形式で回答してください。

rating: "wide" または "narrow" または "none"
stars: 1〜5の整数
summary: 100文字以内の総合所見

回答は以下のJSON形式のみで出力してください。余計な文章は不要です。
{{
  "rating": "wide",
  "stars": 4,
  "quantitative": {{
    "roe_evidence": "ROEが高く...",
    "margin_evidence": "営業利益率が...",
    "fcf_evidence": "FCFが...",
    "growth_evidence": "売上成長率が...",
    "score": 85
  }},
  "qualitative": [
    {{"type": "ブランド力", "strength": "strong", "reason": "..."}},
    {{"type": "規模の経済", "strength": "moderate", "reason": "..."}},
    {{"type": "価格決定力", "strength": "strong", "reason": "..."}},
    {{"type": "ネットワーク効果", "strength": "weak", "reason": "..."}},
    {{"type": "スイッチングコスト", "strength": "weak", "reason": "..."}},
    {{"type": "規制・ライセンス", "strength": "weak", "reason": "..."}}
  ],
  "summary": "..."
}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        return json.loads(text)

    except Exception:
        return _generate_rule_moat(data, score_result)


def _generate_rule_moat(data, score_result):
    """ルールベースでMOATを評価する（APIキー未設定時のフォールバック）"""
    roe = data.get("roe") or 0
    op = data.get("operating_margin") or 0
    fcf = data.get("free_cashflow")
    rg = data.get("revenue_growth") or 0
    pe = data.get("pe_ratio")
    pb = data.get("pb_ratio")

    # 定量スコア（100点満点）
    q_score = 0

    if roe >= 0.20:
        q_score += 25
        roe_evidence = "ROEが20%以上で、極めて高い資本効率。強い競争優位性の証左です。"
    elif roe >= 0.15:
        q_score += 15
        roe_evidence = "ROEが15%以上で、良好な資本効率。一定の優位性が考えられます。"
    elif roe >= 0.10:
        q_score += 5
        roe_evidence = "ROEは平均的。突出した優位性は見られません。"
    else:
        roe_evidence = "ROEが低く、資本効率に課題があります。"

    if op >= 0.20:
        q_score += 25
        margin_evidence = "営業利益率が20%以上で、非常に強い価格決定力とコスト優位性を示唆します。"
    elif op >= 0.15:
        q_score += 15
        margin_evidence = "営業利益率が15%以上で、強い収益性。価格決定力に一定の優位性があります。"
    elif op >= 0.10:
        q_score += 5
        margin_evidence = "営業利益率は平均的。業界特有の競争が激しい可能性があります。"
    else:
        margin_evidence = "営業利益率が低く、価格決定力やコスト優位性に乏しい可能性があります。"

    if fcf is not None and fcf > 0:
        q_score += 20
        fcf_evidence = "フリーキャッシュフローがプラスで、実際に現金を創出しています。"
    else:
        fcf_evidence = "FCFがマイナスまたは取得できません。現金創出力に疑問があります。"

    if rg >= 0.10:
        q_score += 20
        growth_evidence = "売上が10%以上成長。競争優位性を活かした力強い拡大です。"
    elif rg >= 0.05:
        q_score += 10
        growth_evidence = "売上が5%以上成長。優位性を活かした安定した成長です。"
    elif rg >= 0:
        q_score += 5
        growth_evidence = "売上は横ばい。新たな成長ドライバーが必要です。"
    else:
        growth_evidence = "売上が減少。競争優位性が弱まっている可能性があります。"

    if pe is not None and 0 < pe <= 15:
        q_score += 10
    elif pe is not None and 0 < pe <= 25:
        q_score += 5

    if pb is not None and 0 < pb <= 1.5:
        q_score += 10
    elif pb is not None and 0 < pb <= 3.0:
        q_score += 5

    # 総合判定
    if q_score >= 80:
        rating = "wide"
        stars = 5 if q_score >= 90 else 4
    elif q_score >= 50:
        rating = "narrow"
        stars = 3 if q_score >= 65 else 2
    else:
        rating = "none"
        stars = 1

    # 定性評価（簡易的なセクター推定）
    sector = data.get("sector", "")
    qualitative = []

    brand_sectors = ["Consumer Defensive", "Consumer Cyclical", "Communication Services"]
    if sector in brand_sectors:
        qualitative.append({
            "type": "ブランド力",
            "strength": "moderate",
            "reason": "消費者向けセクターのため、ブランドによる差別化が期待できます。"
        })
    else:
        qualitative.append({
            "type": "ブランド力",
            "strength": "weak",
            "reason": "ブランドが主な競争力にならない業種です。"
        })

    scale_sectors = ["Industrials", "Energy", "Materials", "Utilities"]
    if sector in scale_sectors:
        qualitative.append({
            "type": "規模の経済",
            "strength": "moderate",
            "reason": "設備投資型の業種のため、規模によるコスト優位性が期待できます。"
        })
    else:
        qualitative.append({
            "type": "規模の経済",
            "strength": "weak",
            "reason": "軽資産型の業種のため、規模のメリットは限定的です。"
        })

    if op >= 0.20:
        qualitative.append({
            "type": "価格決定力",
            "strength": "strong",
            "reason": "高い営業利益率から、強い価格決定力が読み取れます。"
        })
    elif op >= 0.10:
        qualitative.append({
            "type": "価格決定力",
            "strength": "moderate",
            "reason": "標準的な利益率。価格決定力は平均的です。"
        })
    else:
        qualitative.append({
            "type": "価格決定力",
            "strength": "weak",
            "reason": "低い利益率から、価格決定力は弱いと考えられます。"
        })

    # ネットワーク効果・スイッチングコスト・規制は業界情報がないためweakとする
    qualitative.append({
        "type": "ネットワーク効果",
        "strength": "weak",
        "reason": "公開情報からネットワーク効果の証拠は確認できません。"
    })
    qualitative.append({
        "type": "スイッチングコスト",
        "strength": "weak",
        "reason": "公開情報から高いスイッチングコストは確認できません。"
    })
    qualitative.append({
        "type": "規制・ライセンス",
        "strength": "weak",
        "reason": "業界特有の規制・ライセンス障壁の情報はありません。"
    })

    if rating == "wide":
        summary = "財務指標から強い競争優位性が読み取れます。バフェットが好む「広い堀」を持つ可能性が高いです。"
    elif rating == "narrow":
        summary = "一定の競争優位性はありますが、業界変化に応じて堀が狭まるリスクに注意が必要です。"
    else:
        summary = "現時点では持続的な競争優位性が認められにくい。事業の差別化要因が弱い可能性があります。"

    return {
        "rating": rating,
        "stars": stars,
        "quantitative": {
            "roe_evidence": roe_evidence,
            "margin_evidence": margin_evidence,
            "fcf_evidence": fcf_evidence,
            "growth_evidence": growth_evidence,
            "score": q_score
        },
        "qualitative": qualitative,
        "summary": summary
    }


def generate_brand_analysis(data, score_result):
    """
    ブランド力（Brand Power）を独立して評価する。
    定量指標と定性分析から、バフェット的視点でのブランド力スコアを算出する。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _generate_rule_brand(data, score_result)

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知したアナリストです。
以下の企業の「ブランド力」を深掘り評価してください。

会社名：{data.get("company_name")}
セクター：{data.get("sector")}
ROE：{data.get("roe")}
ROA：{data.get("roa")}
営業利益率：{data.get("operating_margin")}
PER：{data.get("pe_ratio")}
PBR：{data.get("pb_ratio")}
フリーキャッシュフロー：{data.get("free_cashflow")}
売上成長率：{data.get("revenue_growth")}
負債比率（D/E）：{data.get("debt_to_equity")}

以下の項目で評価し、JSON形式のみで出力してください。

1. stars: 1〜5の整数（ブランド力総合スコア）
2. brand_type: ブランドの種類（製品ブランド / 企業ブランド / プラットフォームブランド / B2Bブランド / 弱い）
3. pricing_power: strong / moderate / weak（価格弾力性）
4. loyalty: strong / moderate / weak（顧客ロイヤルティ）
5. recognition: strong / moderate / weak（世界的認知度）
6. maintenance_cost: low / moderate / high（ブランド維持コスト）
7. sustainability: 長期的にブランド力が維持されるか（50文字以内）
8. buffet_view: バフェット的視点から100文字以内の所見
9. quantitative:
   - margin_evidence: 営業利益率から読み取れるブランド力（50文字以内）
   - growth_evidence: 売上成長率から読み取れるブランド力（50文字以内）
   - score: 定量ブランドスコア（0-100の整数）

回答は以下のJSON形式のみで出力してください。余計な文章は不要です。
{{
  "stars": 4,
  "brand_type": "製品ブランド",
  "pricing_power": "strong",
  "loyalty": "strong",
  "recognition": "strong",
  "maintenance_cost": "low",
  "sustainability": "長期的に維持される見込み。",
  "buffet_view": "寝ても覚めても使われるブランドで、強い価格決定力がある。",
  "quantitative": {{
    "margin_evidence": "営業利益率35%はプレミアム価格の証拠。",
    "growth_evidence": "売上成長12%はブランド吸引力の証拠。",
    "score": 85
  }}
}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        return json.loads(text)

    except Exception:
        return _generate_rule_brand(data, score_result)


def _generate_rule_brand(data, score_result):
    """ルールベースでブランド力を評価する（APIキー未設定時のフォールバック）"""
    op = data.get("operating_margin") or 0
    rg = data.get("revenue_growth") or 0
    roe = data.get("roe") or 0
    sector = data.get("sector", "")

    # 定量スコア
    q_score = 0

    if op >= 0.25:
        q_score += 40
        margin_evidence = "営業利益率が25%以上で、強いブランドによるプレミアム価格が読み取れます。"
    elif op >= 0.15:
        q_score += 25
        margin_evidence = "営業利益率が15%以上で、ブランドによる価格決定力が一定あります。"
    elif op >= 0.10:
        q_score += 10
        margin_evidence = "営業利益率は平均的。ブランドによる付加価値は限定的です。"
    else:
        margin_evidence = "営業利益率が低く、ブランドによる価格決定力は弱いと考えられます。"

    if rg >= 0.10:
        q_score += 30
        growth_evidence = "売上が10%以上成長。ブランドの吸引力が需要拡大を牽引しています。"
    elif rg >= 0.05:
        q_score += 15
        growth_evidence = "売上が5%以上成長。ブランドは安定的な需要を確保しています。"
    elif rg >= 0:
        q_score += 5
        growth_evidence = "売上は横ばい。ブランドの新たな魅力が必要です。"
    else:
        growth_evidence = "売上が減少。ブランド力が弱まっている可能性があります。"

    if roe >= 0.20:
        q_score += 30
    elif roe >= 0.15:
        q_score += 20
    elif roe >= 0.10:
        q_score += 10

    # 星評価
    if q_score >= 80:
        stars = 5
    elif q_score >= 65:
        stars = 4
    elif q_score >= 50:
        stars = 3
    elif q_score >= 30:
        stars = 2
    else:
        stars = 1

    # ブランドタイプ推定
    brand_type = "弱い"
    if sector in ["Consumer Defensive", "Consumer Cyclical", "Communication Services"]:
        brand_type = "製品ブランド"
    elif sector in ["Technology", "Software"]:
        brand_type = "プラットフォームブランド"
    elif sector in ["Industrials", "Materials", "Energy"]:
        brand_type = "B2Bブランド"

    if stars <= 2:
        brand_type = "弱い"

    # 定性推定
    if stars >= 4:
        pricing_power = "strong"
        loyalty = "strong"
        recognition = "moderate"
        maintenance_cost = "low"
        sustainability = "高い利益率と成長から、ブランド力は長期的に維持される見込みです。"
        buffet_view = "強い価格決定力と顧客ロイヤルティが、経済的堀の中核を成している。バフェットも好むタイプ。"
    elif stars >= 3:
        pricing_power = "moderate"
        loyalty = "moderate"
        recognition = "moderate"
        maintenance_cost = "moderate"
        sustainability = "一定のブランド力はあるが、競合の攻勢に注意が必要です。"
        buffet_view = "ブランドは一定の価値があるが、さらに深い堀が必要と考えられる。"
    else:
        pricing_power = "weak"
        loyalty = "weak"
        recognition = "weak"
        maintenance_cost = "high"
        sustainability = "現時点ではブランドによる持続的優位性は認めにくい。"
        buffet_view = "ブランドが主な投資理由にはなりづらい。別のMOAT要因を探る必要がある。"

    return {
        "stars": stars,
        "brand_type": brand_type,
        "pricing_power": pricing_power,
        "loyalty": loyalty,
        "recognition": recognition,
        "maintenance_cost": maintenance_cost,
        "sustainability": sustainability,
        "buffet_view": buffet_view,
        "quantitative": {
            "margin_evidence": margin_evidence,
            "growth_evidence": growth_evidence,
            "score": q_score
        }
    }


def generate_management_analysis(data, score_result):
    """
    経営者（Management Quality）を独立して評価する。
    資本配分能力・透明性・長期視点などを定量と定性で評価する。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _generate_rule_management(data, score_result)

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知したアナリストです。
以下の企業の「経営者力」を深掘り評価してください。

会社名：{data.get("company_name")}
ROE：{data.get("roe")}
ROA：{data.get("roa")}
営業利益率：{data.get("operating_margin")}
PER：{data.get("pe_ratio")}
PBR：{data.get("pb_ratio")}
フリーキャッシュフロー：{data.get("free_cashflow")}
売上成長率：{data.get("revenue_growth")}
負債比率（D/E）：{data.get("debt_to_equity")}
配当利回り：{data.get("dividend_yield")}

以下の項目で評価し、JSON形式のみで出力してください。

1. stars: 1〜5の整数（経営者総合スコア）
2. capital_allocation: excellent / good / average / poor（資本配分能力：再投資と還元のバランス）
3. transparency: high / moderate / low（情報開示の透明性）
4. long_term: yes / partial / no（長期視点の有無）
5. self_interest: low / moderate / high（自己利益 vs 株主利益）
6. founder_led: yes / no / unknown（創業者経営の有無）
7. debt_management: conservative / moderate / aggressive（負債管理の保守性）
8. buffet_view: バフェット的視点から100文字以内の所見
9. quantitative:
   - roe_evidence: ROEから読み取れる経営能力（50文字以内）
   - fcf_evidence: FCFから読み取れる経営能力（50文字以内）
   - dividend_evidence: 配当から読み取れる経営姿勢（50文字以内）
   - score: 定量経営者スコア（0-100の整数）

回答は以下のJSON形式のみで出力してください。余計な文章は不要です。
{{
  "stars": 4,
  "capital_allocation": "good",
  "transparency": "high",
  "long_term": "yes",
  "self_interest": "low",
  "founder_led": "no",
  "debt_management": "conservative",
  "buffet_view": "余剰キャッシュを株主還元に回し、自己資本を効率的に活用している。",
  "quantitative": {{
    "roe_evidence": "ROE 20%で優れた資本効率を維持。",
    "fcf_evidence": "FCFがプラスで現金創出能力が高い。",
    "dividend_evidence": "配当継続で株主重視の姿勢が見える。",
    "score": 82
  }}
}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        return json.loads(text)

    except Exception:
        return _generate_rule_management(data, score_result)


def _generate_rule_management(data, score_result):
    """ルールベースで経営者を評価する（APIキー未設定時のフォールバック）"""
    roe = data.get("roe") or 0
    fcf = data.get("free_cashflow")
    de = data.get("debt_to_equity")
    dy = data.get("dividend_yield")
    rg = data.get("revenue_growth") or 0

    # 定量スコア（100点満点）
    q_score = 0

    # ROE維持力
    if roe >= 0.20:
        q_score += 30
        roe_evidence = "ROEが20%以上を維持。優れた資本効率の管理が見られます。"
    elif roe >= 0.15:
        q_score += 20
        roe_evidence = "ROEが15%以上。資本効率の管理は良好です。"
    elif roe >= 0.10:
        q_score += 10
        roe_evidence = "ROEは平均的。資本効率に改善の余地があります。"
    else:
        roe_evidence = "ROEが低く、資本効率の管理に課題があります。"

    # FCF創出
    if fcf is not None and fcf > 0:
        q_score += 25
        fcf_evidence = "フリーキャッシュフローがプラス。株主還元原資の確保ができています。"
    else:
        fcf_evidence = "FCFがマイナスまたは取得できません。現金創出能力に懸念があります。"

    # 負債管理
    if de is not None:
        if de > 100:
            de = de / 100
        if de <= 0.5:
            q_score += 20
            debt_management = "conservative"
            debt_evidence = "負債比率が低く、保守的な財務運営が見られます。"
        elif de <= 1.0:
            q_score += 10
            debt_management = "moderate"
            debt_evidence = "負債は許容範囲で、バランスの取れた財務運営です。"
        else:
            debt_management = "aggressive"
            debt_evidence = "負債が多く、やや積極的すぎる財務運営の可能性があります。"
    else:
        debt_management = "moderate"
        debt_evidence = "負債データが取得できませんでした。"

    # 配当継続性（配当利回りがあれば加点）
    if dy is not None and dy > 0:
        q_score += 15
        dividend_evidence = "配当を継続しており、株主還元への意識が見られます。"
    else:
        dividend_evidence = "配当データがないか、配当を実施していない可能性があります。"

    # 成長の質
    if rg >= 0.05:
        q_score += 10
        growth_evidence = "売上が成長しており、経営者が市場機会を活かしている可能性があります。"
    else:
        growth_evidence = "成長が鈍い。新たな成長戦略が必要かもしれません。"

    # 星評価
    if q_score >= 85:
        stars = 5
    elif q_score >= 70:
        stars = 4
    elif q_score >= 55:
        stars = 3
    elif q_score >= 40:
        stars = 2
    else:
        stars = 1

    # 定性推定
    if stars >= 4:
        capital_allocation = "good"
        transparency = "high"
        long_term = "yes"
        self_interest = "low"
        founder_led = "unknown"
        buffet_view = "余剰キャッシュを効率的に配分し、自己資本を高い水準で維持している。バフェットが好むタイプの経営者。"
        conclusion = "🟢 バフェットが好むタイプの経営者。長期保有に値する。"
    elif stars >= 3:
        capital_allocation = "average"
        transparency = "moderate"
        long_term = "partial"
        self_interest = "moderate"
        founder_led = "unknown"
        buffet_view = "一定の資本配分能力はあるが、さらなる株主還元や長期投資の深化が望まれる。"
        conclusion = "🟡 まずまずの経営者。追加調査で資本配分の姿勢を確認すること。"
    else:
        capital_allocation = "poor"
        transparency = "low"
        long_term = "no"
        self_interest = "high"
        founder_led = "unknown"
        buffet_view = "資本効率や財務運営に懸念があり、バフェット基準を下回る可能性が高い。"
        conclusion = "🔴 経営者の質に懸念。現時点では慎重な判断が望まれる。"

    return {
        "stars": stars,
        "capital_allocation": capital_allocation,
        "transparency": transparency,
        "long_term": long_term,
        "self_interest": self_interest,
        "founder_led": founder_led,
        "debt_management": debt_management,
        "buffet_view": buffet_view,
        "conclusion": conclusion,
        "quantitative": {
            "roe_evidence": roe_evidence,
            "fcf_evidence": fcf_evidence,
            "dividend_evidence": dividend_evidence,
            "score": q_score
        }
    }


def generate_red_team_analysis(data, score_result, checklist, moat, brand, mgmt):
    """
    Red Team AI（反対意見・Devil's Advocate）を生成する。
    既存の分析結果を受け取り、投資の反対側からの疑問とリスクを提示する。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _generate_rule_red_team(data, score_result, checklist, moat, brand, mgmt)

    try:
        client = genai.Client(api_key=api_key)

        # 既存分析結果をテキスト化してプロンプトに渡す
        checklist_text = json.dumps(checklist, ensure_ascii=False) if isinstance(checklist, list) else str(checklist)
        moat_text = json.dumps(moat, ensure_ascii=False) if isinstance(moat, dict) else str(moat)
        brand_text = json.dumps(brand, ensure_ascii=False) if isinstance(brand, dict) else str(brand)
        mgmt_text = json.dumps(mgmt, ensure_ascii=False) if isinstance(mgmt, dict) else str(mgmt)

        prompt = f"""
あなたは「バフェット投資の悪魔の代弁者」です。
これまでの分析が「買い」に傾きがちなバイアスを持つことを自覚し、
あえて「この企業を買わない理由」「分析の盲点」を提示してください。

以下は現在の分析結果です。

【財務スコア】
Buffett Score: {score_result.get("total_score", 0)}/100
判定: {score_result.get("verdict", "不明")}

【企業データ】
ROE: {data.get("roe")}
ROA: {data.get("roa")}
営業利益率: {data.get("operating_margin")}
PER: {data.get("pe_ratio")}
PBR: {data.get("pb_ratio")}
FCF: {data.get("free_cashflow")}
売上成長率: {data.get("revenue_growth")}
D/E: {data.get("debt_to_equity")}

【チェックリスト】
{checklist_text}

【MOAT評価】
{moat_text}

【ブランド力評価】
{brand_text}

【経営者評価】
{mgmt_text}

以下の観点で、それぞれ「この企業を買わない理由」を簡潔に（各40文字以内）述べてください。
JSON形式のみで出力。余計な文章は不要です。

1. financial_skepticism: 財務指標への疑問（ROEはレバレッジによるか？利益率は持続可能か？）
2. moat_vulnerability: MOATの脆弱性（技術変化、規制、競合で堀が埋まるリスク）
3. brand_demand_risk: ブランド・需要リスク（若年層離反、嗜好変化、維持コスト増大）
4. management_blindspot: 経営者・組織の盲点（後継者、M&A失敗、キャッシュの無駄遣い）
5. valuation_concern: バリュエーションの過大評価（PER/PBRの割高感、安全余裕の不足）
6. conclusion: バフェットが静観する理由（100文字以内）

回答は以下のJSON形式のみで出力してください。
{{
  "financial_skepticism": "...",
  "moat_vulnerability": "...",
  "brand_demand_risk": "...",
  "management_blindspot": "...",
  "valuation_concern": "...",
  "conclusion": "..."
}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        return json.loads(text)

    except Exception:
        return _generate_rule_red_team(data, score_result, checklist, moat, brand, mgmt)


def _generate_rule_red_team(data, score_result, checklist, moat, brand, mgmt):
    """ルールベースでRed Team（反対意見）を生成する（APIキー未設定時のフォールバック）"""
    concerns = []

    roe = data.get("roe")
    de = data.get("debt_to_equity")
    if de is not None and de > 100:
        de = de / 100

    # 財務の疑問
    if roe is not None and roe >= 0.20 and de is not None and de >= 1.0:
        financial_skepticism = "ROEは高いが、負債比率も高いためレバレッジによる可能性が高い。実質的な資本効率は見かけ倒れかもしれない。"
    elif roe is not None and roe < 0.10:
        financial_skepticism = "ROEが低く、資本効率に根本的な疑問がある。高いROEでなければ、バフェットは投資しない。"
    else:
        financial_skepticism = "財務指標は良好に見えるが、1年分のデータに過度に依存していないか？長期トレンドの確認が必要。"

    # MOATの脆弱性
    moat_rating = moat.get("rating", "none") if isinstance(moat, dict) else "none"
    if moat_rating == "none":
        moat_vulnerability = "MOATが認められない。競合に容易に模倣され、価格競争に巻き込まれるリスクが高い。"
    elif moat_rating == "narrow":
        moat_vulnerability = "MOATはあるが狭い。テクノロジー変化や規制緩和で、数年で消失する可能性がある。"
    else:
        moat_vulnerability = "広いMOATを持つと評価したが、過去の優位性が未来に通用するとは限らない。変化の速度に注意。"

    # ブランドリスク
    brand_stars = brand.get("stars", 0) if isinstance(brand, dict) else 0
    if brand_stars <= 2:
        brand_demand_risk = "ブランド力が弱い。製品差別化が困難で、コモディティ化のリスクが高い。"
    else:
        brand_demand_risk = "ブランドは強いと評価したが、次世代の消費者（Z世代）の嗜好に合致しているか疑問。維持コストの増大も懸念。"

    # 経営者の盲点
    mgmt_stars = mgmt.get("stars", 0) if isinstance(mgmt, dict) else 0
    if mgmt_stars <= 2:
        management_blindspot = "経営者の質に懸念。資本配分の失敗や、自己利益優先の可能性が否定できない。"
    else:
        management_blindspot = "経営者は優秀と評価したが、創業者依存・後継者不在のリスク、または過去の大規模M&A失敗の有無を確認すべき。"

    # バリュエーション
    pe = data.get("pe_ratio")
    pb = data.get("pb_ratio")
    if pe is not None and pe > 30:
        valuation_concern = f"PERが{pe:.1f}倍と極めて高い。将来の成長を過大に織り込み、安全余裕がない。バフェットは待つだろう。"
    elif pe is not None and pe > 25:
        valuation_concern = f"PERが{pe:.1f}倍と高め。まだ許容範囲だが、成長鈍化時の下振れリスクは大きい。"
    elif pb is not None and pb > 5.0:
        valuation_concern = f"PBRが{pb:.1f}倍と高い。帳簿価値に対して大きなプレミアムがついており、割安感は乏しい。"
    else:
        valuation_concern = "バリュエーションは適正に見えるが、市場全体が楽観的な場合、相対的に割高になっている可能性に注意。"

    # 結論
    total_score = score_result.get("total_score", 0)
    if total_score >= 75:
        conclusion = "各種スコアは高いが、優良企業は誰もが知っている。現在の株価に「安全余裕」があるかが最大の疑問。バフェットは「待つ」か「買い増し」で迷う。"
    elif total_score >= 55:
        conclusion = "一定の魅力は認められるが、複数の懸念材料が重なる。バフェットは「もっと調べてから」と言うだろう。"
    else:
        conclusion = "財務スコアが低い。買う理由より買わない理由の方が多い。バフェットは即座に見送るタイプ。"

    return {
        "financial_skepticism": financial_skepticism,
        "moat_vulnerability": moat_vulnerability,
        "brand_demand_risk": brand_demand_risk,
        "management_blindspot": management_blindspot,
        "valuation_concern": valuation_concern,
        "conclusion": conclusion
    }


def generate_investment_hypothesis(data, score_result, checklist, moat, brand, mgmt, red_team):
    """
    投資仮説を自動生成する。
    APIキーがあればGeminiに依頼し、なければルールベースで返す。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        from hypothesis import generate_default_hypotheses
        return generate_default_hypotheses(data, score_result, checklist, moat, brand, mgmt, red_team)

    try:
        client = genai.Client(api_key=api_key)

        checklist_text = json.dumps(checklist, ensure_ascii=False) if isinstance(checklist, list) else str(checklist)
        moat_text = json.dumps(moat, ensure_ascii=False) if isinstance(moat, dict) else str(moat)
        brand_text = json.dumps(brand, ensure_ascii=False) if isinstance(brand, dict) else str(brand)
        mgmt_text = json.dumps(mgmt, ensure_ascii=False) if isinstance(mgmt, dict) else str(mgmt)
        red_team_text = json.dumps(red_team, ensure_ascii=False) if isinstance(red_team, dict) else str(red_team)

        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知したアナリストです。
以下の分析結果を基に、投資仮説（Investment Hypothesis）を3〜5個生成してください。

【企業データ】
会社名: {data.get("company_name")}
ROE: {data.get("roe")}
営業利益率: {data.get("operating_margin")}
PER: {data.get("pe_ratio")}
PBR: {data.get("pb_ratio")}
FCF: {data.get("free_cashflow")}
D/E: {data.get("debt_to_equity")}

【Buffett Score】
{score_result.get("total_score", 0)}/100

【各種評価】
Checklist: {checklist_text}
MOAT: {moat_text}
Brand: {brand_text}
Management: {mgmt_text}
Red Team: {red_team_text}

各仮説は以下のJSON形式で出力してください。余計な文章は不要です。
statusは「未検証」「検証中」「成立」「却下」「保留」のいずれか。

[
  {{"id": 1, "title": "...", "rationale": "...", "evidence": ["...", "..."], "verification_items": ["...", "..."], "status": "未検証", "source": "ai"}},
  {{"id": 2, "title": "...", "rationale": "...", "evidence": ["...", "..."], "verification_items": ["...", "..."], "status": "未検証", "source": "ai"}}
]
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        raw_list = json.loads(text)

        # dict から dataclass へ変換
        from hypothesis import InvestmentHypothesis, HypothesisStatus
        hypotheses = []
        for idx, d in enumerate(raw_list, start=1):
            d["id"] = idx
            hypotheses.append(InvestmentHypothesis(
                id=d["id"],
                title=d["title"],
                rationale=d["rationale"],
                evidence=d.get("evidence", []),
                verification_items=d.get("verification_items", []),
                status=HypothesisStatus(d.get("status", "未検証")),
                source="ai",
            ))
        return hypotheses

    except Exception:
        from hypothesis import generate_default_hypotheses
        return generate_default_hypotheses(data, score_result, checklist, moat, brand, mgmt, red_team)

def generate_news_confirmation_points(data, news, score_result):
    """
    Sprint7: ニュースから「次に確認すべきポイント」をAIが自動生成する。
    APIキーがあればGeminiに依頼し、なければルールベースで返す。
    """
    if not news:
        return []

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _generate_rule_confirmation_points(data, news, score_result)

    try:
        client = genai.Client(api_key=api_key)
        news_text = ""
        for article in news:
            news_text += f"""
タイトル
{article['title']}

本文
{article.get('content','')}

-----------------------
"""

        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知した長期投資アナリストです。

以下は企業に関する最新ニュースと基本情報です。

会社名：{data.get("company_name")}
セクター：{data.get("sector")}
Buffett Score：{score_result.get("total_score", 0)}/100

【ニュース】
{news_text}

このニュースを踏まえて、投資判断の前に「次に確認すべきポイント」を5〜8個、
以下のカテゴリの中から該当するものを選んで提示してください。

カテゴリ例：
決算確認項目 / リスクイベント / 競合動向 / 設備投資 / 規制 / 為替 / その他

各ポイントについて、以下を判定してください。
- category: 上記カテゴリのいずれか
- point: 確認すべき内容（60文字以内）
- priority: "high" / "medium" / "low"（緊急度・重要度）

回答は以下のJSON形式のみで出力してください。余計な文章は不要です。
[
  {{"category": "決算確認項目", "point": "...", "priority": "high"}},
  {{"category": "リスクイベント", "point": "...", "priority": "medium"}}
]
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        return json.loads(text)

    except Exception:
        return _generate_rule_confirmation_points(data, news, score_result)


def _generate_rule_confirmation_points(data, news, score_result):
    """ルールベースで確認ポイントを生成する（APIキー未設定時・エラー時のフォールバック）"""
    points = []

    # 決算確認項目：財務スコアに応じて
    total_score = score_result.get("total_score", 0)
    if total_score < 75:
        points.append({
            "category": "決算確認項目",
            "point": "次期決算で主要指標（ROE・営業利益率）が改善しているか確認する。",
            "priority": "high"
        })
    else:
        points.append({
            "category": "決算確認項目",
            "point": "次期決算で高水準の指標が維持されているか確認する。",
            "priority": "medium"
        })

    # リスクイベント：ニュース件数から一般的な注意喚起
    points.append({
        "category": "リスクイベント",
        "point": f"直近ニュース{len(news)}件の内容が一時的要因か構造的変化かを見極める。",
        "priority": "medium"
    })

    # 競合動向
    points.append({
        "category": "競合動向",
        "point": "同業他社の決算・新製品動向と比較し、相対的な優位性を確認する。",
        "priority": "medium"
    })

    # 設備投資
    fcf = data.get("free_cashflow")
    if fcf is not None and fcf < 0:
        points.append({
            "category": "設備投資",
            "point": "FCFがマイナスのため、設備投資の規模と回収見込みを確認する。",
            "priority": "high"
        })
    else:
        points.append({
            "category": "設備投資",
            "point": "設備投資が将来の成長にどう寄与するか確認する。",
            "priority": "low"
        })

    # 規制
    sector = data.get("sector", "")
    if sector in ["Financial Services", "Utilities", "Healthcare", "Energy"]:
        points.append({
            "category": "規制",
            "point": f"{sector}セクターは規制変更の影響を受けやすいため、関連法規の動向を確認する。",
            "priority": "medium"
        })

    # 為替
    if data.get("country") and data.get("country") != "Japan":
        points.append({
            "category": "為替",
            "point": "為替変動が業績・株価に与える影響を確認する。",
            "priority": "low"
        })

    return points


def generate_earnings_material_analysis(pdf_text, company_name=None):
    """
    Sprint17: 決算資料解析
    アップロードされた決算説明資料（PDFから抽出したテキスト）を
    Geminiに渡して要約・ポイント抽出させる。
    APIキーがあればGeminiに依頼し、なければルールベースで返す
    （既存のgenerate_ai_analysis等と同じフォールバック設計）。
    """
    if not pdf_text or not pdf_text.strip():
        return "PDFからテキストを抽出できませんでした。"

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _generate_rule_earnings_material_analysis(pdf_text)

    try:
        client = genai.Client(api_key=api_key)

        # プロンプトに収まるよう、長すぎる場合は先頭部分のみを使用する
        truncated_text = pdf_text[:15000]

        company_line = f"会社名（参考情報）：{company_name}\n" if company_name else ""

        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知した長期投資アナリストです。

以下は企業の決算説明資料（決算プレゼンテーション資料等）から抽出したテキストです。

{company_line}
【決算資料本文（抜粋）】
{truncated_text}

以下のルールで日本語で分析してください。

【分析方針】
・短期的な株価変動より企業価値を重視する
・数字の背景にある構造的な変化を見極める
・競争優位性（MOAT）への影響を意識する
・経営陣のコメントのトーン（強気/弱気/曖昧）を評価する

以下の形式で回答してください。

# 決算サマリー
200文字以内

# 良かった点
箇条書き

# 懸念点
箇条書き

# 経営陣コメントの印象

# 長期投資への影響

# Buffettならどう考えるか
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text

    except Exception:
        return _generate_rule_earnings_material_analysis(pdf_text)


def _generate_rule_earnings_material_analysis(pdf_text):
    """ルールベースで決算資料の簡易表示を行う（APIキー未設定時・エラー時のフォールバック）"""
    preview = pdf_text.strip()
    if len(preview) > 1000:
        preview = preview[:1000] + "…"

    lines = [
        "⚠️ AI要約は現在利用できません（APIクォータ超過、または未設定）。",
        "以下はPDFから抽出したテキストの冒頭部分です。\n",
        preview,
        "\n※ AI分析を利用するには、しばらく時間を置いてから再実行するか、"
        "Gemini APIのプラン・クォータをご確認ください。",
    ]
    return "\n".join(lines)


####################################################
# Sprint18
# Buffett Overall Summary
# 総合評価文章だけをGeminiに生成させる
####################################################


def generate_overall_summary(
    overall,
    data,
    score_result,
):

    company = data.get("company_name", "この企業")

    prompt = f"""
あなたはウォーレン・バフェット投資法専門のアナリストです。

以下の結果から100〜150文字程度で
投資判断をまとめてください。

会社名
{company}

Buffett Score
{score_result["total_score"]}/100

Overall Grade
{overall["grade"]}

Risk
{overall["risk"]}

Confidence
{overall["confidence"]}

推奨アクション
{overall["action"]}

初心者にも分かる文章でお願いします。
"""

    try:
        return _call_gemini(prompt)

    except Exception:

        return (
            f"{company}は"
            f"Overall Grade {overall['grade']} "
            f"と評価されました。"
            f"{overall['action']}です。"
        )
def generate_roic_analysis(data: dict, roic_result: dict) -> dict:
    """ROIC分析結果に対するAI評価を生成する（Sprint19）。"""
    company = data.get("company_name", "不明")
    roic = roic_result.get("roic")
    nopat = roic_result.get("nopat")
    ic = roic_result.get("invested_capital")
    rating = roic_result.get("rating", "unknown")

    if roic is None:
        return {
            "id": "roic",
            "title": "ROIC（投下資本利益率）AI評価",
            "score": 0,
            "max_score": 15,
            "rating": "unknown",
            "summary": f"{company}のROICを計算するためのデータが不足しています。",
            "details": [],
            "warnings": ["データ不足のためAI評価を生成できませんでした。"],
            "buffet_view": "評価できません。",
        }

    fallback = {
        "id": "roic",
        "title": "ROIC（投下資本利益率）AI評価",
        "score": min(int(roic * 100 / 20 * 15), 15) if roic else 0,
        "max_score": 15,
        "rating": rating,
        "summary": f"{company}のROICは{roic*100:.1f}%（{rating}）です。",
        "details": [],
        "warnings": [],
        "buffet_view": f"ROIC {roic*100:.1f}%は、{company}の資本効率を示しています。",
        "conclusion": f"ROIC {roic*100:.1f}% - {rating}",
    }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback

    prompt = f"""あなたはウォーレン・バフェットの投資スタイルを模倣したAIアナリストです。

{company}のROIC（投下資本利益率）分析結果をバフェット視点で評価してください。

## 分析データ
- ROIC: {roic*100:.1f}%
- NOPAT（税引後営業利益）: {f'{nopat:,.0f}' if nopat else 'N/A'}
- 投下資本: {f'{ic:,.0f}' if ic else 'N/A'}
- 評価: {rating}

## 評価基準（バフェット）
- ROIC 20%以上: 強力な競争優位性（Wide Moat）の証拠
- ROIC 15%以上: 良好な資本効率
- ROIC 10%以上: 平均的
- ROIC 10%未満: 資本効率に課題

## 出力形式（JSON）
{{
    "buffet_view": "バフェット視点での洞察（100〜200文字）",
    "competitive_advantage": "競争優位性への影響（50〜100文字）",
    "capital_efficiency": "資本効率の評価（50〜100文字）",
    "improvement_area": "改善すべき点（50〜100文字、あれば）",
    "conclusion": "総合的な結論（50〜100文字）"
}}
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)
        result["id"] = "roic"
        result["title"] = "ROIC（投下資本利益率）AI評価"
        result["score"] = fallback["score"]
        result["max_score"] = 15
        result["rating"] = rating
        result["summary"] = result.get("conclusion", "")
        result["details"] = []
        result["warnings"] = []
        if roic and roic < 0.10:
            result["warnings"].append("ROICが低く、資本効率に課題があります。")
        return result
    except Exception:
        return fallback


def generate_owner_earnings_analysis(data: dict, oe_result: dict) -> dict:
    """Owner Earnings分析結果に対するAI評価を生成する（Sprint20）。"""
    company = data.get("company_name", "不明")
    oe = oe_result.get("owner_earnings")
    oe_yield = oe_result.get("owner_earnings_yield")
    net_income = oe_result.get("net_income")
    da = oe_result.get("depreciation_amortization")
    capex = oe_result.get("capital_expenditures")
    rating = oe_result.get("rating", "unknown")

    if oe is None:
        return {
            "id": "owner_earnings",
            "title": "Owner Earnings（オーナーアーニングス）AI評価",
            "score": 0,
            "max_score": 10,
            "rating": "unknown",
            "summary": f"{company}のOwner Earningsを計算するためのデータが不足しています。",
            "details": [],
            "warnings": ["データ不足のためAI評価を生成できませんでした。"],
            "buffet_view": "評価できません。",
        }

    fallback_score = min(int(oe_yield * 100 / 8 * 10), 10) if oe_yield and oe_yield > 0 else 0
    fallback = {
        "id": "owner_earnings",
        "title": "Owner Earnings（オーナーアーニングス）AI評価",
        "score": fallback_score,
        "max_score": 10,
        "rating": rating,
        "summary": f"{company}のOwner Earningsは{oe:,.0f}（利回り{f'{oe_yield*100:.1f}%' if oe_yield is not None else 'N/A'}、{rating}）です。",
        "details": [],
        "warnings": [],
        "buffet_view": f"Owner Earnings {oe:,.0f}は、{company}の実質的な現金創出力を示しています。",
        "conclusion": f"Owner Earnings {rating}",
    }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback

    prompt = f"""あなたはウォーレン・バフェットの投資スタイルを模倣したAIアナリストです。

{company}のOwner Earnings（オーナーアーニングス）分析結果をバフェット視点で評価してください。

## 分析データ
- Owner Earnings: {f'{oe:,.0f}' if oe is not None else 'N/A'}
- Owner Earnings利回り（対時価総額）: {f'{oe_yield*100:.1f}%' if oe_yield is not None else 'N/A'}
- 当期純利益: {f'{net_income:,.0f}' if net_income is not None else 'N/A'}
- 減価償却費等（D&A、推定）: {f'{da:,.0f}' if da is not None else 'N/A'}
- 設備投資（CapEx、推定）: {f'{capex:,.0f}' if capex is not None else 'N/A'}
- 評価: {rating}

## 評価基準（バフェット）
Owner Earnings = 当期純利益 + 減価償却費等 − 設備投資
会計上の利益ではなく、株主が実質的に自由に使える現金創出力を示す指標。
- 利回り8%以上: 極めて高い株主価値創出力
- 利回り5%以上: 良好な現金創出力
- 利回り3%以上: 平均的な水準
- 利回り3%未満: 現金創出力に課題

## 出力形式（JSON）
{{
    "buffet_view": "バフェット視点での洞察（100〜200文字）",
    "competitive_advantage": "利益の質（会計上の利益との乖離）についての評価（50〜100文字）",
    "capital_efficiency": "設備投資負担についての評価（50〜100文字）",
    "improvement_area": "改善すべき点（50〜100文字、あれば）",
    "conclusion": "総合的な結論（50〜100文字）"
}}
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)
        result["id"] = "owner_earnings"
        result["title"] = "Owner Earnings（オーナーアーニングス）AI評価"
        result["score"] = fallback_score
        result["max_score"] = 10
        result["rating"] = rating
        result["summary"] = result.get("conclusion", "")
        result["details"] = []
        result["warnings"] = []
        if oe_yield is not None and oe_yield < 0.03:
            result["warnings"].append("Owner Earnings利回りが低く、実質的な現金創出力に課題があります。")
        return result
    except Exception:
        return fallback

def generate_intrinsic_value_analysis(data: dict, intrinsic_raw: dict) -> dict:
    """
    Sprint21: Intrinsic Value分析のAI考察を生成する。
    ROIC / Owner Earningsと同じく、ルールベースの数値(raw)は上書きせず、
    Geminiの考察（buffet_view 等）だけを返す。AI不可時はfallback。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    consensus = intrinsic_raw.get("consensus_intrinsic_value_per_share")
    current_price = intrinsic_raw.get("current_price")
    mosp = intrinsic_raw.get("margin_of_safety_pct")

    fallback = {
        "buffet_view": "Intrinsic Value（内在価値）分析のAI考察は利用できませんでした。",
        "competitive_advantage": "ルールベースの評価を参照してください。",
        "capital_efficiency": "ルールベースの評価を参照してください。",
        "improvement_area": "複数方式の推定値が大きく乖離する場合は、前提（成長率・割引率）を見直してください。",
        "conclusion": intrinsic_raw.get("summary", "データ不足"),
    }

    if not api_key:
        return fallback

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知した投資アナリストです。

以下の企業のIntrinsic Value（内在価値）分析結果を、バフェットの視点から簡潔に考察してください。

会社名：{data.get("company_name")}

コンセンサス内在価値（1株）：{f"{consensus:,.2f}" if consensus is not None else "N/A"}
現在株価：{f"{current_price:,.2f}" if current_price is not None else "N/A"}
安全余裕(Margin of Safety)：{f"{mosp:+.1f}%" if mosp is not None else "N/A"}
判定：{intrinsic_raw.get("verdict", "N/A")}

各方式の推定:
{chr(10).join(f"- {e.get('label','')}: {e.get('value',0):,.2f}（{e.get('detail','')}）" for e in intrinsic_raw.get("estimates", []))}

以下のJSON形式だけで回答してください。
{{
  "buffet_view": "バフェット的視点から100文字以内の所見",
  "competitive_advantage": "50文字以内",
  "capital_efficiency": "50文字以内",
  "improvement_area": "改善点（複数方式の乖離がある場合の見直し等）50文字以内",
  "conclusion": "総合結論 100文字以内"
}}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)
        result["id"] = "intrinsic_value"
        result["title"] = "Intrinsic Value（内在価値）AI評価"
        result["score"] = intrinsic_raw.get("rating", "unknown")
        result["max_score"] = 15
        result["rating"] = intrinsic_raw.get("rating", "unknown")
        result["summary"] = result.get("conclusion", "")
        result["details"] = []
        result["warnings"] = []
        if mosp is not None and mosp < 0:
            result["warnings"].append("安全余裕がありません。価格が内在価値を上回っています。")
        return result
    except Exception:
        return fallback


def generate_capital_allocation_analysis(data: dict, capital_allocation_raw: dict) -> dict:
    """
    Sprint22: Capital Allocation分析のAI考察を生成する。
    ROIC / Owner Earnings / Intrinsic Value と同じく、ルールベースの数値(raw)は上書きせず、
    Geminiの考察（buffet_view 等）だけを返す。AI不可時はfallback。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    total_score = capital_allocation_raw.get("total_score", 0)
    max_score = capital_allocation_raw.get("max_score", 10)
    rating = capital_allocation_raw.get("rating", "unknown")

    fallback = {
        "buffet_view": "Capital Allocation（資本配分）分析のAI考察は利用できませんでした。",
        "competitive_advantage": "ルールベースの評価を参照してください。",
        "capital_efficiency": "ルールベースの評価を参照してください。",
        "improvement_area": "再投資効率・配当性向・自社株買いタイミングの3軸で経営者の資本配分判断を確認してください。",
        "conclusion": capital_allocation_raw.get("summary", "データ不足"),
    }

    if not api_key:
        return fallback

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知した投資アナリストです。

以下の企業のCapital Allocation（資本配分）分析結果を、バフェットの視点から簡潔に考察してください。

会社名：{data.get("company_name")}

資本配分スコア：{total_score} / {max_score}点
評価：{rating}
所見：{capital_allocation_raw.get("summary", "")}

再投資効率（ROIC基準）：{capital_allocation_raw.get("reinvestment_detail", "")}
株主還元の規律（配当性向）：{capital_allocation_raw.get("payout_detail", "")}
自社株買いのタイミング（MOSとの突合）：{capital_allocation_raw.get("buyback_detail", "")}

以下のJSON形式だけで回答してください。
{{
  "buffet_view": "バフェット的視点から100文字以内の所見（経営者の資本配分能力は企業価値の鍵）",
  "competitive_advantage": "50文字以内",
  "capital_efficiency": "50文字以内",
  "improvement_area": "改善点 50文字以内",
  "conclusion": "総合結論 100文字以内"
}}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)
        result["id"] = "capital_allocation"
        result["title"] = "Capital Allocation（資本配分）AI評価"
        result["score"] = total_score
        result["max_score"] = max_score
        result["rating"] = rating
        result["summary"] = result.get("conclusion", "")
        result["details"] = []
        result["warnings"] = []
        if total_score < 6:
            result["warnings"].append("資本配分スコアが低く、経営者の資本配分判断に課題があります。")
        return result
    except Exception:
        return fallback


def generate_share_buyback_analysis(data: dict, share_buyback_raw: dict) -> dict:
    """
    Sprint23: Share Buyback（自社株買い）分析のAI考察を生成する。
    ROIC / Owner Earnings / Intrinsic Value / Capital Allocation と同じく、
    ルールベースの数値(raw)は上書きせず、Geminiの考察（buffet_view 等）だけを返す。
    AI不可時はfallback。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    total_score = share_buyback_raw.get("total_score", 0)
    max_score = share_buyback_raw.get("max_score", 10)
    rating = share_buyback_raw.get("rating", "unknown")

    fallback = {
        "buffet_view": "Share Buyback（自社株買い）分析のAI考察は利用できませんでした。",
        "competitive_advantage": "ルールベースの評価を参照してください。",
        "capital_efficiency": "ルールベースの評価を参照してください。",
        "improvement_area": "一貫性・株式数減少効果・財務健全性・PER水準の4軸で確認してください。",
        "conclusion": share_buyback_raw.get("summary", "データ不足"),
    }

    if not api_key:
        return fallback

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知した投資アナリストです。

以下の企業のShare Buyback（自社株買い）分析結果を、バフェットの視点から簡潔に考察してください。
Capital Allocation分析（別軸、自社株買いのタイミングをMOSで評価済み）とは異なり、
ここでは自社株買いそのものの質・効果・一貫性を評価しています。

会社名：{data.get("company_name")}

自社株買いスコア：{total_score} / {max_score}点
評価：{rating}
所見：{share_buyback_raw.get("summary", "")}

買い入れの一貫性：{share_buyback_raw.get("consistency_detail", "")}
発行済株式数の減少効果：{share_buyback_raw.get("reduction_detail", "")}
財務健全性とのバランス：{share_buyback_raw.get("balance_detail", "")}
買い入れの効果的なタイミング（PER水準）：{share_buyback_raw.get("timing_detail", "")}

以下のJSON形式だけで回答してください。
{{
  "buffet_view": "バフェット的視点から100文字以内の所見（自社株買いは価値ある時にのみ行うべき）",
  "competitive_advantage": "50文字以内",
  "capital_efficiency": "50文字以内",
  "improvement_area": "改善点 50文字以内",
  "conclusion": "総合結論 100文字以内"
}}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)
        result["id"] = "share_buyback"
        result["title"] = "Share Buyback（自社株買い）AI評価"
        result["score"] = total_score
        result["max_score"] = max_score
        result["rating"] = rating
        result["summary"] = result.get("conclusion", "")
        result["details"] = []
        result["warnings"] = []
        if total_score < 6:
            result["warnings"].append("自社株買いスコアが低く、質・効果・一貫性に課題があります。")
        return result
    except Exception:
        return fallback


def generate_debt_quality_analysis(data: dict, debt_quality_raw: dict) -> dict:
    """
    Sprint24: Debt Quality（負債の質）分析のAI考察を生成する。
    ROIC / Owner Earnings / Intrinsic Value / Capital Allocation / Share Buyback と
    同じく、ルールベースの数値(raw)は上書きせず、Geminiの考察（buffet_view 等）
    だけを返す。AI不可時はfallback。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    total_score = debt_quality_raw.get("total_score", 0)
    max_score = debt_quality_raw.get("max_score", 10)
    rating = debt_quality_raw.get("rating", "unknown")

    fallback = {
        "buffet_view": "Debt Quality（負債の質）分析のAI考察は利用できませんでした。",
        "competitive_advantage": "ルールベースの評価を参照してください。",
        "capital_efficiency": "ルールベースの評価を参照してください。",
        "improvement_area": "負債水準・金利負担能力・負債構成・トレンドの4軸で確認してください。",
        "conclusion": debt_quality_raw.get("summary", "データ不足"),
    }

    if not api_key:
        return fallback

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
あなたはウォーレン・バフェットの投資哲学を熟知した投資アナリストです。

以下の企業のDebt Quality（負債の質）分析結果を、バフェットの視点から簡潔に考察してください。
Share Buyback分析（別軸、負債の「量」の推移は評価済み）とは異なり、
ここでは負債の「質」＝返済能力・構成・リスクを評価しています。
バフェットは保守的な財務体質と過度なレバレッジの回避を重視します。

会社名：{data.get("company_name")}

負債の質スコア：{total_score} / {max_score}点
評価：{rating}
所見：{debt_quality_raw.get("summary", "")}

負債水準の適正さ：{debt_quality_raw.get("level_detail", "")}
金利負担能力：{debt_quality_raw.get("coverage_detail", "")}
負債の質・構成：{debt_quality_raw.get("composition_detail", "")}
負債推移のトレンド：{debt_quality_raw.get("trend_detail", "")}

以下のJSON形式だけで回答してください。
{{
  "buffet_view": "バフェット的視点から100文字以内の所見（保守的な財務体質を重視）",
  "competitive_advantage": "50文字以内",
  "capital_efficiency": "50文字以内",
  "improvement_area": "改善点 50文字以内",
  "conclusion": "総合結論 100文字以内"
}}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)
        result["id"] = "debt_quality"
        result["title"] = "Debt Quality（負債の質）AI評価"
        result["score"] = total_score
        result["max_score"] = max_score
        result["rating"] = rating
        result["summary"] = result.get("conclusion", "")
        result["details"] = []
        result["warnings"] = []
        if total_score < 6:
            result["warnings"].append("負債の質スコアが低く、返済能力または構成のリスクに課題があります。")
        return result
    except Exception:
        return fallback
