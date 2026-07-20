import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_company(company_name):

    prompt = f"""
あなたはウォーレン・バフェットです。

以下の企業を分析してください。

企業名
{company_name}

以下の形式だけで回答してください。

【企業概要】

【強み】

【弱み】

【競争優位性】

【Buffett評価】
★1〜5

【投資判断】
100文字以内
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text