import io, sys

APP = r"C:\Users\t.k\buffett-invest-analyzer\services\app.py"

with io.open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

def sw(s):
    return s.strip()

# end marker
end_idx = None
for i, ln in enumerate(lines):
    if sw(ln).startswith("st.session_state.analysis_bundle = bundle"):
        end_idx = i
        break
if end_idx is None:
    print("ERROR: end marker not found"); sys.exit(1)

# start marker (legacy bundle dict or new if-block)
start_idx = None
for i in range(end_idx):
    if sw(lines[i]).startswith("bundle = {"):
        start_idx = i
        break

if start_idx is None:
    for i in range(end_idx):
        if sw(lines[i]).startswith("if analysis_mode.startswith("):
            start_idx = i
            break
    if start_idx is None:
        print("ERROR: start marker not found"); sys.exit(1)
    j = start_idx - 1
    while j >= 0:
        s = sw(lines[j])
        if s == "" or s.startswith("#"):
            j -= 1
        else:
            break
    start_idx = j + 1

new_block = (
"\t####################################################\n"
"\t# Sprint18 Phase4: 分析はanalysis_bundleに一元化\n"
"\t# app.pyはControllerとしてcreate_analysis_bundle()を呼ぶだけ。\n"
"\t# データ取得(news)のみapp.pyが担当する。\n"
"\t####################################################\n"
'\tif analysis_mode.startswith("⚡"):\n'
"\t\tnews = None\n"
"\telse:\n"
'\t\tnews = cached_get_latest_news(data["company_name"])\n'
"\n"
'\tdcf_result = globals().get("dcf_result") or {}\n'
"\n"
'\twith st.spinner("🤖 AIが分析中...（初回のみ少し時間がかかります）"):\n'
"\t\tbundle = create_analysis_bundle(\n"
"\t\t\tdata=data,\n"
"\t\t\tscore_result=score_result,\n"
"\t\t\tdcf_result=dcf_result,\n"
"\t\t\tmode=analysis_mode,\n"
"\t\t\tnews=news,\n"
'\t\t\tis_quick=analysis_mode.startswith("⚡"),\n'
'\t\t\tis_full=analysis_mode.startswith("🔎"),\n'
"\t\t)\n"
"\n"
"\tst.session_state.analysis_bundle = bundle\n"
)

lines[start_idx:end_idx+1] = [new_block]
content = "".join(lines)

if "from analysis import create_analysis_bundle" not in content:
    marker = "from ai_analysis import ("
    idx = content.find(marker)
    if idx == -1:
        print("ERROR: import marker not found"); sys.exit(1)
    close_idx = content.find(")", idx)
    if close_idx == -1:
        print("ERROR: import close paren not found"); sys.exit(1)
    content = content[:close_idx+1] + "\nfrom analysis import create_analysis_bundle" + content[close_idx+1:]

with io.open(APP, "w", encoding="utf-8", newline="") as f:
    f.write(content)

print("app.py patched OK")