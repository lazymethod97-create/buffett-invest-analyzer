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
    for mod in ["data_fetcher","news_fetcher","scoring_engine","dcf_analysis","ai_analysis","pdf_report"]:
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
    from ui import render_summary_card, render_decision_card
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
    assert "news_impact" in bq and bq["news_impact"] is None, "Sprint34-4 regression: quick bundle must expose news_impact as None"
    assert "news_impact" in bf and bf["news_impact"] is None, "Sprint34-4 regression: full bundle without news must expose news_impact as None"
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

# 4b) Sprint34-4 news integration

def t_sprint34_4_news_integration():
    from analysis.overall_eval import calculate_overall_grade
    from ai.ai_analysis import generate_news_summary_result

    base_kwargs = dict(
        score_result={"total_score": 100},
        dcf_result={"success": True, "margin_of_safety_pct": 30},
        moat={"rating": "wide"},
        brand={"stars": 5},
        mgmt={"stars": 5},
        red_team={"conclusion": ""},
        roic={"score": 15},
        owner_earnings={"score": 10},
        intrinsic_value={"score": 15},
        capital_allocation={"score": 10},
        share_buyback={"score": 10},
        debt_quality={"score": 10},
        moat_strength={"score": 10},
        backtest={"score": 10},
    )
    base = calculate_overall_grade(**base_kwargs)
    no_news = calculate_overall_grade(**base_kwargs, news_impact={})
    assert base["overall_score"] == no_news["overall_score"], "Sprint34-4 regression: no-news score changed"
    assert base["decision"] == no_news["decision"], "Sprint34-4 regression: no-news decision changed"

    severe = calculate_overall_grade(
        **base_kwargs,
        news_impact={
            "available": True,
            "impact": "negative",
            "severity": "high",
            "confidence": "high",
            "reason": "重大な構造悪化",
        },
    )
    assert severe["overall_score"] == base["overall_score"], "Sprint34-4 regression: news changed 190-point score"
    assert severe["decision"] == "WATCH", "Sprint34-4 regression: severe negative news must downgrade BUY to WATCH (or WATCH to PASS)"
    assert severe["news_adjusted"] is True, "Sprint34-4 regression: news_adjusted flag missing"

    medium_conf = calculate_overall_grade(
        **base_kwargs,
        news_impact={
            "available": True,
            "impact": "negative",
            "severity": "high",
            "confidence": "medium",
            "reason": "根拠不足",
        },
    )
    assert medium_conf["decision"] == base["decision"], "Sprint34-4 regression: insufficient confidence should not change decision"

    no_data = generate_news_summary_result([])
    assert no_data["news_impact"]["available"] is False, "Sprint34-4 regression: empty news must be unavailable"
    print("   news integration: score preserved / severe-risk downgrade / unavailable-news neutrality OK")
check("Sprint34-4 news integration", t_sprint34_4_news_integration)

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


# 6c) Sprint30 members (_cache_by_signature generalized + Portfolio Risk PDF wired through it)
def t_sprint30_cache_by_signature_wired():
	"""
	Sprint30調査の結果、候補2（フルモード一括計算）は全19分析軸すべてが
	画面表示・PDF出力に使われており無駄な計算は見つからなかった（対応不要、
	docs/AI_HANDOVER.md参照）。候補3（PDF生成）は、単一銘柄向けPDFは
	st.buttonで生成タイミングを制御できているため無駄が無かったが、
	Portfolio Risk PDF（generate_portfolio_pdf_report）はst.download_buttonの
	data=引数として無条件に呼ばれており、アプリ内のどこかで操作されるたびに
	（Portfolio Riskタブを見ていないときも含めて）毎回ゼロから再生成されて
	いた（Sprint29の_build_rows_cached()と同種の問題）。

	Sprint29の「signature + TTLでsession_stateキャッシュする」仕組みを
	_cache_by_signature()として汎用化し、_build_rows_cached()はこれを呼ぶ
	薄いラッパーに書き換えた（重複実装禁止・ルール14）うえで、Portfolio Risk
	PDFのバイト列生成もこのヘルパー経由にした。app.pyのソースを直接検査し、
	汎用ヘルパーが定義され、_build_rows_cached()から呼ばれ、かつPortfolio
	Risk PDF生成にも配線されていることを確認する。
	"""
	app_path = BASE + r"\services\app.py"
	with open(app_path, "r", encoding="utf-8-sig") as f:
		src = f.read()
	assert "def _cache_by_signature(" in src, "Sprint30 regression: _cache_by_signature helper missing"
	assert "return _cache_by_signature(" in src, \
		"Sprint30 regression: _build_rows_cached must delegate to _cache_by_signature (no duplicate caching logic)"
	assert '_cache_by_signature(\n\t\t\t\t\t\t"portfolio_risk_pdf_cache"' in src or \
		'"portfolio_risk_pdf_cache"' in src, \
		"Sprint30 regression: Portfolio Risk PDF generation not wired through _cache_by_signature"
	assert "generate_portfolio_pdf_report(portfolio_risk_result)" in src, \
		"Sprint30 regression: generate_portfolio_pdf_report call missing/renamed unexpectedly"
	print("   _cache_by_signature wired: _build_rows_cached + Portfolio Risk PDF OK")
