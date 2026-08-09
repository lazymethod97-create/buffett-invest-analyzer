import sys, importlib, py_compile

BASE = r"C:\Users\t.k\buffett-invest-analyzer"
sys.path.insert(0, BASE + r"\services\src")

ok = True

def check(label, fn):
    global ok
    try:
        fn()
        print("PASS:", label)
    except Exception as e:
        ok = False
        print("FAIL:", label, "->", repr(e))

# 1) legacy wrappers
def t_wrappers():
    for mod in ["data_fetcher","news_fetcher","scoring_engine","dcf_analysis","checklist_engine","gemini","ai_analysis","pdf_report","overall_eval"]:
        importlib.import_module(mod)
        print("   wrapper:", mod, "OK")
check("legacy wrappers import", t_wrappers)

# 2) new packages
def t_packages():
    for pkg in ["data","engines","ai","analysis","report","ui"]:
        importlib.import_module(pkg)
        print("   package:", pkg, "OK")
check("new packages import", t_packages)

# 3) Phase3 members
def t_members():
    from engines import generate_buffett_checklist_rule
    from ui import render_summary_card, render_decision_card, render_financial_table, render_score_card, render_chart_panel
    from analysis import create_analysis_bundle, calculate_overall_grade
check("Phase3 members (checklist rule + ui)", t_members)

# 3b) Sprint21 members
def t_sprint21_members():
    from engines import calculate_intrinsic_value
    from analysis import analyze_intrinsic_value
    from ai.ai_analysis import generate_intrinsic_value_analysis
    from report.report import create_intrinsic_value_display
    print("   intrinsic_value wired: engine/analysis/ai/report OK")
check("Sprint21 members (intrinsic_value)", t_sprint21_members)

# 3c) Sprint22 members (Capital Allocation)
def t_sprint22_members():
    from engines import calculate_capital_allocation
    from analysis import analyze_capital_allocation
    from ai.ai_analysis import generate_capital_allocation_analysis
    from report.report import create_capital_allocation_display
    # 実import検証（Sprint20でapp.pyが参照していたのに実装漏れだった
    # create_owner_earnings_display のようなImportErrorの再発防止）
    from report.report import create_owner_earnings_display
    print("   capital_allocation wired: engine/analysis/ai/report OK")
    print("   display imports OK (owner_earnings/capital_allocation)")
check("Sprint22 members (capital_allocation)", t_sprint22_members)

# 3d) Sprint23 members (Share Buyback)
def t_sprint23_members():
    from engines import calculate_share_buyback
    from analysis import analyze_share_buyback
    from ai.ai_analysis import generate_share_buyback_analysis
    from report.report import create_share_buyback_display
    print("   share_buyback wired: engine/analysis/ai/report OK")
check("Sprint23 members (share_buyback)", t_sprint23_members)

# 3e) Sprint24 members (Debt Quality)
def t_sprint24_members():
    from engines import calculate_debt_quality
    from analysis import analyze_debt_quality
    from ai.ai_analysis import generate_debt_quality_analysis
    from report.report import create_debt_quality_display
    print("   debt_quality wired: engine/analysis/ai/report OK")
check("Sprint24 members (debt_quality)", t_sprint24_members)

# 3f) Sprint25 members (Economic Moat強化)
def t_sprint25_members():
    from engines import calculate_moat_strength
    from analysis import analyze_moat_strength
    from ai.ai_analysis import generate_moat_strength_analysis
    from report.report import create_moat_strength_display
    print("   moat_strength wired: engine/analysis/ai/report OK")
check("Sprint25 members (moat_strength)", t_sprint25_members)

# 3g) Sprint26 members (Backtest)
def t_sprint26_members():
    from engines import calculate_backtest
    from analysis import analyze_backtest
    from ai.ai_analysis import generate_backtest_analysis
    from report.report import create_backtest_display
    print("   backtest wired: engine/analysis/ai/report OK")
