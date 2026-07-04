"""
financial_analyzer.py

役割：
財務データをウォーレン・バフェットの投資基準で評価する。
"""


class FinancialAnalyzer:

    def evaluate_roe(self, roe):

        if roe is None:
            return ("評価不可", 0)

        # Yahoo Finance は 0.20 = 20%
        roe_percent = roe * 100

        if roe_percent >= 20:
            return ("★★★★★", 25)

        elif roe_percent >= 15:
            return ("★★★★☆", 20)

        elif roe_percent >= 10:
            return ("★★★☆☆", 15)

        elif roe_percent >= 5:
            return ("★★☆☆☆", 10)

        else:
            return ("★☆☆☆☆", 5)