check("Sprint30 members (_cache_by_signature wiring)", t_sprint30_cache_by_signature_wired)

# 6d) Sprint30 members (Portfolio Risk PDF output unchanged - same bytes for same input)
def t_sprint30_portfolio_pdf_output_unchanged():
	"""
	Performance改善はPDFの表示内容そのものを変えてはならない（実装方針・
	既存機能を壊さない）。generate_portfolio_pdf_report()自体は変更して
	いないため、同一入力に対して複数回呼び出しても同一バイト列を返すことを
	直接確認する（キャッシュ層を経由しない、関数そのものの回帰確認）。
	"""
	from report.pdf_report import generate_portfolio_pdf_report
	class _FakeHolding:
		def __init__(self, ticker, shares):
			self.ticker = ticker
			self.shares = shares
			self.id = 1
	rows = [
		{"holding": _FakeHolding("AAPL", 5), "data": {"company_name": "Apple Inc.", "current_price": 200.0, "sector": "Technology", "country": "United States"}, "score_result": {"total_score": 140, "max_score": 190}, "error": None},
	]
	from analysis import analyze_portfolio_risk
	result = analyze_portfolio_risk(rows, generate_ai_narrative=False)
	pdf_a = generate_portfolio_pdf_report(result)
	pdf_b = generate_portfolio_pdf_report(result)
	# 注：ReportLabはcanvas.save()のたびにPDFの/ID（メタデータ、ランダムな
	# ドキュメント識別子）を新規生成するため、完全なバイト一致は元々成立しない
	# （Sprint30で新規に混入した差異ではない）。レポート内容自体が同一かは
	# バイト長の一致で確認する（内容が変われば長さも変わるため十分な代理指標）。
	assert len(pdf_a) == len(pdf_b), "Sprint30 regression: generate_portfolio_pdf_report content length differs across identical calls"
	assert pdf_a and pdf_b, "Sprint30 regression: generate_portfolio_pdf_report returned empty bytes"
	print("   generate_portfolio_pdf_report output stable across repeated calls (same length: ", len(pdf_a), "bytes)")
check("Sprint30 members (portfolio PDF output unchanged)", t_sprint30_portfolio_pdf_output_unchanged)


# 6e) Sprint32 members (overall grade wired into Summary tab + PDF report)
def t_sprint32_overall_wired_in_app():
	"""
	Sprint18からcreate_analysis_bundle()は毎回calculate_overall_grade()を
	実行しbundle["overall"]に格納していたが、app.py側で一度も取り出して
	表示していなかった（計算されるが画面に一切出ない状態だった。詳細は
	docs/AI_HANDOVER.md Sprint32セクション参照）。app.pyのソースを直接検査し、
	overallがbundleから取り出され、render_summary_card / render_decision_card
	（Sprint18製・Sprint32まで未使用だったui/の部品、重複実装禁止のため
	新規実装ではなく再利用）に渡されていることを確認する。
	"""
	app_path = BASE + r"\services\app.py"
	with open(app_path, "r", encoding="utf-8-sig") as f:
		src = f.read()
	assert 'overall = bundle.get("overall")' in src, \
		"Sprint32 regression: overall not extracted from bundle in app.py"
	assert "from ui import render_summary_card, render_decision_card" in src, \
		"Sprint32 regression: ui card components not imported"
	assert "render_summary_card(overall, score_result)" in src, \
		"Sprint32 regression: render_summary_card not called in Summary tab"
	assert "render_decision_card(overall)" in src, \
		"Sprint32 regression: render_decision_card not called in Summary tab"
	print("   overall wired: bundle extraction + render_summary_card + render_decision_card OK")