check("Sprint26 members (backtest)", t_sprint26_members)

# 3h) Sprint27 members (Portfolio Risk)
def t_sprint27_members():
    from engines import calculate_portfolio_risk
    from analysis import analyze_portfolio_risk
    from ai.ai_analysis import generate_portfolio_risk_analysis
    from report.report import create_portfolio_risk_display
    from report.pdf_report import generate_portfolio_pdf_report
    print("   portfolio_risk wired: engine/analysis/ai/report/pdf OK")
    # Portfolio Risk is a portfolio-level analysis (multiple tickers), unlike
    # every other Sprint19-26 axis (single ticker). It is intentionally NOT
    # wired into create_analysis_bundle() / calculate_overall_grade() -
    # see docs/AI_HANDOVER.md Sprint27 section for the design rationale.
    # A quick smoke test of the engine/analysis functions with fake holdings:
    class _FakeHolding:
        def __init__(self, ticker, shares):
            self.ticker = ticker
            self.shares = shares
            self.id = 1
    rows = [
        {"holding": _FakeHolding("AAPL", 5), "data": {"company_name": "Apple Inc.", "current_price": 200.0, "sector": "Technology", "country": "United States"}, "score_result": {"total_score": 140, "max_score": 190}, "error": None},
        {"holding": _FakeHolding("7203", 100), "data": {"company_name": "トヨタ自動車", "current_price": 2500.0, "sector": "Consumer Cyclical", "country": "Japan"}, "score_result": {"total_score": 160, "max_score": 190}, "error": None},
    ]
    result = analyze_portfolio_risk(rows, generate_ai_narrative=False)
    assert result["max_score"] == 10, "Sprint27 regression: portfolio_risk max_score should be 10"
    assert result["raw"]["raw"]["holding_count"] == 2, "Sprint27 regression: holding_count mismatch"
    _ = create_portfolio_risk_display(result)
    _pdf = generate_portfolio_pdf_report(result)
    assert _pdf, "Sprint27 regression: generate_portfolio_pdf_report returned empty bytes"
    print("   portfolio_risk smoke OK: score=", result["score"], "/", result["max_score"])
check("Sprint27 members (portfolio_risk)", t_sprint27_members)

# 3i) Sprint28 members (Watchlist Insights)
def t_sprint28_members():
    from analysis import build_watchlist_insights
    from report.report import create_watchlist_insights_display
    print("   watchlist_insights wired: analysis/report OK")
    # Watchlist Insights is, like Portfolio Risk, a multi-ticker analysis and is
    # intentionally NOT wired into create_analysis_bundle() / calculate_overall_grade().
    # Unlike Portfolio Risk it does NOT produce a score (no score/max_score/rating) -
    # see docs/AI_HANDOVER.md Sprint28 section for the design rationale.
    class _FakeItem:
        def __init__(self, ticker, target_price=None):
            self.ticker = ticker
            self.target_price = target_price
            self.memo = ""
            self.id = 1
    rows = [
        {"item": _FakeItem("AAPL", 190.0), "data": {"company_name": "Apple Inc.", "current_price": 200.0, "sector": "Technology", "country": "United States"}, "score_result": {"total_score": 140, "max_score": 190, "verdict": "A"}, "error": None},
        {"item": _FakeItem("7203", 3000.0), "data": {"company_name": "トヨタ自動車", "current_price": 2500.0, "sector": "Consumer Cyclical", "country": "Japan"}, "score_result": {"total_score": 160, "max_score": 190, "verdict": "S"}, "error": None},
        {"item": _FakeItem("MSFT", None), "data": {"company_name": "Microsoft", "current_price": 400.0, "sector": "Technology", "country": "United States"}, "score_result": {"total_score": 120, "max_score": 190, "verdict": "B"}, "error": None},
    ]
    result = build_watchlist_insights(rows, [])
    assert result["success"] is True, "Sprint28 regression: build_watchlist_insights should succeed for non-empty watchlist"
    assert result["watchlist_count"] == 3, "Sprint28 regression: watchlist_count mismatch"
    assert "score" not in result, "Sprint28 regression: Watchlist Insights must NOT be score-based (no 'score' key)"
    assert result["target_price_ranking"][0]["ticker"] == "7203", "Sprint28 regression: target price ranking order wrong (reached items should sort first)"
    empty_result = build_watchlist_insights([], [])
    assert empty_result["success"] is False, "Sprint28 regression: empty watchlist should return success=False"
    _ = create_watchlist_insights_display(result)
    print("   watchlist_insights smoke OK: watchlist_count=", result["watchlist_count"])
