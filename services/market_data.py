# services/market_data.py

def get_financial_data(ticker: str):
    """
    指定されたティッカーの財務データを取得する関数（テスト用スタブ）
    """
    print(f"DEBUG: get_financial_data が {ticker} で呼び出されました。")
    
    # テスト用のダミーデータ（エラーが出なくなったら実際のAPI処理などに書き換えてください）
    return {
        "ticker": ticker,
        "roe": 15.5,
        "eps": 5.20,
        "debt_to_equity": 0.4
    }
