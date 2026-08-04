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
    assert bf["overall"]["detail"].get("roic", 0) >= 0, "roic score missing from overall detail"
    assert bf["overall"]["detail"].get("owner_earnings", 0) >= 0, "owner_earnings score missing from overall detail"
    print("   roic wired:", bf["roic"]["score"], "/", bf["roic"]["max_score"],
          " owner_earnings wired:", bf["owner_earnings"]["score"], "/", bf["owner_earnings"]["max_score"])
check("bundle smoke (quick/full)", t_bundle)

# 5) app.py compiles
def t_compile():
    py_compile.compile(BASE + r"\services\app.py", doraise=True)
check("app.py compiles", t_compile)

print("=== HEALTH:", "ALL OK" if ok else "ISSUES FOUND", "===")
