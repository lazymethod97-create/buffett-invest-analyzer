"""
PDFレポート生成モジュール（Sprint8）
ReportLabを使用し、分析結果全体をPDFとして出力する。
日本語フォントはReportLab組み込みのCIDフォント（HeiseiKakuGo-W5／HeiseiMin-W3）を
使用するため、別途フォントファイルを用意する必要はない。
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

####################################################
# フォント登録（モジュール読込時に一度だけ実行）
####################################################
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))  # 見出し用ゴシック
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))      # 本文用明朝

FONT_BOLD = "HeiseiKakuGo-W5"
FONT_NORMAL = "HeiseiMin-W3"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 20 * mm
MARGIN_TOP = 20 * mm
MARGIN_BOTTOM = 20 * mm
LINE_HEIGHT = 6 * mm
MAX_CHARS_PER_LINE = 42  # 本文フォントサイズでの概算折り返し文字数


####################################################
# PDF組み立てヘルパークラス
####################################################
class PDFBuilder:
    """ページ送り・文字折り返しを管理しながらPDFを組み立てるヘルパー"""

    def __init__(self):
        self.buffer = io.BytesIO()
        self.c = canvas.Canvas(self.buffer, pagesize=A4)
        self.y = PAGE_HEIGHT - MARGIN_TOP

    def _new_page(self):
        self.c.showPage()
        self.y = PAGE_HEIGHT - MARGIN_TOP

    def _check_space(self, needed: float = LINE_HEIGHT):
        if self.y - needed < MARGIN_BOTTOM:
            self._new_page()

    def add_title(self, text: str):
        self._check_space(10 * mm)
        self.c.setFont(FONT_BOLD, 16)
        self.c.drawString(MARGIN_X, self.y, text)
        self.y -= 10 * mm

    def add_heading(self, text: str):
        self._check_space(8 * mm)
        self.c.setFont(FONT_BOLD, 12)
        self.c.setFillColor(colors.HexColor("#1a4d8f"))
        self.c.drawString(MARGIN_X, self.y, text)
        self.c.setFillColor(colors.black)
        self.y -= 8 * mm

    def add_paragraph(self, text: str, size: int = 10):
        if not text:
            return
        self.c.setFont(FONT_NORMAL, size)
        for raw_line in str(text).split("\n"):
            if not raw_line.strip():
                self.y -= LINE_HEIGHT / 2
                continue
            for line in _wrap_text(raw_line, MAX_CHARS_PER_LINE):
                self._check_space()
                self.c.drawString(MARGIN_X, self.y, line)
                self.y -= LINE_HEIGHT

    def add_bullet(self, text: str):
        self.add_paragraph(f"・{text}")

    def add_divider(self):
        self._check_space(4 * mm)
        self.c.setStrokeColor(colors.HexColor("#cccccc"))
        self.c.line(MARGIN_X, self.y, PAGE_WIDTH - MARGIN_X, self.y)
        self.c.setStrokeColor(colors.black)
        self.y -= 6 * mm

    def save(self) -> bytes:
        self.c.showPage()
        self.c.save()
        self.buffer.seek(0)
        return self.buffer.read()


def _wrap_text(text: str, max_chars: int):
    """日本語対応の簡易折り返し（文字数ベース）"""
    lines = []
    current = ""
    for ch in text:
        current += ch
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines or [""]


####################################################
# メイン関数
####################################################
def generate_pdf_report(
    data: dict,
    score_result: dict,
    ai_analysis_text: str,
    news_summary: str,
    checklist: list,
    moat: dict,
    brand: dict,
    mgmt: dict,
    red_team: dict,
    confirmation_points: list,
    hypotheses: list,
    roic: dict = None,
    owner_earnings: dict = None,
    intrinsic_value: dict = None,
    capital_allocation: dict = None,
) -> bytes:
    """
    Sprint8: 分析結果全体をPDFレポートとして出力する。
    戻り値はPDFバイナリデータ（st.download_buttonにそのまま渡せる）。
    """
    pdf = PDFBuilder()

    # 表紙
    pdf.add_title("Buffett Investment Analyzer")
    pdf.add_paragraph(f"分析レポート：{data.get('company_name', '不明')}")
    pdf.add_paragraph(f"セクター：{data.get('sector', '不明')}　国：{data.get('country', '不明')}")
    pdf.add_divider()

    # Buffett Score
    pdf.add_heading("📊 Buffett Score")
    pdf.add_paragraph(f"総合スコア：{score_result.get('total_score', 0)} / {score_result.get('max_score', 100)}点")
    pdf.add_paragraph(f"判定：{score_result.get('verdict', '')}")
    pdf.add_paragraph(score_result.get("verdict_comment", ""))
    pdf.add_divider()

    # 採点詳細
    pdf.add_heading("📋 採点詳細")
    for d in score_result.get("details", []):
        status = "合格" if d.get("passed") else "不合格"
        pdf.add_bullet(
            f"{d.get('item','')}：{d.get('value','')}"
            f"（{d.get('score','')}/{d.get('max_score','')}点・{status}）"
        )
    pdf.add_divider()

    # AI定性分析
    pdf.add_heading("🤖 AI定性分析")
    pdf.add_paragraph(ai_analysis_text)
    pdf.add_divider()

    # ニュース要約
    pdf.add_heading("📝 AIニュース要約")
    pdf.add_paragraph(news_summary or "ニュースは取得できませんでした。")
    pdf.add_divider()

    # ニュース確認ポイント（Sprint7）
    pdf.add_heading("🔍 ニュースから確認すべきポイント")
    priority_label = {"high": "高", "medium": "中", "low": "低"}
    if confirmation_points:
        for p in confirmation_points:
            pri = priority_label.get(p.get("priority", ""), "-")
            pdf.add_bullet(f"[{p.get('category','')}/／優先度:{pri}] {p.get('point','')}")
    else:
        pdf.add_paragraph("確認すべきポイントはありません。")
    pdf.add_divider()

    # Checklist
    pdf.add_heading("📋 Buffett Investment Checklist")
    status_label = {"pass": "合格", "warning": "要注意", "fail": "不適合"}
    for item in checklist or []:
        st_label = status_label.get(item.get("status", ""), item.get("status", ""))
        pdf.add_bullet(f"{item.get('item','')}：{st_label}｜{item.get('reason','')}")
    pdf.add_divider()

    # MOAT
    pdf.add_heading("🏰 MOAT評価（経済的堀）")
    rating_label = {"wide": "Wide MOAT", "narrow": "Narrow MOAT", "none": "No MOAT"}
    pdf.add_paragraph(
        f"評価：{rating_label.get(moat.get('rating',''), moat.get('rating',''))}"
        f"（★{moat.get('stars',0)}）"
    )
    pdf.add_paragraph(moat.get("summary", ""))
    pdf.add_divider()

    # ブランド
    pdf.add_heading("🏷️ ブランド力評価")
    pdf.add_paragraph(f"評価：★{brand.get('stars',0)}（{brand.get('brand_type','不明')}）")
    pdf.add_paragraph(brand.get("buffet_view", ""))
    pdf.add_divider()

    # 経営者
    pdf.add_heading("👔 経営者評価")
    pdf.add_paragraph(f"評価：★{mgmt.get('stars',0)}")
    pdf.add_paragraph(mgmt.get("conclusion", ""))
    pdf.add_divider()

    # Red Team
    pdf.add_heading("🔴 Red Team AI（反対意見）")
    for key, label in [
        ("financial_skepticism", "財務への疑問"),
        ("moat_vulnerability", "MOATの脆弱性"),
        ("brand_demand_risk", "ブランド・需要リスク"),
        ("management_blindspot", "経営・組織リスク"),
        ("valuation_concern", "バリュエーション懸念"),
    ]:
        val = red_team.get(key, "")
        if val:
            pdf.add_paragraph(f"【{label}】{val}")
    pdf.add_paragraph(f"結論：{red_team.get('conclusion','')}")
    pdf.add_divider()

    pdf.add_divider()

    # ROIC（Sprint19）
    pdf.add_heading("💰 ROIC（投下資本利益率）分析")
    if roic and roic.get("raw"):
        raw = roic.get("raw", {})
        roic_val = raw.get("roic")
        if roic_val is not None:
            pdf.add_paragraph(f"ROIC：{roic_val*100:.1f}%")
        else:
            pdf.add_paragraph("ROIC：データ不足")
        pdf.add_paragraph(f"評価：{roic.get('summary', '')}")
        pdf.add_paragraph(f"スコア：{roic.get('score', 0)} / {roic.get('max_score', 15)}点")
        nopat = raw.get("nopat")
        ic = raw.get("invested_capital")
        if nopat is not None:
            pdf.add_paragraph(f"NOPAT（税引後営業利益）：{nopat:,.0f}")
        if ic is not None:
            pdf.add_paragraph(f"投下資本：{ic:,.0f}")
        tax_rate = raw.get("tax_rate", 0.25)
        pdf.add_paragraph(f"実効税率：{tax_rate*100:.1f}%")
    else:
        pdf.add_paragraph("ROIC分析結果がありません。")
    pdf.add_divider()

    # Owner Earnings（Sprint20）
    pdf.add_heading("💵 Owner Earnings（オーナーアーニングス）分析")
    if owner_earnings and owner_earnings.get("raw"):
        oe_raw = owner_earnings.get("raw", {})
        oe_val = oe_raw.get("owner_earnings")
        oe_yield = oe_raw.get("owner_earnings_yield")
        if oe_val is not None:
            pdf.add_paragraph(f"Owner Earnings：{oe_val:,.0f}")
        else:
            pdf.add_paragraph("Owner Earnings：データ不足")
        if oe_yield is not None:
            pdf.add_paragraph(f"Owner Earnings利回り：{oe_yield*100:.1f}%")
        pdf.add_paragraph(f"評価：{owner_earnings.get('summary', '')}")
        pdf.add_paragraph(f"スコア：{owner_earnings.get('score', 0)} / {owner_earnings.get('max_score', 10)}点")
        net_income = oe_raw.get("net_income")
        da = oe_raw.get("depreciation_amortization")
        capex = oe_raw.get("capital_expenditures")
        if net_income is not None:
            pdf.add_paragraph(f"当期純利益：{net_income:,.0f}")
        if da is not None:
            pdf.add_paragraph(f"減価償却費等（推定）：{da:,.0f}")
        if capex is not None:
            pdf.add_paragraph(f"設備投資CapEx（推定）：{capex:,.0f}")
    else:
        pdf.add_paragraph("Owner Earnings分析結果がありません。")
    # Intrinsic Value（Sprint21）
    pdf.add_heading("🎯 Intrinsic Value（内在価値）分析")
    if intrinsic_value and intrinsic_value.get("raw"):
        iv_raw = intrinsic_value.get("raw", {})
        consensus = iv_raw.get("consensus_intrinsic_value_per_share")
        current_price = iv_raw.get("current_price")
        mosp = iv_raw.get("margin_of_safety_pct")
        if consensus is not None:
            pdf.add_paragraph(f"コンセンサス内在価値（1株）：{consensus:,.2f}")
        else:
            pdf.add_paragraph("コンセンサス内在価値：データ不足")
        if current_price is not None:
            pdf.add_paragraph(f"現在株価：{current_price:,.2f}")
        if mosp is not None:
            pdf.add_paragraph(f"安全余裕（Margin of Safety）：{mosp:+.1f}%")
        pdf.add_paragraph(f"判定：{intrinsic_value.get('summary', '')}")
        pdf.add_paragraph(f"スコア：{intrinsic_value.get('score', 0)} / {intrinsic_value.get('max_score', 15)}点")
        for est in iv_raw.get("estimates", []):
            pdf.add_bullet(f"{est.get('label', '')}: {est.get('value', 0):,.2f}（{est.get('detail', '')}）")
    else:
        pdf.add_paragraph("Intrinsic Value分析結果がありません。")
    # Capital Allocation（Sprint22）
    pdf.add_heading("🔄 Capital Allocation（資本配分）分析")
    if capital_allocation and capital_allocation.get("raw"):
        ca_raw = capital_allocation.get("raw", {})
        pdf.add_paragraph(f"スコア：{capital_allocation.get('score', 0)} / {capital_allocation.get('max_score', 10)}点")
        pdf.add_paragraph(f"評価：{capital_allocation.get('summary', '')}")
        re_score = ca_raw.get("reinvestment_score", 0)
        po_score = ca_raw.get("payout_score", 0)
        bb_score = ca_raw.get("buyback_score", 0)
        pdf.add_bullet(f"再投資効率（ROIC基準）：{re_score}/4点 - {ca_raw.get('reinvestment_detail', '')}")
        pdf.add_bullet(f"株主還元の規律（配当性向）：{po_score}/3点 - {ca_raw.get('payout_detail', '')}")
        pdf.add_bullet(f"自社株買いのタイミング（MOSとの突合）：{bb_score}/3点 - {ca_raw.get('buyback_detail', '')}")
    else:
        pdf.add_paragraph("Capital Allocation分析結果がありません。")
    # 投資仮説
    pdf.add_heading("📋 投資仮説管理")
    if hypotheses:
        for h in hypotheses:
            hd = h.to_dict() if hasattr(h, "to_dict") else h
            pdf.add_paragraph(f"■ {hd.get('title','')}　[{hd.get('status','')}]")
            pdf.add_paragraph(hd.get("rationale", ""))
            for v in hd.get("verification_items", []):
                pdf.add_bullet(v)
    else:
        pdf.add_paragraph("登録されている投資仮説はありません。")
    pdf.add_divider()

    pdf.add_paragraph(
        "⚠️ 本レポートは投資の参考情報です。実際の投資判断はご自身の責任で行ってください。",
        size=8,
    )

    return pdf.save()