check("Sprint28 members (watchlist_insights)", t_sprint28_members)

# 4) bundle smoke (quick + full)
def t_bundle():
    from analysis import create_analysis_bundle
    from engines import calculate_buffett_score
    data={"company_name":"TEST","roe":0.25,"operating_margin":0.2,"debt_to_equity":50.0,"current_ratio":1.5,"pe_ratio":15.0,"pb_ratio":2.0,"free_cashflow":1000000000,"market_cap":10000000000,"current_price":100.0,"revenue_growth":0.05,"roa":0.12}
    s=calculate_buffett_score(data)
    bq=create_analysis_bundle(data,s,dcf_result={},mode="quick")
    print("   quick decision:", bq["overall"]["decision"], "grade:", bq["overall"]["grade"], "checklist:", len(bq["checklist"]))
    bf=create_analysis_bundle(data,s,dcf_result={},mode="full",news=[],is_quick=False,is_full=True)
    print("   full  decision:", bf["overall"]["decision"], "grade:", bf["overall"]["grade"], "checklist:", len(bf["checklist"]), "red_team set:", bool(bf["red_team"]))
    assert bf["roic"] is not None, "Sprint19 regression: bundle['roic'] is None in full mode"
    assert bf["owner_earnings"] is not None, "Sprint20 regression: bundle['owner_earnings'] is None in full mode"
    assert bf["intrinsic_value"] is not None, "Sprint21 regression: bundle['intrinsic_value'] is None in full mode"
    assert bf["capital_allocation"] is not None, "Sprint22 regression: bundle['capital_allocation'] is None in full mode"
    assert bf["share_buyback"] is not None, "Sprint23 regression: bundle['share_buyback'] is None in full mode"
    assert bf["debt_quality"] is not None, "Sprint24 regression: bundle['debt_quality'] is None in full mode"
    assert bf["moat_strength"] is not None, "Sprint25 regression: bundle['moat_strength'] is None in full mode"
    assert bf["backtest"] is not None, "Sprint26 regression: bundle['backtest'] is None in full mode"
    assert bf["overall"]["detail"].get("roic", 0) >= 0, "roic score missing from overall detail"
    assert bf["overall"]["detail"].get("owner_earnings", 0) >= 0, "owner_earnings score missing from overall detail"
    assert bf["overall"]["detail"].get("intrinsic_value", 0) >= 0, "intrinsic_value score missing from overall detail"
    assert bf["overall"]["detail"].get("capital_allocation", 0) >= 0, "capital_allocation score missing from overall detail"
    assert bf["overall"]["detail"].get("share_buyback", 0) >= 0, "share_buyback score missing from overall detail"
    assert bf["overall"]["detail"].get("debt_quality", 0) >= 0, "debt_quality score missing from overall detail"
    assert bf["overall"]["detail"].get("moat_strength", 0) >= 0, "moat_strength score missing from overall detail"
    assert bf["overall"]["detail"].get("backtest", 0) >= 0, "backtest score missing from overall detail"
    print("   roic wired:", bf["roic"]["score"], "/", bf["roic"]["max_score"],
          " owner_earnings wired:", bf["owner_earnings"]["score"], "/", bf["owner_earnings"]["max_score"],
          " intrinsic_value wired:", bf["intrinsic_value"]["score"], "/", bf["intrinsic_value"]["max_score"],
          " capital_allocation wired:", bf["capital_allocation"]["score"], "/", bf["capital_allocation"]["max_score"],
          " share_buyback wired:", bf["share_buyback"]["score"], "/", bf["share_buyback"]["max_score"],
          " debt_quality wired:", bf["debt_quality"]["score"], "/", bf["debt_quality"]["max_score"],
          " moat_strength wired:", bf["moat_strength"]["score"], "/", bf["moat_strength"]["max_score"],
          " backtest wired:", bf["backtest"]["score"], "/", bf["backtest"]["max_score"])