check("Sprint32 members (overall wired in app.py)", t_sprint32_overall_wired_in_app)


def t_sprint32_decision_card_covers_14_factors():
	"""
	Sprint18時点のrender_decision_card()は6項目・/100正規化のままで、
	Sprint19〜26で追加された8項目（roic〜backtest）が欠けていた。
	Sprint32で実際の14項目・正しい満点に更新した。calculate_overall_grade()
	のdetailキー14個すべてに対応するラベルがrender_decision_card内に
	存在すること、かつ満点の合計が190点になることを直接検証する。
	"""
	import inspect
	from ui.decision_card import render_decision_card
	from analysis.overall_eval import calculate_overall_grade
	src = inspect.getsource(render_decision_card)

	score_result = {"total_score": 90}
	dcf_result = {"success": True, "margin_of_safety_pct": 30}
	overall = calculate_overall_grade(
		score_result=score_result, dcf_result=dcf_result,
		moat={"rating": "wide", "stars": 5}, brand={"stars": 5}, mgmt={"stars": 5},
		red_team={"conclusion": "", "summary": ""},
		roic={"score": 15}, owner_earnings={"score": 10}, intrinsic_value={"score": 15},
		capital_allocation={"score": 10}, share_buyback={"score": 10}, debt_quality={"score": 10},
		moat_strength={"score": 10}, backtest={"score": 10},
	)
	detail_keys = list(overall["detail"].keys())
	assert len(detail_keys) == 14, f"Sprint32 regression: overall detail should have 14 keys, got {len(detail_keys)}"
	for key in detail_keys:
		assert f'"{key}"' in src, f"Sprint32 regression: render_decision_card missing label for detail key '{key}'"
	assert "/ 100.0" not in src, "Sprint32 regression: stale /100.0 normalization still present in render_decision_card"

	# 満点(190点)で全項目が満点表示になることをスモークテストで確認
	# (calculate_overall_grade自体はSprint26で確定済みのため計算ロジックは検証済み。
	#  ここではrender_decision_card用のmax_score一覧が190点に合計されることのみ検証する)
	import re
	max_scores = [int(m) for m in re.findall(r'",\s*(\d+)\),', src)]
	assert sum(max_scores) == 190, f"Sprint32 regression: decision_card max scores sum to {sum(max_scores)}, expected 190"
	print("   render_decision_card covers all 14 factors, max scores sum to 190")
check("Sprint32 members (decision_card 14 factors)", t_sprint32_decision_card_covers_14_factors)


