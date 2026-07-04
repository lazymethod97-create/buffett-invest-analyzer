from financial_analyzer import FinancialAnalyzer

analyzer = FinancialAnalyzer()

test_data = {
    "ROE": 1.4147099,
    "PER": 37.319225,
    "PBR": 42.511017,
}

print("=" * 40)
print("Buffett Analyzer Test")
print("=" * 40)

for metric, value in test_data.items():
    rating, score = analyzer.evaluate(metric, value)

    print(f"{metric}")
    print(f"値      : {value}")
    print(f"評価    : {rating}")
    print(f"点数    : {score}")
    print("-" * 40)
