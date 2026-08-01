import io, sys

PATH = r"C:\Users\t.k\buffett-invest-analyzer\services\src\analysis\analysis_bundle.py"

with io.open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

marker = "# Overall verdict - ONLY overall_eval decides BUY / WATCH / PASS"

if 'bundle["checklist"] = bundle["checklist"] or []' not in content:
    insert = (
        '    # Normalize bundle values (Sprint18)\n'
        '    bundle["checklist"] = bundle["checklist"] or []\n'
        '    bundle["news"] = bundle["news"] or []\n'
        "\n"
    )
    idx = content.find(marker)
    if idx == -1:
        print("ERROR: marker not found")
        sys.exit(1)
    content = content[:idx] + insert + content[idx:]

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(content)

print("analysis_bundle.py normalized OK")