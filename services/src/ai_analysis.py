import os
from google import genai


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
        return "Gemini APIキーが設定されていません。"

    try:
        client = genai.Client(api_key=api_key)
        news_text = ""
        for article in news:
            # for の内部は必ずインデントする（スペース4つ推奨）
            news_text += f"タイトル: {article['title']}\n"

        prompt = f"""
        あなたはウォーレン・バフェットの投資アナリストです。
        以下は企業の最新ニュースです。
        {news_text}
        次の形式で日本語で回答してください。
        【ニュース要約】 150文字以内
        【株価への短期影響】
        【長期投資への影響】
        【Buffett視点】
        ★★★★★で重要度も付けてください。
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text

    except Exception as e:
        return str(e)