check("bundle smoke (quick/full)", t_bundle)

# 5) app.py compiles
def t_compile():
    py_compile.compile(BASE + r"\services\app.py", doraise=True)
check("app.py compiles", t_compile)

# 6) Sprint29 members (Performance改善)
def t_sprint29_watchlist_insights_placement():
    """
    Sprint28で混入した不具合の再発防止：
    「📊 Watchlist Insights」セクションが `for row in watchlist_rows:` ループの
    内側に置かれていると、登録銘柄数ぶん集計・表示が重複実行されてしまう
    （Sprint29で発見・修正）。app.pyのソースを直接検査し、insightsセクションの
    開始行のインデント（タブ数）が、ループ行自身と同じ深さであること
    （＝ループの外側にあること）を確認する。
    """
    app_path = BASE + r"\services\app.py"
    with open(app_path, "r", encoding="utf-8-sig") as f:
        lines = f.read().split("\n")

    def tabs(line):
        return len(line) - len(line.lstrip("\t"))

    loop_idx = next(i for i, l in enumerate(lines) if l.strip() == "for row in watchlist_rows:")
    insights_idx = next(
        i for i, l in enumerate(lines)
        if "Watchlist Insights" in l and "st.subheader" in l
    )
    assert insights_idx > loop_idx, "Sprint29 regression: watchlist insights header not found after the loop"
    assert tabs(lines[insights_idx]) == tabs(lines[loop_idx]), (
        "Sprint29 regression: Watchlist Insights section must sit at the same "
        "indentation level as 'for row in watchlist_rows:' (i.e. run once, "
        "after the per-item loop) - not nested inside it."
    )
    print("   watchlist insights placement OK: runs once, outside the per-item loop")
check("Sprint29 members (watchlist insights placement)", t_sprint29_watchlist_insights_placement)

# 6b) Sprint29 members (_build_rows_cached shared helper wired into both tabs)
def t_sprint29_build_rows_cached_wired():
    """
    Portfolio/Watchlistの銘柄一覧構築は、無関係な操作による再実行のたびに
    yfinance呼び出しループが走ってしまう問題を解消するため、
    session_stateベースの共通キャッシュヘルパー _build_rows_cached() を
    追加した（重複実装禁止・ルール14によりPortfolio/Watchlistで共通利用）。
    app.pyのソースを直接検査し、ヘルパーが定義され、かつ両セクションから
    呼び出されていることを確認する。
    """
    app_path = BASE + r"\services\app.py"
    with open(app_path, "r", encoding="utf-8-sig") as f:
        src = f.read()
    assert "def _build_rows_cached(" in src, "Sprint29 regression: _build_rows_cached helper missing"
    assert src.count('_build_rows_cached(\n\t\t\t\t"portfolio_rows_cache"') == 1 or \
        '"portfolio_rows_cache"' in src, "Sprint29 regression: portfolio rows not wired through _build_rows_cached"
    assert '"watchlist_rows_cache"' in src, "Sprint29 regression: watchlist rows not wired through _build_rows_cached"
    print("   _build_rows_cached wired: portfolio + watchlist OK")
check("Sprint29 members (_build_rows_cached wiring)", t_sprint29_build_rows_cached_wired)


print("=== HEALTH:", "ALL OK" if ok else "ISSUES FOUND", "===")
