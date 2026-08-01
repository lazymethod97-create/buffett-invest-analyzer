"""financial_table: 主要財務指標テーブルの描画 (Sprint18)"""
import streamlit as st
import pandas as pd


def render_financial_table(data: dict) -> None:
    """data: get_stock_data() の戻り値から主要指標を表形式で表示する。"""
    rows = [
        ("会社名", data.get("company_name", "-")),
        ("セクター", data.get("sector", "-")),
        ("ROE", data.get("roe")),
        ("ROA", data.get("roa")),
        ("営業利益率", data.get("operating_margin")),
        ("D/E", data.get("debt_to_equity")),
        ("PER", data.get("pe_ratio")),
        ("PBR", data.get("pb_ratio")),
        ("フリーキャッシュフロー", data.get("free_cashflow")),
        ("売上成長率", data.get("revenue_growth")),
        ("配当利回り", data.get("dividend_yield")),
    ]
    df = pd.DataFrame(rows, columns=["指標", "値"])
    st.dataframe(df, use_container_width=True)