####################################################
# earnings_material.py
# Sprint17: 決算資料解析
#
# PDFファイル（決算説明資料など）からテキストを抽出する処理だけを担当する。
# 抽出したテキストをGeminiに渡して要約・分析する処理は、
# 既存のGemini呼び出しと同じ場所に統一するため、ai_analysis.py側
# （generate_earnings_material_analysis）で行う。
#
# 新規ライブラリ pdfplumber を使用する（requirements.txtへの追加が必要）。
####################################################

import io

import pdfplumber


def extract_text_from_pdf(file_bytes):
	"""PDFファイル（バイト列）からテキストを抽出する。

	Args:
		file_bytes (bytes): アップロードされたPDFファイルの中身
			（Streamlitのst.file_uploaderで取得したファイルの.read()の結果）

	Returns:
		str: 抽出されたテキスト（ページごとに改行2つで連結）。
			画像のみのPDF等でテキストが取得できないページは無視する。
	"""
	text_parts = []
	with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
		for page in pdf.pages:
			page_text = page.extract_text()
			if page_text:
				text_parts.append(page_text)
	return "\n\n".join(text_parts)