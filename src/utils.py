import re


def normalize_ticker(symbol: str) -> str:

    symbol = symbol.strip().upper()

    if re.fullmatch(r"\d{4}", symbol):
        return f"{symbol}.T"

    return symbol


print(normalize_ticker("7203"))
print(normalize_ticker("AAPL"))