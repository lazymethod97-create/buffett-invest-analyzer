
from data_fetcher import StockDataFetcher


def main():
	symbol = input("銘柄コードを入力してください（例：AAPL または 7203）：")

	fetcher = StockDataFetcher(symbol)

	data = fetcher.fetch()

	print("\n===== 取得結果 =====")

	for key, value in data.items():
		print(f"{key}: {value}")


if __name__ == "__main__":
	main()