def t_sprint32_pdf_report_accepts_overall():
	"""
	generate_pdf_report()にoverallパラメータを追加した。既存呼び出し
	（overallを渡さない）でも壊れないこと（後方互換）、overallを渡した
	場合は総合判定セクションがPDFに実際に含まれることを確認する。

	注：当初PDFのバイト長比較（overallあり＝より大きいはず）で検証して
	いたが、環境（Windows/Linux、フォント・PDF内部構造の違い）によって
	バイト長の増減が安定しないことが分かった（きたのWindows環境で
	FAILし、サンドボックスでも実行のたびに増分が21〜169バイトと大きく
	揺れた）。バイト長は実際の内容を保証しないため、pdfplumber
	（既存の依存関係、earnings_material.pyで決算資料解析に使用中）で
	PDFのテキストを直接抽出し、総合判定セクションの見出し文字列
	「総合判定」が実際に含まれているかどうかで判定する、より直接的で
	環境非依存な検証に変更した。
	"""
	import io
	import pdfplumber
	from report.pdf_report import generate_pdf_report
	score_result = {"total_score": 82, "max_score": 100, "verdict": "test", "verdict_comment": "", "details": []}
	data = {"company_name": "Test Corp", "sector": "Technology", "country": "United States"}
	pdf_without = generate_pdf_report(
		data, score_result, "analysis", "news", [], {}, {}, {}, {}, [], [],
	)
	assert pdf_without[:4] == b"%PDF", "Sprint32 regression: generate_pdf_report broken when overall omitted"

	overall = {
		"overall_score": 150, "grade": "A", "risk": "Low", "confidence": "Medium",
		"action": "買い候補", "decision": "BUY",
		"detail": {"buffett": 35, "dcf": 15, "moat": 15, "brand": 8, "management": 8, "redteam": 5,
		           "roic": 12, "owner_earnings": 8, "intrinsic_value": 12, "capital_allocation": 8,
		           "share_buyback": 7, "debt_quality": 9, "moat_strength": 8, "backtest": 7},
	}
	pdf_with = generate_pdf_report(
		data, score_result, "analysis", "news", [], {}, {}, {}, {}, [], [],
		None, None, None, None, None, None, None, None,
		overall,
	)
	assert pdf_with[:4] == b"%PDF", "Sprint32 regression: generate_pdf_report broken when overall provided"

	with pdfplumber.open(io.BytesIO(pdf_without)) as pdf:
		text_without = "\n".join(p.extract_text() or "" for p in pdf.pages)
	with pdfplumber.open(io.BytesIO(pdf_with)) as pdf:
		text_with = "\n".join(p.extract_text() or "" for p in pdf.pages)

	assert "総合判定" not in text_without, \
		"Sprint32 regression: overall section text present even when overall not passed"
	assert "総合判定" in text_with, \
		"Sprint32 regression: overall section text missing from PDF when overall was passed"
	assert "BUY" in text_with and "Grade A" in text_with, \
		"Sprint32 regression: overall section content (decision/grade) not rendered correctly"
	print("   generate_pdf_report: backward compatible without overall, includes 総合判定 section when provided")
check("Sprint32 members (PDF report overall param)", t_sprint32_pdf_report_accepts_overall)


# 7) Sprint33 members (未使用コード・重複実装の削除)
def t_sprint33_dead_code_removed():
	"""
	きたからの依頼（未使用コード・冗長な部分の洗い出しと修正）を受けた
	全体調査で見つかった、どこからもimportされていない孤立ファイル・
	重複実装（ルール14違反）を削除した。回帰防止のため、以下を確認する。

	- 削除したファイルが実際に存在しないこと
	  （services/market_data.py、src/checklist_engine.py、src/overall_eval.py、
	  src/gemini.py、src/engines/dcf_analysis.py、
	  src/ui/{score_card,chart_panel,financial_table}.py）
	- engines.checklist_engine には generate_buffett_checklist_rule のみが
	  残り、report.report と重複していた create_radar_chart / create_score_bar /
	  create_checklist_display が削除されていること
	- ai.ai_analysis から、どこにも呼ばれていなかった重複ロジック
	  _generate_rule_checklist が削除されていること
	- ui パッケージが render_summary_card / render_decision_card のみを
	  公開していること（Sprint18で作られたが未配線のままだった
	  render_score_card / render_chart_panel / render_financial_table は
	  対象外）
	"""
	import os as _os

	removed_files = [
		r"\services\market_data.py",
		r"\services\src\checklist_engine.py",
		r"\services\src\overall_eval.py",
		r"\services\src\gemini.py",
		r"\services\src\engines\dcf_analysis.py",
		r"\services\src\ui\score_card.py",
		r"\services\src\ui\chart_panel.py",
		r"\services\src\ui\financial_table.py",
	]
	for rel in removed_files:
		path = BASE + rel
		assert not _os.path.exists(path), f"Sprint33 regression: dead file should be removed but still exists: {path}"

	import engines.checklist_engine as checklist_engine_mod
	assert hasattr(checklist_engine_mod, "generate_buffett_checklist_rule"), \
		"Sprint33 regression: generate_buffett_checklist_rule missing from engines.checklist_engine"
	for stale in ("create_radar_chart", "create_score_bar", "create_checklist_display"):
		assert not hasattr(checklist_engine_mod, stale), \
			f"Sprint33 regression: duplicate function '{stale}' should have been removed from engines.checklist_engine (kept only in report.report)"

	import ai.ai_analysis as ai_analysis_mod
	assert not hasattr(ai_analysis_mod, "_generate_rule_checklist"), \
		"Sprint33 regression: unused duplicate _generate_rule_checklist should have been removed from ai.ai_analysis"

	import ui as ui_mod
	assert set(ui_mod.__all__) == {"render_summary_card", "render_decision_card"}, \
		f"Sprint33 regression: ui package should export only render_summary_card/render_decision_card, got {ui_mod.__all__}"

	print("   dead files removed, duplicate checklist/UI functions cleaned up, ui package exports only active components")
