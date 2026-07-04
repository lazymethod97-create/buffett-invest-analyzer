"""
financial_analyzer.py

役割：
ウォーレン・バフェットの投資基準に基づいて
財務指標を評価する。
"""


class FinancialAnalyzer:

    def evaluate(self, metric, value):
        """
        財務指標を評価する

        戻り値
        -------
        (星評価, 点数)
        """

        if value is None:
            return ("評価不可", 0)

        # ROE（0.20 = 20%）
        if metric == "ROE":
            value = value * 100

            if value >= 20:
                return ("★★★★★", 25)
            elif value >= 15:
                return ("★★★★☆", 20)
            elif value >= 10:
                return ("★★★☆☆", 15)
            elif value >= 5:
                return ("★★☆☆☆", 10)
            else:
                return ("★☆☆☆☆", 5)

        # PER
        elif metric == "PER":

            if value <= 15:
                return ("★★★★★", 20)
            elif value <= 20:
                return ("★★★★☆", 16)
            elif value <= 30:
                return ("★★★☆☆", 12)
            elif value <= 40:
                return ("★★☆☆☆", 8)
            else:
                return ("★☆☆☆☆", 4)

        # PBR
        elif metric == "PBR":

            if value <= 3:
                return ("★★★★★", 15)
            elif value <= 5:
                return ("★★★★☆", 12)
            elif value <= 8:
                return ("★★★☆☆", 9)
            elif value <= 10:
                return ("★★☆☆☆", 6)
            else:
                return ("★☆☆☆☆", 3)

        return ("未対応", 0)
