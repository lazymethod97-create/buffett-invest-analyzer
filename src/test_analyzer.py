from financial_analyzer import FinancialAnalyzer

analyzer = FinancialAnalyzer()

# AppleのROE（約141%）
rating, score = analyzer.evaluate_roe(1.4147099)

print("ROE評価")
print("星評価 :", rating)
print("点数   :", score)

