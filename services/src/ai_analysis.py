import os
from openai import OpenAI


def generate_ai_analysis(data, score_result):
    """
    OpenAI APIが設定されていればGPTで分析、
    設定されていなければルールベース分析を返す。
    """

    api_key = os.getenv("OPENAI_API_KEY")

    # APIキーが無い場合
    if not api_key:
        return generate_rule_analysis(data, score_result)

    try:
        client = OpenAI(api_key=api_key)

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

        response = client.responses.create(
            model="gpt-5",
            input=prompt,
        )

        return response.output_text

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

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:

        return "OpenAI APIキーが設定されていないためニュース要約は利用できません。"

    try:

        client = OpenAI(api_key=api_key)

        titles = ""

        for article in news:
            titles += f"- {article['title']}\n"

        prompt = f"""
あなたはプロの証券アナリストです。

以下は企業の最新ニュースです。

{titles}

300文字以内で

・最近何が起きたか
・株価への影響
・長期投資への影響

を日本語で要約してください。
"""

        response = client.responses.create(
            model="gpt-5",
            input=prompt
        )

        return response.output_text

    except Exception as e:

        return str(e)