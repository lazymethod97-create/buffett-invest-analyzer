from financial_analyzer import FinancialAnalyzer
from buffett_score import BuffettScore

analyzer = FinancialAnalyzer()
score_engine = BuffettScore()

test_data = {
    "ROE": 1.4147099,
    "PER": 37.319225,
    "PBR": 42.511017,
}

scores = []

print("=" * 40)
print("Buffett Investment Analyzer")
print("=" * 40)

for metric, value in test_data.items():

    rating, score = analyzer.evaluate(metric, value)

    scores.append(score)

    print(f"\n{metric}")
    print(f"値      : {value}")
    print(f"評価    : {rating}")
    print(f"点数    : {score}")

print("\n" + "-" * 40)

result = score_engine.calculate(scores)

print("\nBuffett Score")
print(f"{result['total']} 点")
print(result["rating"])

print("\n判定")
print(result["message"])