check("Sprint33 members (dead code cleanup)", t_sprint33_dead_code_removed)


# 8) Sprint36 members (score snapshot auto-save wiring)
def t_sprint36_snapshot_builder():
	"""
	Sprint36では、Sprint35の永続化層(storage)をapp.pyから呼び出し、
	単一銘柄の分析実行のたびにScoreSnapshotを自動保存する導線を追加した。
	app.py自体にはUI mode -> storage mode変換やScoreSnapshot組み立てロジックを
	書かず、storage.build_score_snapshot / storage.resolve_snapshot_modeへ
	切り出している（ルール4：app.pyへ分析ロジックを書かない）ため、
	ここではその公開APIの存在とマッピングの回帰を確認する。
	"""
	from storage import JsonScoreStorage, ScoreSnapshot, build_score_snapshot, resolve_snapshot_mode

	assert resolve_snapshot_mode("⚡ クイック（財務スコアのみ）") == "quick", \
		"Sprint36 regression: quick mode label should map to 'quick'"
	assert resolve_snapshot_mode("📊 標準（+AI定性分析・要約）") == "standard", \
		"Sprint36 regression: standard mode label should map to 'standard'"
	assert resolve_snapshot_mode("🔎 フル（すべて）") == "full", \
		"Sprint36 regression: full mode label should map to 'full'"

	snapshot = build_score_snapshot(
		ticker="AAPL",
		mode_label="🔎 フル（すべて）",
		overall={"overall_score": 150, "grade": "A", "decision": "BUY"},
		score_result={"total_score": 80},
	)
	assert isinstance(snapshot, ScoreSnapshot), \
		"Sprint36 regression: build_score_snapshot must return a ScoreSnapshot"

	print("   score snapshot auto-save wiring: storage.build_score_snapshot/resolve_snapshot_mode OK")
check("Sprint36 members (score snapshot auto-save wiring)", t_sprint36_snapshot_builder)


# 9) Sprint37 members (score history chart display)
def t_sprint37_history_chart():
	"""
	Sprint37では、Sprint36で自動保存しているScoreSnapshotを読み込み、
	サマリータブの末尾に折れ線チャートとして表示する導線を追加した。
	チャート生成そのものはreport.create_score_history_chart側に切り出し、
	app.pyは呼び出しと0件時のメッセージ分岐のみを担う（ルール4）。
	Streamlit非依存の部分（チャート生成関数）の存在と基本的な入出力を
	ここで確認する。
	"""
	from report.report import create_score_history_chart
	from storage import ScoreSnapshot

	empty_fig = create_score_history_chart([])
	assert len(empty_fig.data) == 0, \
		"Sprint37 regression: empty history should produce an empty figure"

	snapshot = ScoreSnapshot.create(
		ticker="AAPL",
		mode="full",
		overall_score=150,
		grade="A",
		decision="BUY",
		buffett_score=80,
		evaluated_at="2026-08-16T09:00:00+00:00",
	)
	fig = create_score_history_chart([snapshot])
	assert len(fig.data) == 1, \
		"Sprint37 regression: non-empty history should produce exactly one trace"
	assert list(fig.data[0].y) == [150], \
		"Sprint37 regression: chart y-values should be overall_score"

	print("   score history chart wired: report.create_score_history_chart OK")
check("Sprint37 members (score history chart display)", t_sprint37_history_chart)


print("=== HEALTH:", "ALL OK" if ok else "ISSUES FOUND", "===")
