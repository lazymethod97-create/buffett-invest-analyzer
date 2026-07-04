"""
buffett_score.py

役割：
財務指標の点数を合計し、
Buffett Score を計算する。
"""


class BuffettScore:

    def calculate(self, scores):
        """
        scores : 点数のリスト

        例
        [25, 8, 3]
        """

        total = sum(scores)

        if total >= 80:
            rating = "★★★★★"
            message = "投資候補"

        elif total >= 60:
            rating = "★★★★☆"
            message = "前向きに検討"

        elif total >= 40:
            rating = "★★★☆☆"
            message = "慎重に検討"

        elif total >= 20:
            rating = "★★☆☆☆"
            message = "様子見"

        else:
            rating = "★☆☆☆☆"
            message = "見送り候補"

        return {
            "total": total,
            "rating": rating,
            "message": message
        }
