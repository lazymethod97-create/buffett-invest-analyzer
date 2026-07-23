import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

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
		return "Gemini APIキーが設定されていません。"

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

	except Exception as e:
		return str(e)


def generate_buffett_checklist(data, score_result):
	"""
	Buffett Investment Checklist を生成する。
	APIキーがあればGeminiに依頼し、なければルールベースで返す。
	"""
	api_key = os.getenv("GEMINI_API_KEY")
	if not api_key:
		return _generate_rule_checklist(data, score_result)

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
		return _generate_rule_checklist(data, score_result)


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

