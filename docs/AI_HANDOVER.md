# AI_HANDOVER.md

# Buffett Investment Analyzer Ver2
## AI引き継ぎ書

---

# GitHub

GitHubを唯一の正とする。

ローカルよりGitHub最新版を優先。

新しいSprintを開始する前に必ず最新コードを確認すること。

---

# Version

Buffett Investment Analyzer Ver2

現在Sprint34-4完了。

次回のSprintは未定。

---

# Sprint18 完了内容

## リファクタリング（責務分離）

Version2の責務分離方針を確定・実装完了。

### app.py

app.pyはController専用とする。

以下のみ担当する。

・入力受付

・データ取得（cached_get_latest_news等）

・分析呼び出し（create_analysis_bundle() のみ）

・UI表示

分析ロジックは禁止。

---

### analysis

分析処理を集約するディレクトリ。

対象

overall_eval

moat

brand

management

red_team

analysis_bundle

roic

---

### engines

数値計算のみ。

対象

scoring_engine

dcf_engine

checklist_engine

roic_engine

Sprint20 / Sprint21で追加完了

intrinsic_engine（Sprint21）

owner_earnings_engine（Sprint20）

---

### data

データ取得のみ。

data_fetcher

news_fetcher

---

### ai

Geminiとの通信のみ。

gemini.py

ai_analysis.py

---

### ui

Streamlit描画専用。

summary_card

decision_card

financial_table

score_card

chart_panel

---

### report

PDF関連

report.py

pdf_report.py

---

# analysis_bundle

Version2から導入。

全分析を一括実行する。

create_analysis_bundle()

のみをapp.pyから呼び出す。

戻り値

overall

brand

moat

management（mgmt）

red_team

checklist

news

roic

---

# overall_eval

総合判定はここだけ。

BUY

WATCH

PASS

などをここで決定する。

他モジュールでは判定しない。

---

# Sprint19 完了内容

## ROIC分析

### 新規作成

engines/roic_engine.py

ROIC計算エンジン（ルールベース）

NOPAT = 営業利益 × (1 - 実効税率)

投下資本 = 純資産 + 総負債 - 現金同等物

ROIC = NOPAT ÷ 投下資本

analysis/roic.py

ROIC分析モジュール（共通形式）

### 修正

data/data_fetcher.py

ROIC関連フィールド追加

operating_income

income_tax_expense

income_before_tax

long_term_debt

short_term_debt

total_equity

cash

short_term_investments

analysis/analysis_bundle.py

create_analysis_bundle() に roic を追加

analysis/overall_eval.py

_score_roic() 追加（15点満点）

report/report.py

create_roic_display() 追加

report/pdf_report.py

PDFにROICセクション追加

ai/ai_analysis.py

generate_roic_analysis() 追加（Gemini評価）

app.py

定性分析タブ + PDFダウンロードにROIC表示追加

### スコア配分（115点満点、Sprint19時点）

Buffett Score: 40点

DCF: 20点

MOAT: 15点

ブランド: 10点

経営者: 10点

Red Team: 5点

ROIC: 15点（新規）

### 判定基準（調整後、Sprint19時点）

S: 100点以上

A: 85点以上

B: 70点以上

C: 55点以上

D: 55点未満

---

# Sprint19 不具合修正（Sprint20で実施）

Sprint19は上記の通り「完了」と記載されていたが、GitHub最新版を確認した結果、
以下の不具合が見つかったため、Sprint20の中で修正した。

## 不具合1：analysis_bundle.pyがanalyze_roic()を呼んでいない

analyze_roicをimportしているが呼び出しコードが存在せず、
bundle["roic"]が常にNoneだった。ROIC分析結果が画面にもPDFにも一切表示されない状態だった。

修正：is_full時にanalyze_roic(data)を明示的に呼び出すよう変更。

## 不具合2：calculate_overall_grade()にroicが渡っていない

不具合1と合わせて、ROICスコア（15点）が総合スコアに一度も反映されていなかった。

修正：calculate_overall_grade()呼び出し時にroic=bundle["roic"]を渡すよう変更。

## 不具合3：overall_eval.pyの判定基準が未更新のまま

115点満点への変更後も、_grade()/_stars()の閾値が更新されておらず、
古い100点満点相当の基準（90/80/70/60）のままだった。

修正：Sprint20で125点満点（Owner Earnings追加）に合わせて全面更新（下記参照）。

## 不具合4：generate_roic_analysis()が死にコードだった

ai/__init__.pyからexportされておらず、どこからも呼ばれていなかった。
さらに関数内部で未定義の_call_gemini()を呼んでおり（broad exceptで握りつぶされ気づきにくい形で）、
たとえ呼ばれても常にフォールバックしか返せない状態だった。

修正：ai/__init__.pyにexportを追加し、analysis_bundle.py内でanalyze_roic()のルールベース結果に対する
AI考察の上乗せとして呼び出すよう配線。関数内部も他のgenerate_X_analysis関数と同じ
「os.getenv("GEMINI_API_KEY") + genai.Client()」パターンに書き換えて修正。

## 不具合5：docs/AI_HANDOVER.md自体にPowerShellスクリプトの断片が混入していた

ファイル冒頭に`@'`、末尾に`'@ | Set-Content -Path ...`が本文として保存されてしまっていた
（Set-Content実行時にスクリプト全体を貼り付けてしまったと見られる）。本更新で除去。

## 参考：generate_overall_summary()も同種の不具合あり（未修正・対象外）

ai/ai_analysis.py内のgenerate_overall_summary()も未定義の_call_gemini()を呼んでいるが、
app.py等どこからもimport・使用されていない（デッドコード）ため、Sprint20では対象外とした。
将来このコードを使う場合は同様の修正が必要。

## 不具合6：PowerShellスクリプト適用時にCRLF不一致・BOM二重化が発生（適用時に発覚・修正済み）

Sprint20のコードは全て正しかったが、実際にきたの環境（Windows + Git clone）へ適用する過程で
以下2つの環境依存の問題が発覚した。

- app.py / pdf_report.py がCRLF改行だったため、LF基準で書いた`.Replace()`パッチが
  0件ヒットでSKIPされた。→ 比較前にLF正規化、書き込み前にCRLF復元する方式に修正。
- 一部ファイルのヒアストリング内に、AIが誤ってBOM文字（U+FEFF）を直接含めてしまい、
  `Set-Content -Encoding UTF8`が自動付与するBOMと二重になり、
  `SyntaxError: invalid non-printable character U+FEFF`が発生。→ 該当7ファイルのBOMを
  全て除去し、BOMなしUTF-8に統一して解消。

以後のSprintでは、PROJECT_RULES.md 18番の規則に従うこと。

**Sprint20はhealth_check.py実行により`=== HEALTH: ALL OK ===`を確認済み。GitHubへのcommit/push待ち。**

---

# Sprint20 完了内容

## Owner Earnings分析

### 新規作成

engines/owner_earnings_engine.py

Owner Earnings計算エンジン（ルールベース）

Owner Earnings = 当期純利益 + 減価償却費等（D&A） − 設備投資（CapEx）

D&A（推定） = EBITDA − 営業利益

CapEx（推定） = 営業キャッシュフロー − フリーキャッシュフロー

analysis/owner_earnings.py

Owner Earnings分析モジュール（共通形式）

### 修正

data/data_fetcher.py

Owner Earnings関連フィールド追加

net_income

ebitda

operating_cashflow

total_revenue

shares_outstanding

analysis/analysis_bundle.py

create_analysis_bundle() に owner_earnings を追加

analyze_roic()の呼び出し漏れ（Sprint19不具合1）もあわせて修正

analysis/overall_eval.py

_score_owner_earnings() 追加（10点満点）

calculate_overall_grade() の判定基準を125点満点に合わせて全面更新

report/report.py

create_owner_earnings_display() 追加

report/pdf_report.py

PDFにOwner Earningsセクション追加

ai/ai_analysis.py

generate_owner_earnings_analysis() 追加（Gemini評価、フォールバック付き）

generate_roic_analysis() の_call_gemini未定義バグを修正（Sprint19不具合4）

app.py

定性分析タブ + PDFダウンロードにOwner Earnings表示追加

roic / owner_earnings をbundle展開時に取得するよう整理（moat/brand/mgmt/red_teamと同じ配置）

health_check.py

bundle["roic"] / bundle["owner_earnings"] がNoneでないことを検証するアサーションを追加
（Sprint19不具合1の再発防止）

### スコア配分（125点満点）

Buffett Score: 40点

DCF: 20点

MOAT: 15点

ブランド: 10点

経営者: 10点

Red Team: 5点

ROIC: 15点

Owner Earnings: 10点（新規）

### 判定基準（Sprint20更新後）

S: 109点以上

A: 92点以上

B: 76点以上

C: 60点以上

D: 60点未満

# Sprint21 完了内容

## Intrinsic Value（内在価値）分析

### 新規作成

engines/intrinsic_engine.py

Intrinsic Value計算エンジン（ルールベース）
複数方式のコンセンサスで内在価値（1株あたり）を算出する。

・方式1: DCF（FCF割引） 重み40%（既存 dcf_engine を再利用）
・方式2: Owner Earnings方式 重み30%（既存 owner_earnings_engine を再利用、2段階成長で割引）
・方式3: Earnings Power方式 重み30%（当期純利益 × 保守的PER 12倍）

データ不足の方式はスキップし、利用可能な方式のみで重みを再正規化する。

analysis/intrinsic_value.py

Intrinsic Value分析モジュール（共通形式）

### 修正

data/data_fetcher.py

変更なし（既存フィールドで計算可能）

analysis/analysis_bundle.py

create_analysis_bundle() に intrinsic_value を追加（is_full時）

analysis/overall_eval.py

_score_intrinsic_value() 追加（15点満点）
判定基準を140点満点に合わせて全面更新

ai/ai_analysis.py

generate_intrinsic_value_analysis() 追加（Gemini評価、フォールバック付き）

report/report.py

create_intrinsic_value_display() 追加

report/pdf_report.py

PDFにIntrinsic Valueセクション追加

app.py

定性分析タブ + PDFダウンロードにIntrinsic Value表示追加
（import / bundle展開 / 表示 / PDF引数の4箇所を編集）

health_check.py

Sprint21検証を追加（engines/analysis/ai/report のimport確認、
bundle["intrinsic_value"]がNoneでないこと、overall detailへの配線確認）

### スコア配分（140点満点、Sprint21時点）

Buffett Score: 40点

DCF: 20点

MOAT: 15点

ブランド: 10点

経営者: 10点

Red Team: 5点

ROIC: 15点

Owner Earnings: 10点

Intrinsic Value: 15点（新規）

### 判定基準（Sprint21更新後）

S: 122点以上

A: 103点以上

B: 85点以上

C: 67点以上

D: 67点未満

---

# Sprint22 完了内容

## Capital Allocation（資本配分）分析

### 新規作成

engines/capital_allocation_engine.py

Capital Allocation計算エンジン（ルールベース）

3軸で評価（合計10点満点）：

・再投資効率（4点）: ROICのトレンドと水準から、内部再投資の効率を評価
・株主還元の規律（3点）: 配当性向・配当利回りから、安定した株主還元の規律を評価
・自社株買いのタイミング（3点）: 買い戻し額と安全域（MOS）とのバランスから、適切なタイミングでの自社株買いを評価

analysis/capital_allocation.py

Capital Allocation分析モジュール（共通形式）

### 修正

data/data_fetcher.py

Capital Allocation関連フィールド追加

payout_ratio（配当性向）

buyback_amount（自社株買い額）

analysis/analysis_bundle.py

create_analysis_bundle() に capital_allocation を追加（is_full時）

analysis/overall_eval.py

_score_capital_allocation() 追加（10点満点）

判定基準を150点満点に合わせて全面更新（S:131 / A:110 / B:91 / C:72）

ai/ai_analysis.py

generate_capital_allocation_analysis() 追加（Gemini評価、フォールバック付き）

report/report.py

create_owner_earnings_display() の実装漏れを修正（Sprint20以降app.pyから参照されていたが未実装だった）

create_capital_allocation_display() 追加

report/pdf_report.py

PDFにCapital Allocationセクション追加

app.py

定性分析タブ + PDFダウンロードにCapital Allocation表示追加

（import / bundle展開 / 表示 / PDF引数の4箇所を編集）

health_check.py

Sprint22検証を追加（engines/analysis/ai/reportのimport確認、
display関数の実import検証（create_owner_earnings_displayが実際にimport可能であること）、
bundle["capital_allocation"]がNoneでないこと、overall detailへの配線確認）

### スコア配分（150点満点、Sprint22時点）

Buffett Score: 40点

DCF: 20点

MOAT: 15点

ブランド: 10点

経営者: 10点

Red Team: 5点

ROIC: 15点

Owner Earnings: 10点

Intrinsic Value: 15点

Capital Allocation: 10点（新規）

### 判定基準（Sprint22更新後）

S: 131点以上

A: 110点以上

B: 91点以上

C: 72点以上

D: 72点未満

---

# Sprint23 完了内容

## Share Buyback（自社株買い）分析

Capital Allocation（Sprint22）では自社株買いの「タイミング」を
安全余裕（MOS）との突合で単年評価済み。Sprint23では自社株買い
そのものの「質・効果・一貫性」を、複数年の推移データから
独立した分析軸として評価する（Sprint22との重複なし）。

### 新規作成

engines/share_buyback_engine.py

Share Buyback計算エンジン（ルールベース）

4軸で評価（合計10点満点）：

・買い入れの一貫性（3点）: 複数年の自社株買い実施率で評価
・発行済株式数の減少効果（3点）: 期中平均株式数の減少率で評価
・財務健全性とのバランス（2点）: 負債推移とのバランスで評価
・買い入れの効果的なタイミング（2点）: 現在PERと過去5年平均PER（簡易推定）の比較で評価
　（Sprint22はMOS基準・単年、Sprint23はPER基準・複数年トレンドで異なる）

analysis/share_buyback.py

Share Buyback分析モジュール（共通形式）

### 修正

data/data_fetcher.py

Share Buyback関連フィールド追加（複数年データ、yfinanceの複数年カラムをそのまま利用）

buyback_history（自社株買い額の複数年推移）

shares_outstanding_history（期中平均株式数の複数年推移）

total_debt_history（総負債の複数年推移）

avg_price_5y（過去5年終値平均）

trailing_eps（トレーリングEPS）

analysis/analysis_bundle.py

create_analysis_bundle() に share_buyback を追加（is_full時）

analysis/overall_eval.py

_score_share_buyback() 追加（10点満点）

判定基準を160点満点に合わせて全面更新（S:140 / A:117 / B:97 / C:77）

ai/ai_analysis.py

generate_share_buyback_analysis() 追加（Gemini評価、フォールバック付き）

report/report.py

create_share_buyback_display() 追加

report/pdf_report.py

PDFにShare Buybackセクション追加

app.py

定性分析タブ + PDFダウンロードにShare Buyback表示追加

（import / bundle展開 / 表示 / PDF引数の4箇所を編集）

health_check.py

Sprint23検証を追加（engines/analysis/ai/reportのimport確認、
bundle["share_buyback"]がNoneでないこと、overall detailへの配線確認）

### スコア配分（160点満点、Sprint23時点）

Buffett Score: 40点

DCF: 20点

MOAT: 15点

ブランド: 10点

経営者: 10点

Red Team: 5点

ROIC: 15点

Owner Earnings: 10点

Intrinsic Value: 15点

Capital Allocation: 10点

Share Buyback: 10点（新規）

### 判定基準（Sprint23更新後）

S: 140点以上

A: 117点以上

B: 97点以上

C: 77点以上

D: 77点未満

---

# Sprint24 完了内容

## Debt Quality（負債の質）分析

負債の「量」（Share Buyback／Sprint23で複数年推移を評価済み）ではなく「質」を
評価する分析軸を新設。既存のROIC分析（投下資本に総負債を使用）、Capital
Allocation分析（財務健全性の一部評価）、Share Buyback分析（total_debt_history
で負債推移を取得済み）とは異なる切り口で、負債の返済能力・構成・リスクを
独立して深掘りする（重複実装禁止・ルール14）。

### 新規作成

engines/debt_quality_engine.py

Debt Quality計算エンジン（ルールベース）

4軸で評価（合計10点満点）：

・負債水準の適正さ（3点）: D/E比率とDebt/EBITDA倍率のうち、厳しい方の水準を採用して評価
・金利負担能力（3点）: インタレスト・カバレッジ・レシオ（営業利益 ÷ 支払利息）で評価
・負債の質・構成（2点）: 短期負債 ÷ 総負債の比率（借り換えリスク）で評価
・負債推移のトレンド（2点）: total_debt_history（Sprint23で取得済み）の年平均変化率で評価
　（Sprint23の「財務健全性とのバランス」軸は自社株買いと負債増の同時発生を
　単純な始点・終点比較で見る一方、本軸は自社株買いと無関係に負債推移そのものの
　年平均変化率を独立して評価する点で異なる）

無借金企業（total_debt <= 0）は水準・金利負担・構成の3軸を満点として扱う特例あり。

analysis/debt_quality.py

Debt Quality分析モジュール（共通形式）

### 修正

data/data_fetcher.py

Debt Quality関連フィールド追加

interest_expense（支払利息、income_stmtから複数ラベル候補で取得）

※debt_to_equity / total_debt / long_term_debt / short_term_debt / ebitda /
operating_income は既存フィールドをそのまま再利用（重複取得なし）

analysis/analysis_bundle.py

create_analysis_bundle() に debt_quality を追加（is_full時）

analysis/overall_eval.py

_score_debt_quality() 追加（10点満点）

判定基準を170点満点に合わせて全面更新（S:149 / A:124 / B:103 / C:82）

ai/ai_analysis.py

generate_debt_quality_analysis() 追加（Gemini評価、フォールバック付き）

report/report.py

create_debt_quality_display() 追加

report/pdf_report.py

PDFにDebt Qualityセクション追加

app.py

定性分析タブ + PDFダウンロードにDebt Quality表示追加

（import / bundle展開 / 表示 / PDF引数の4箇所を編集）

health_check.py

Sprint24検証を追加（engines/analysis/ai/reportのimport確認、
bundle["debt_quality"]がNoneでないこと、overall detailへの配線確認）

### スコア配分（170点満点、Sprint24時点）

Buffett Score: 40点

DCF: 20点

MOAT: 15点

ブランド: 10点

経営者: 10点

Red Team: 5点

ROIC: 15点

Owner Earnings: 10点

Intrinsic Value: 15点

Capital Allocation: 10点

Share Buyback: 10点

Debt Quality: 10点（新規）

### 判定基準（Sprint24更新後）

S: 149点以上

A: 124点以上

B: 103点以上

C: 82点以上

D: 82点未満

---

# Sprint25 完了内容

## Economic Moat強化（経済的堀の定量的検証）分析

既存のMOAT評価（Sprint18、ai/ai_analysis.pyのgenerate_moat_analysis）は、単年の
ROE・営業利益率等の断面データをもとにGeminiが定性的に6観点（ブランド力／規模の
経済／価格決定力／ネットワーク効果／スイッチングコスト／規制障壁）を判定し、
wide/narrow/noneを決めるAI判定のみであり、複数年のルールベース検証が存在しな
かった。Sprint25では、この定性判定を「複数年の定量トレンド」で裏付ける独立した
ルールベース分析軸を新設した。既存のMOAT判定（qualitative）とは評価データ・
評価軸ともに重複しない（重複実装禁止・ルール14）。

### 新規作成

engines/moat_strength_engine.py

Economic Moat強化計算エンジン（ルールベース）

4軸で評価（合計10点満点）：

・収益性の持続性・安定性（3点）: ROE（優先）または営業利益率の複数年推移の
　水準（平均）と変動係数（CV=標準偏差／平均）で評価。moatが「本物」であることの
　定量的裏付けとする。
・価格決定力の定量的検証（3点）: 粗利率（Gross Profit÷売上高、取得不可の場合は
　EBITDAマージンで代替）の直近年 vs 過去平均の防衛度合いで評価。コスト上昇局面
　でも利益率を防衛できているか（値上げ耐性）を検証する。
・市場地位の安定性（2点）: 売上高成長率の複数年推移のブレ幅（標準偏差・最小値）
　で評価。急激な浮沈がなく、安定的にシェアを維持・拡大しているかを見る。
・既存MOAT判定との整合性（2点）: Sprint18のgenerate_moat_analysisによる
　wide/narrow/none判定（引数として受け取るのみ、再計算しない）と、軸1〜3の
　定量トレンド評価（8点満点）を突合する。乖離が大きい場合は「AI判定が楽観的
　すぎる可能性があります」等の警告をwarningsに追加する。

いずれの軸も、複数年データが不足する場合は中立評価（デフォルトスコア1点、
Debt Qualityエンジンと同じ規約）とし、絶対に例外を投げない。

analysis/moat_strength.py

Economic Moat強化分析モジュール（共通形式）。analyze_moat_strength(data,
moat_result) がSprint18のMOAT判定（bundle["moat"]）を引数で受け取り、
整合性チェックに使う。

### 修正

data/data_fetcher.py

Economic Moat強化関連フィールド追加（すべてyfinanceのincome_stmt／
balance_sheetから複数年抽出、直近年が先頭、取得不可時は空リストを返し
例外を投げない）

revenue_history（売上高の複数年推移、income_stmtの"Total Revenue"）

operating_margin_history（営業利益率の複数年推移、営業利益÷売上高を年ごとに算出）

gross_margin_history（粗利率の複数年推移、売上総利益÷売上高。取得不可時はEBITDAマージンにフォールバック）

roe_history（ROEの複数年推移、当期純利益÷自己資本を年ごとに算出。balance_sheetの自己資本行と突合）

※total_debt_history等、Sprint23・24で追加済みの複数年抽出関数群の踏襲パターン
（直近年から古い年の順でリスト化、取得不可時は空リストで例外を投げない）に準拠。

analysis/analysis_bundle.py

create_analysis_bundle() にmoat_strengthを追加（is_full時）。既存MOAT判定
（bundle["moat"]、Sprint18で計算済み）をanalyze_moat_strength()に渡し、
再計算はしない。

analysis/overall_eval.py

_score_moat_strength() 追加（10点満点）

判定基準を180点満点に合わせて全面更新（S:158 / A:131 / B:109 / C:87）

ai/ai_analysis.py

generate_moat_strength_analysis() 追加（Gemini評価、フォールバック付き。
ルールベースのraw数値は上書きせず、buffet_view等の考察のみ追加）

report/report.py

create_moat_strength_display() 追加

report/pdf_report.py

PDFにEconomic Moat強化セクション追加

app.py

定性分析タブ + PDFダウンロードにEconomic Moat強化表示追加

（import / bundle展開 / 表示 / PDF引数の4箇所を編集）

health_check.py

Sprint25検証を追加（engines/analysis/ai/reportのimport確認、
bundle["moat_strength"]がNoneでないこと、overall detailへの配線確認）

### スコア配分（180点満点、Sprint25時点）

Buffett Score: 40点

DCF: 20点

MOAT: 15点

ブランド: 10点

経営者: 10点

Red Team: 5点

ROIC: 15点

Owner Earnings: 10点

Intrinsic Value: 15点

Capital Allocation: 10点

Share Buyback: 10点

Debt Quality: 10点

Economic Moat強化: 10点（新規）

### 判定基準（Sprint25更新後）

S: 158点以上

A: 131点以上

B: 109点以上

C: 87点以上

D: 87点未満

---

# Sprint26 完了内容

## Backtest（簡易品質スコア × フォワードリターン検証）分析

「過去のBuffett Score（総合判定）が高かった時点で買っていたら、実際のリターンは
どうだったか」を検証する機能。

過去の任意時点でフルのBuffett Score（DCF・AI定性MOAT判定・Red Team等を含む190点満点）
を再計算することは、当時の市場前提やGemini判定を再現できないため事実上不可能。
そのため、Sprint23〜25で取得済みの複数年データ（ROE・営業利益率・売上高・総負債の
推移）から、AI判定やDCFを含まない「簡易品質スコア代理指標」を決算期ごとに
ルールベースで算出し、実際のフォワードリターンと突き合わせて検証する簡易版とした
（重複実装禁止・ルール14。既存のscoring_engine.pyは再利用のみで再実装しない）。

### 設計上の重要な注意点（交絡の排除）

当初、フォワードリターンを「決算期から現在までの累積リターン」として計算したところ、
決算期が古いほど保有期間が長くなり複利で見かけ上リターンが伸びるという交絡
（期間長の効果）により、質の高さとは無関係に古い年ほどリターンが高く出る現象が
発生した。これを排除するため、フォワードリターンは「翌決算期（直近年のみ現在）
までの約1年間」に統一し、各決算期の品質と「その後1年程度の株価の動き」を
公平に比較できるようにした。

### 新規作成

engines/backtest_engine.py

Backtest計算エンジン（ルールベース）

4軸で評価（合計10点満点）：

・高品質年 vs 低品質年のリターン差検証（3点）: 決算期を簡易品質スコアの中央値で
　高品質群・低品質群に分け、フォワードリターンの平均差を検証する。
・最高品質期間の実績リターン（3点）: 複数年の中で最も簡易品質スコアが高かった
　決算期のフォワードリターンを評価する。
・一貫性（順位相関）（2点）: 簡易品質スコアとフォワードリターンの相関係数
　（Pearson、自前実装）で、質とリターンの関係が一貫していたかを検証する。
・現在のBuffett Scoreとの整合性（2点）: score_result（scoring_engine.pyの計算結果、
　再利用のみ）を引数として受け取り、「過去に質の高さがリターンに繋がっていたか」と
　「現在のBuffett Scoreが高水準か（70点以上）」の整合性を検証する。乖離がある場合は
　「過去は質の高さがリターンに繋がっていましたが、現在のBuffett Scoreは低下しています」
　等の警告を出す。

簡易品質スコア代理指標は、決算期ごとにROEティア・営業利益率ティア・売上成長率
ティア・負債水準（対売上高）ティアを合算して算出する（AI判定・DCFは含まない）。

いずれの軸も、フォワードリターンを算出できる決算期が3期未満の場合は中立評価
（デフォルトスコア1点、Debt Quality／Economic Moat強化エンジンと同じ規約）とし、
絶対に例外を投げない。

analysis/backtest.py

Backtest分析モジュール（共通形式）。analyze_backtest(data, score_result) が
現在のBuffett Score（score_result）を引数で受け取り、整合性チェックに使う。

### 修正

data/data_fetcher.py

Backtest関連フィールド追加

fiscal_year_end_dates（決算期末日の複数年推移、income_stmtの列から取得。
roe_history等Sprint25の各*_historyと同じ列インデックスに対応）

historical_prices_at_fiscal_year_end（各決算期末日時点の終値、
stock.history(period="10y")から該当日以前で直近の終値を検索して取得）

analysis/analysis_bundle.py

create_analysis_bundle() にbacktestを追加（is_full時）。現在のBuffett Score
（score_result、既に引数として渡されている）をanalyze_backtest()に渡す。

analysis/overall_eval.py

_score_backtest() 追加（10点満点）

判定基準を190点満点に合わせて全面更新（S:167 / A:138 / B:115 / C:92、
Sprint22〜25の閾値増分パターンS+9/A+7/B+6/C+5を踏襲）

ai/ai_analysis.py

generate_backtest_analysis() 追加（Gemini評価、フォールバック付き。
ルールベースのraw数値は上書きせず、buffet_view等の考察のみ追加）

report/report.py

create_backtest_display() 追加（決算期別の簡易品質スコア・フォワードリターンの
一覧テーブルを含む）

report/pdf_report.py

PDFにBacktestセクション追加

app.py

定性分析タブ + PDFダウンロードにBacktest表示追加

（import / bundle展開 / 表示 / PDF引数の4箇所を編集）

health_check.py

Sprint26検証を追加（engines/analysis/ai/reportのimport確認、
bundle["backtest"]がNoneでないこと、overall detailへの配線確認）

### スコア配分（190点満点、Sprint26時点）

Buffett Score: 40点

DCF: 20点

MOAT: 15点

ブランド: 10点

経営者: 10点

Red Team: 5点

ROIC: 15点

Owner Earnings: 10点

Intrinsic Value: 15点

Capital Allocation: 10点

Share Buyback: 10点

Debt Quality: 10点

Economic Moat強化: 10点

Backtest: 10点（新規）

### 判定基準（Sprint26更新後）

S: 167点以上

A: 138点以上

B: 115点以上

C: 92点以上

D: 92点未満

---

# Sprint27 完了内容

## Portfolio Risk（保有ポートフォリオのリスク分散評価）分析

「保有銘柄全体として、リスクがどれだけ分散されているか」を評価する機能。
主目的はリスク分散評価（セクター・銘柄・地域の集中度の偏り検出）。

### 設計上の重要な決定（単一銘柄向けスコアに含めない）

Sprint19〜26のすべての分析軸（ROIC・Owner Earnings・Backtest等）は「単一銘柄」を
評価単位とし、190点満点のBuffett Scoreに積み上げてBUY/WATCH/PASSを判定する
（overall_eval.py）。一方、Portfolio Riskは「複数銘柄からなるポートフォリオ全体」を
評価単位とするため、単一銘柄の総合判定に組み込むのは設計として不整合になる
（例：ポートフォリオの分散度が低いからといって、個別銘柄Aの投資判断
BUY/WATCH/PASSが変わるわけではない）。

そのため、Portfolio Riskはanalysis_bundle.py / overall_eval.pyには一切組み込まず、
独立した10点満点のポートフォリオレベル分析として実装した（200点満点への拡張は
行っていない。190点満点・判定基準（S:167/A:138/B:115/C:92）は変更なし）。

### 既存「💼 Portfolio」タブ（Sprint13〜16）との関係

新規タブとして分離せず、既存の「💼 Portfolio」タブ内の「📋 保有銘柄一覧」の下に
新セクション「🎯 Portfolio Risk」として追加した。理由：

・既存タブが既にcached_get_stock_data / calculate_buffett_scoreで各保有銘柄の
　sector・country・current_price・Buffett Scoreを取得済み（portfolio_rows）であり、
　これをそのまま再利用できる（重複実装禁止・ルール14。新規のデータ取得関数は
　一切追加していない）。
・分析対象となる「保有銘柄」の登録・削除UIと、その分析結果を同一画面内に
　置く方が自然。

### 評価軸（4観点、合計10点）

・セクター分散度（3点）: 時価評価額ベースのセクター別構成比のHHI
　（ハーフィンダール・ハーシュマン指数）で評価。
・銘柄集中度（3点）: 時価評価額ベースで最大の構成比を持つ1銘柄の比率で評価。
　セクター分散度とは異なり、個別銘柄単位での偏りを検証する（同一セクター内で
　あっても特定1社への集中を捕捉できる）。
・地域分散度（2点）: 国内（日本）／海外の構成比の内訳で評価。
・保有銘柄数の充足度（2点）: 分散効果を得るために必要な最低限の銘柄数
　（4銘柄未満は0点、8銘柄以上で満点）が確保されているかで評価。

複数のシナリオ（0銘柄・1銘柄集中・8銘柄均等分散・同一セクターへの多銘柄集中・
一部データ取得失敗）で検証済み。「同一セクターに銘柄数だけ多い」ケースで
セクター分散度が正しく0点になり、銘柄数の多さだけでは高スコアにならないこと
（軸間の交絡が無いこと）を確認した。

参考情報として、保有銘柄の時価評価額加重平均Buffett Score
（weighted_avg_buffett_score）も算出しているが、これはPortfolio Riskスコア
（10点満点）には含まれない、あくまで参考値。既存のscore_result
（app.py側で計算済み）を再利用するのみで、新たなスコア計算は行っていない。

### 新規作成

engines/portfolio_risk_engine.py

Portfolio Risk計算エンジン（ルールベース）。calculate_portfolio_risk(holdings)。

analysis/portfolio_risk.py

Portfolio Risk分析モジュール（共通形式）。analyze_portfolio_risk(portfolio_rows,
generate_ai_narrative=False)。portfolio_rowsはapp.py「💼 Portfolio」タブで
既に構築済みの一覧（holding/data/score_result/errorのリスト）をそのまま渡す。
generate_ai_narrative=Trueのときのみ_safe_ai経由でGeminiを呼び出す
（AI考察のコスト制御のため、既定はFalse）。

### 修正

ai/ai_analysis.py

generate_portfolio_risk_analysis(portfolio_raw) 追加。他のgenerate_X_analysisは
単一銘柄のdataを第一引数に取るが、本関数はポートフォリオ全体のraw結果のみを
引数に取る点が異なる（単一銘柄のdataが存在しないため）。

report/report.py

create_portfolio_risk_display() 追加（セクター別・国別・銘柄別構成比の
一覧テーブルを含む）

report/pdf_report.py

generate_portfolio_pdf_report() 追加。単一銘柄向けgenerate_pdf_report()とは
別の独立したPDF生成関数（PDFBuilderクラスは再利用）。

app.py

「💼 Portfolio」タブに「🎯 Portfolio Risk」セクションを追加
（import / 表示 / AI考察ボタン / PDFダウンロードボタンの4箇所を編集）。
Gemini呼び出しは「🤖 AIによる考察を追加する」ボタン押下時のみに限定し、
タブの再描画のたびに自動実行しないようにした（既存のフルモード等と同様、
コスト制御のため）。保有銘柄の構成（ティッカー集合）が変わった場合は、
session_stateに保持していた古いAI考察を破棄する。

health_check.py

Sprint27検証を追加（engines/analysis/ai/report/pdfのimport確認、
analyze_portfolio_risk()のスモークテスト）。portfolio_riskはbundle（単一銘柄の
create_analysis_bundle()の戻り値）には含まれない設計のため、Sprint19〜26と
異なりbundleへの組み込み確認は行わない。

### スコア配分（190点満点、Sprint27時点。変更なし）

Sprint26時点のスコア配分・判定基準（S:167/A:138/B:115/C:92/D:92点未満）から
変更なし。Portfolio Riskは190点満点の外側にある、独立した10点満点の
ポートフォリオレベル分析。

---

# Sprint28 完了内容

## Watchlist Insights（ウォッチリスト横断の集計・ランキング表示）

既存の「👀 ウォッチリスト」（Sprint14実装、target_price到達判定のみ）を拡張し、
登録銘柄全体を横断した集計・ランキングを表示する機能。主目的は既存Sprint14機能の
拡張（分析軸追加）であり、通知・アラート機能や新規タブの追加ではない。

着手前にきたと以下を確認した（依頼書の指示どおり、実装前に方針を確定してから
着手）。

・主目的：既存Sprint14ウォッチリスト機能の拡張

・評価単位：複数銘柄横断（Sprint27のPortfolio Riskと同じ設計判断を踏襲）

・190点満点スコアへの影響：なし（200点満点への拡張は行わない）

・得点化の要否：**しない**（Portfolio Riskとは異なる決定）

### 設計上の重要な決定（1）：複数銘柄横断のため独立機能とする

Sprint27のPortfolio Riskと同じ理由により、Watchlist Insightsも
analysis_bundle.py / overall_eval.py（単一銘柄のBUY/WATCH/PASS判定）には
組み込まない。ウォッチリスト全体の集計結果によって、個別銘柄の投資判断が
変わるわけではないため、単一銘柄の総合判定に混ぜるのは設計として不整合になる。

### 設計上の重要な決定（2）：Portfolio Riskと異なり得点化しない

Portfolio Risk（Sprint27）は複数銘柄横断でありながら10点満点のスコア・rating
を持つ「共通形式」（PROJECT_RULES.md Rule 12）で結果を返すが、Watchlist
Insightsはスコア・rating・共通形式のいずれも持たない。理由：

・目標株価接近度やBuffett Scoreの高さは、ランキング表示自体が既に
　自己説明的であり、あらためて0〜10点のような合成スコアに圧縮する意味が薄い
　（Portfolio Riskのセクター分散度のような「複数要素を1つの指標に集約する
　必要がある」評価軸ではない）。
・「ウォッチリストの質」を採点する明確な唯一の正解（例：分散されているほど
　良い、といったPortfolio Riskのような一方向の評価基準）が無く、無理に
　点数化すると恣意的な基準になりやすい。
・得点化しないことで、`analysis_bundle.py`の共通形式（id/title/score/
　max_score/rating/summary/details/warnings）に従う必要が無くなり、
　実装・保守がシンプルになる。

そのため、`analysis/watchlist_insights.py`の`build_watchlist_insights()`は
共通形式に従わない専用の戻り値形式（target_price_ranking / score_ranking /
sector_overlap 等）を返す。`engines/`にも計算エンジンを置いていない
（数値計算はソート・差分%計算のみで、Portfolio Riskのような多段階の
ルールベース採点ロジックが無いため、`analysis/watchlist_insights.py`内で
完結させた）。

### 表示内容（3項目、いずれもスコアなし）

・目標株価接近度ランキング：目標株価を設定した銘柄を、
　(現在値-目標株価)/目標株価×100 の昇順（到達済み＝マイナス値が先頭）で
　ソート表示。目標株価未設定の銘柄はランキング対象外（no_target_countで件数のみ表示）。
・ウォッチリスト内Buffett Scoreランキング：登録銘柄をBuffett Scoreの高い順に
　ソート表示。既存の`calculate_buffett_score`の結果（score_result、Sprint14の
　ウォッチリスト一覧で計算済み）をそのまま再利用し、新規のスコア計算は行わない
　（ルール14）。
・Portfolioとの重複・セクター構成 参考表示：保有銘柄（Portfolio）と同じ
　セクターの銘柄がウォッチリストに含まれていないかを、単純な件数集計で表示。
　Portfolio Riskのような時価評価額加重のHHI計算は行わない（得点化しない方針と
　整合させ、あくまで参考情報にとどめる）。

複数のシナリオ（通常ケース／ウォッチリスト0件／全銘柄データ取得エラー／
目標株価と現在値が完全一致する境界値／portfolio_rows省略時）で検証済み。

### AI考察（Gemini）は追加しない

Portfolio Risk・Backtest等とは異なり、Watchlist Insightsには
`generate_watchlist_insights_analysis()`のようなAI考察関数を追加していない。
理由：

・得点化しない設計であり、ランキングの数値自体が既に自己説明的なため、
　AIによる解釈の付加価値が小さい。
・Gemini呼び出しは必要最小限に留める方針（docs/AI_HANDOVER.md全体の方針）に
　照らし、スコア化しない集計機能にまでAI呼び出しを追加するのは過剰。
・個別銘柄をより深く知りたい場合は、既存のフルモード分析でAI考察を確認できる
　（Watchlist Insightsは「どれから見るべきか」のトリアージという位置づけ）。

将来的にニーズが生じた場合は、Sprint29以降で`ai_analysis.py`に追加する形で
拡張可能（後方互換を壊さずに追加できる設計）。

### PDF出力は今回追加しない

Sprint14のウォッチリスト自体に元々PDF出力機能が無く、Portfolio Riskのように
既存PDFへの追記対象も無い。得点化しないシンプルな集計機能であるため、
Sprint28では新規のPDF生成関数を追加していない。必要になった場合は
`report/pdf_report.py`に`generate_watchlist_insights_pdf_report()`のような
形で追加できる（Portfolio Riskの`generate_portfolio_pdf_report()`と同様の
パターンを踏襲すればよい）。

### 新規作成

analysis/watchlist_insights.py

Watchlist Insights集計モジュール（共通形式には従わない）。
`build_watchlist_insights(watchlist_rows, portfolio_rows=None)`。
watchlist_rowsはapp.py「👀 ウォッチリスト」タブで既に構築済みの一覧
（item/data/score_result/errorのリスト）をそのまま渡す。portfolio_rowsは
「💼 Portfolio」タブの一覧（省略可、省略時はセクター重複表示なしで動作）。

### 修正

report/report.py

create_watchlist_insights_display() 追加（目標株価接近度ランキング・
Buffett Scoreランキング・セクター件数の3テーブルをMarkdownで表示）。

app.py

「👀 ウォッチリスト」セクション（Sprint14実装の一覧表示の直後）に
「📊 Watchlist Insights」セクションを追加（import / 集計呼び出し / 表示の
3箇所を編集）。保有銘柄（Portfolio）が未登録の場合はportfolio_rowsが
未定義になるため、`portfolio_rows if portfolio_holdings else []`で
安全に空リストへフォールバックしている。

health_check.py

Sprint28検証を追加（analysis/reportのimport確認、build_watchlist_insights()の
スモークテスト。Portfolio Riskとの違いを明示するため、戻り値に"score"キーが
含まれないことも検証している）。watchlist_insightsもportfolio_riskと同様、
bundle（単一銘柄のcreate_analysis_bundle()の戻り値）には含まれない設計のため、
bundleへの組み込み確認は行わない。

### スコア配分（190点満点、Sprint28時点。変更なし）

Sprint27時点のスコア配分・判定基準（S:167/A:138/B:115/C:92/D:92点未満）から
変更なし。Watchlist Insightsは190点満点にもPortfolio Risk（10点満点）にも
含まれない、得点を持たない独立した集計・ランキング表示機能。

---

## Sprint29 完了内容（Performance改善）

Sprint29は新規の分析軸を追加するものではなく、既存機能の非機能要件改善
（処理速度・重複計算の削減）。既存の計算ロジック・スコア・判定結果は
一切変更していない（Before/Afterの比較テストで確認済み。後述）。

### 発見1：Watchlist Insightsのループ内配置バグ（Sprint28で混入）を修正

`app.py`の「📊 Watchlist Insights」セクションが、誤って
`for row in watchlist_rows:`（ウォッチリスト一覧の1銘柄ずつのカード表示ループ）
の内側に配置されていた。インデントの1段ずれにより、ウォッチリスト登録銘柄が
N件あると、`build_watchlist_insights()`の集計計算とランキング表示セクション
全体がN回繰り返して実行・表示される不具合だった（登録件数が少ないと
気づきにくい）。

対応：該当セクションをループの外側（`for row in watchlist_rows:`と同じ
インデント深さ）に移動し、ループ終了後に1回だけ実行されるよう修正。
スコア・判定結果には影響しない（Watchlist Insightsは元々得点化しない
集計表示のみのため）。

health_check.pyに`t_sprint29_watchlist_insights_placement()`を追加し、
Watchlist Insightsセクションの開始行が`for row in watchlist_rows:`と
同じインデント深さにあることをソース検査で検証、再発を防止している。

### 発見2：Portfolio／Watchlistタブの行構築がrerunのたびに毎回実行されていた問題

Streamlitはアプリ内のどこか（他タブ含む）でボタン/入力が操作されるたびに
スクリプト全体を再実行する。そのため「💼 Portfolio」「👀 ウォッチリスト」
タブの「登録銘柄ぶんループして`cached_get_stock_data()` +
`calculate_buffett_score()`を実行する」処理も、無関係な操作のたびに
毎回再実行されていた。`cached_get_stock_data()`自体は
`st.cache_data(ttl=3600)`でキャッシュ済みのためキャッシュヒット時は軽いが、
キャッシュミス時（1時間経過後・初回等）は登録銘柄数ぶんのyfinance呼び出しが
直列に発生し、Portfolio/Watchlistタブを見ていない操作のときも含めて
アプリ全体の応答が重くなる構造になっていた。

対応：構築済みのrows自体を「銘柄構成（signature）」と紐付けて
`st.session_state`に保持する共通ヘルパー `_build_rows_cached()` を追加し、
Portfolio・Watchlist両方の行構築をこの経由に統一した（重複実装禁止・
ルール14により、ヘルパーは1箇所にまとめてPortfolio/Watchlist双方から再利用）。
銘柄構成が変わっていない・かつ`cached_get_stock_data`と同じTTL（3600秒）
以内であれば、rowsの再構築（データ取得・スコア計算）自体をスキップする。
データ取得・スコア計算のロジックは一切変更していないため、出力される値は
変更前と完全に同一（鮮度の上限＝TTLも変更前と同じ3600秒のまま）。

health_check.pyに`t_sprint29_build_rows_cached_wired()`を追加し、
`_build_rows_cached()`が定義され、Portfolio・Watchlist双方の
session_stateキーから呼び出されていることをソース検査で検証している。

### Before/After比較テスト

`compare_before_after.py`（サンドボックス実行用、リポジトリ外）で、
Sprint28時点の素朴なループ実装（Before）と`_build_rows_cached()`経由の
実装（After）が、同一の入力データに対して完全に同一のrowsを返すことを
確認した。また、無関係な操作によるrerunを複数回シミュレートしても
Afterの方式ではデータ取得が再実行されないこと（キャッシュヒット）、
銘柄構成が変わった場合・TTLが超過した場合は正しく再構築されることも
あわせて確認済み。

### 測定方法について

体感で「遅い」と感じる特定の操作が無かった（きたへのヒアリング結果）ため、
今回はUI上への処理時間ログ出力等は追加せず、コード調査で見つかった
上記2件の無駄な処理（重複実行）を解消する対応にとどめた。将来的に
体感で重いと感じる操作が出てきた場合は、対象の関数呼び出し前後で
`time.perf_counter()`を使った簡易ログ出力を追加する形が、既存の
プロジェクト構成（Rule 4：app.pyはController専用）に最も自然に馴染む。

### 新規作成

なし（既存ファイルの修正のみ）。

### 修正

app.py

- 「📊 Watchlist Insights」セクションのインデント修正
  （`for row in watchlist_rows:`ループの内側→外側、1回のみ実行）
- `_build_rows_cached()`共通ヘルパーを追加
  （Portfolio「💼」・Watchlist「👀」タブの行構築処理をこの経由に統一）
- `import time`を追加（TTL判定に使用）

health_check.py

- Sprint29検証を2件追加（Watchlist Insightsのループ外配置の検証、
  `_build_rows_cached()`のPortfolio/Watchlist双方への配線検証）

### スコア配分（190点満点、Sprint29時点。変更なし）

Sprint28時点のスコア配分・判定基準（S:167/A:138/B:115/C:92/D:92点未満）から
変更なし。Sprint29は既存機能の非機能要件改善であり、新規の分析軸・得点は
追加していない。

---

## Sprint30 完了内容（Performance改善・続き）

Sprint29に続き、新規の分析軸を追加するものではなく、既存機能の非機能要件
改善（処理速度・重複計算の削減）。既存の計算ロジック・スコア・判定結果は
一切変更していない。190点満点・スコア配分・判定基準（S:167/A:138/B:115/
C:92/D:92未満）への影響もない。

実装前に、候補2（フルモード一括計算）・候補3（PDF生成）を調査し、きたに
報告・確認したうえで着手した。

### 候補2（フルモード一括計算）：調査の結果、対応不要と判断

`create_analysis_bundle()`のfullモードで計算される19分析軸
（moat/brand/mgmt/red_team + roic〜backtestの14軸 + checklist等）と、
`app.py`側の表示コード・PDF出力コードを突き合わせて調査した。

- ROIC・Owner Earnings・Intrinsic Value・Capital Allocation・Share Buyback・
  Debt Quality・Economic Moat強化・Backtestの8軸は、いずれも「🧠 定性分析」
  タブ内で`if is_full: ... st.markdown(create_X_display(X))`という形で
  個別に表示されている（app.py 531〜611行目付近）
- moat・brand・mgmt・red_teamも同様に定性分析タブで表示されている
- 上記すべてが`generate_pdf_report()`にも渡され、PDFレポートにも出力されている

→ 計算だけして画面上どこにも表示されていないもの（無駄な計算）は
見つからなかった。候補2は見送りとし、対応は行っていない。

### 候補3（PDF生成）：調査結果と対応

`report/pdf_report.py`の`generate_pdf_report()`・
`generate_portfolio_pdf_report()`を調査した。

調査で分かったこと：

- チャート画像化：なし（ReportLabでテキスト・箇条書きを直接描画するのみ。
  レーダーチャートはPlotlyでStreamlit画面表示専用に使われており、PDFには
  埋め込まれていない）
- フォント処理：`pdfmetrics.registerFont()`はモジュール読込時に1回だけ
  実行されており、レポート生成のたびに毎回登録し直してはいない
  （既に効率的）
- 単一銘柄向け`generate_pdf_report()`：`st.button("📄 PDFレポートを生成")`
  の中でのみ呼ばれており、ボタンを押すまで実行されない（無駄なし）

きたへのヒアリングの結果、体感で「遅い」と感じる特定の操作は無かった。

発見（候補3で見つかった無駄な処理）：

`💼 Portfolio`タブ内の`generate_portfolio_pdf_report(portfolio_risk_result)`
（Sprint29時点でapp.py 1135行目）が、単一銘柄向けPDFと異なり
`st.button`で囲われておらず、`st.download_button`のdata引数として
毎回無条件に呼ばれていた。Streamlitはアプリ内のどこかで操作されるたびに
スクリプト全体を再実行するため（Sprint29の発見2と同じ構造）、保有銘柄が
登録されている限り、Portfolio Risk PDFはユーザーがダウンロードするか
どうかに関わらず、無関係な操作のたびに毎回ゼロから再生成されていた
（PDF自体は画像を含まず軽量なので1回あたりの負荷は大きくないが、
無駄な再計算であることは確かである）。

対応：Sprint29の`_build_rows_cached()`が使っていた「signature + TTLで
session_stateキャッシュし、両方一致すれば再計算をスキップする」仕組みを、
rows構築以外にも使える汎用ヘルパー`_cache_by_signature()`として一般化し、
`_build_rows_cached()`自体もこれを呼び出す薄いラッパーに書き換えた
（重複実装禁止・ルール14。signature計算・TTL判定・戻り値の意味は完全に
同一のため、Portfolio/Watchlist側の挙動・出力は一切変わらない）。

Portfolio Risk PDFのバイト列生成は、この`_cache_by_signature()`経由に
した。signatureは「保有銘柄構成（portfolio_signature、既存のAI考察
リセット判定で使っているものと同じ）」と「AI考察の有無・内容
（st.session_state.portfolio_risk_ai）」の組にしている。どちらも
変わっていなければ`generate_portfolio_pdf_report()`を再実行せず、
前回生成したバイト列をそのまま返す。TTLはPortfolio/Watchlistのrows
キャッシュと同じ3600秒（cached_get_stock_dataのTTLに合わせている）。

### Before/After比較テスト

`compare_before_after_sprint30.py`（サンドボックス実行用、リポジトリ外）で、
以下を確認した。

- リファクタ後の`_build_rows_cached()`が、素朴なループ実装と完全に同一の
  rowsを返すこと（Sprint29の挙動を壊していないこと）
- `_cache_by_signature()`が、signatureが変わらない限り`build_fn()`を
  再実行しないこと（無関係な操作によるrerunを複数回シミュレートしても
  再生成されない）
- 保有銘柄構成が変わった場合、AI考察が追加された場合は、それぞれ正しく
  signatureが変わり再生成されること

また、`generate_portfolio_pdf_report()`自体（キャッシュ層を経由しない
関数そのもの）は変更していないため、同一入力に対する出力の同一性を
health_check.pyのスモークテストで確認している（ReportLabは
`canvas.save()`のたびにPDFの`/ID`（ランダムなドキュメント識別子、
メタデータ）を新規生成する仕様のため、完全なバイト一致は元々成立しない。
内容の同一性はバイト長の一致で確認した）。

### 新規作成

なし（既存ファイルの修正のみ）。

### 修正

app.py

- `_cache_by_signature(session_key, signature, build_fn, ttl_seconds=3600)`
  汎用ヘルパーを追加（Sprint29の`_build_rows_cached()`のキャッシュロジックを
  一般化したもの）
- `_build_rows_cached()`を`_cache_by_signature()`呼び出しに書き換え
  （挙動・戻り値は変更前と完全に同一）
- Portfolio Risk PDFバイト列生成（`generate_portfolio_pdf_report()`の
  呼び出し）を`_cache_by_signature()`経由に変更

health_check.py

- Sprint30検証を2件追加（`_cache_by_signature()`の配線検証、
  `generate_portfolio_pdf_report()`の出力安定性スモークテスト）

### スコア配分（190点満点、Sprint30時点。変更なし）

Sprint29時点のスコア配分・判定基準（S:167/A:138/B:115/C:92/D:92点未満）
から変更なし。Sprint30は既存機能の非機能要件改善であり、新規の分析軸・
得点は追加していない。

---

## Sprint31 完了内容（Version 2.0 Release）

新規機能追加ではなく、Sprint1〜30までの実装を集約したリリース作業。
きたに作業範囲を確認したうえで、以下3点を実施した。

### 1. README.md更新

- バージョン表記を「現在開発中 Version 0.3.0」→「Version 2.0.0」に更新
- 「Version 1.0で実装予定」（Sprint1〜2時点の予定リストのまま放置されて
  いた）を、実際にSprint1〜30で実装済みの機能一覧に置き換え
- 起動方法の`streamlit run app.py`が実際のファイル配置
  （`services/app.py`）と食い違っていたため`streamlit run services/app.py`
  に修正
- 使用技術にPlotly・ReportLab・pdfplumberを追加（requirements.txtには
  含まれていたがREADMEに記載が無かった）
- 「開発ルール」セクション（Sprint1〜2時点の5行サマリーのまま）は、
  docs/PROJECT_RULES.md（25ルールまで拡張済み）との重複・乖離を避けるため、
  重複記載をやめてdocs/PROJECT_RULES.mdへのリンクのみに変更
- 「ドキュメント」セクションを実態に合わせて更新（PROJECT.md→
  PROJECT_RULES.md、ROADMAP.mdは実際には作成されていないため削除、
  AI_HANDOVER.md・CHANGELOG.mdの「今後追加」表記を削除）

### 2. docs/CHANGELOG.md新規作成

Sprint1〜31の変更履歴をまとめたCHANGELOG.mdを新規作成した。Sprint1〜9は
詳細なSprint別記録がAI_HANDOVER.mdに残っていなかったため、app.py等の
ソースコード中のSprintコメント（Sprint6投資仮説管理、Sprint7ニュース
確認ポイント、Sprint8 PDFレポート、Sprint9 DCF分析等）から裏付けが
取れた範囲のみを記載し、確認できない詳細は推測で補わなかった。
Sprint10〜17もソースコードのコメントを根拠に一覧化した。Sprint18以降は
docs/AI_HANDOVER.mdの各Sprintセクションを要約する形で記載している。

### 3. リポジトリ内の不要ファイル整理

以下5ファイルを削除した。いずれもdocs/・services/配下のどこからも
参照されていないことを確認済み（過去のSprintでのコード配布用の一時
ファイル、または既にmainへマージ済みのSprint25/26のgit bundle）。

- fix.patch
- fix_app.py
- fix_bundle.py
- sprint25.bundle
- sprint26.bundle

### スコア配分（190点満点、Sprint31時点。変更なし）

Sprint30時点のスコア配分・判定基準（S:167/A:138/B:115/C:92/D:92点未満）
から変更なし。Sprint31は新規の分析軸・得点を追加していない。

---

## Sprint32 完了内容（総合判定(overall)をサマリータブ・PDFレポートに表示）

きたからの質問（サマリータブの「使い方 / 判定基準」・「75点以上→投資推奨」は
現在の想定と合っているか）をきっかけに全体調査を行い、その結果を踏まえて
きたに実装を依頼された。

### 発見した問題

`create_analysis_bundle()`はSprint18から毎回`overall_eval.calculate_overall_grade()`
を実行し、`bundle["overall"]`（190点満点・S〜Dグレード・BUY/WATCH/PASS判定、
Sprint19〜26で追加された14項目すべてを反映済み）を計算していたが、
`app.py`側でこれを取り出して表示している箇所が一つもなかった（Summary・
Portfolio・ウォッチリスト・比較分析・PDFレポート、いずれも未使用）。
代わりにすべての画面で`calculate_buffett_score()`（100点満点、14項目中の
1項目にすぎない）だけが表示され続けていた。

さらに、`services/src/ui/`にはSprint18時点で総合判定表示専用に作られた
部品（`render_summary_card`・`render_decision_card`等）が存在したが、
一度も`app.py`からimportされておらず未使用のままだった。うち
`render_decision_card`は6項目・`/100`正規化のままで、Sprint19〜26で
追加された8項目（ROIC等）に対応していなかった。

（「75点以上→投資推奨」自体は`calculate_buffett_score()`自身の判定
ロジックとは一致しており、その点は誤りではなかった。問題は「本来の
総合判定システムがどこにも表示されていない」ことだった。）

### 対応内容

1. **`render_decision_card()`を14項目・正しい満点に更新**
   （Buffett40/DCF20/MOAT15/ブランド10/経営者10/RedTeam5/ROIC15/
   OwnerEarnings10/IntrinsicValue15/CapitalAllocation10/ShareBuyback10/
   DebtQuality10/EconomicMoat強化10/Backtest10、合計190点）。
   計算ロジック（`calculate_overall_grade()`）自体は変更していない。

2. **サマリータブ最上部に総合判定を表示**
   `bundle.get("overall")`を取り出し、Sprint18製で未使用だった
   `render_summary_card()`・`render_decision_card()`をそのまま再利用
   （新規実装ではなく既存部品の活用、ルール14）。クイック/標準モードでは
   MOAT・ROIC等の一部項目が未評価（0点扱い）になるため、フルモードで
   ない場合は暫定値である旨のキャプションを追加した。

3. **「使い方 / 判定基準」の説明を更新**
   190点満点・S〜Dグレード・BUY/WATCH/PASSの基準を追記し、既存の
   Buffett Score（100点満点）の表はその1項目という位置づけが分かるように
   した。「75点以上→投資推奨」の表記自体は残しつつ、「Buffett Score単体の
   判定。総合判定とは別」と明記した。

4. **PDFレポートに総合判定セクションを追加**
   `generate_pdf_report()`に`overall`パラメータ（デフォルト`None`、既存
   呼び出しとの後方互換を維持）を追加し、表紙の直後・Buffett Scoreより
   前に総合判定（Grade・決定・リスク・確信度・アクション）を出力する
   ようにした。

5. **軽微な修正**：Portfolio Riskセクションのコード内コメントで
   「Buffett Score（190点満点）」とBuffett Score（実際は100点満点の一部品）
   と総合判定（190点満点）を混同していた表現を修正した
   （ユーザー非表示のコメントのみ）。

Portfolio／ウォッチリスト／比較分析タブは対象外とした（Portfolio Risk・
Watchlist Insightsは元々BUY/WATCH/PASS判定に含まれないと明記されている
独立機能のため）。

### 検証

- `calculate_overall_grade()`のdetailが14項目であること、
  `render_decision_card()`が14項目すべてに対応するラベルを持ち、満点の
  合計が190点であることをhealth_check.pyで直接検証
- `render_summary_card()` / `render_decision_card()`をfake streamlitで
  実行し、正しいラベル・比率・テキストが生成されることをサンドボックスで
  確認
- `generate_pdf_report()`を`overall`ありなし両方で呼び出し、有効なPDFが
  生成されること、`overall`ありの場合はバイト数が増える（総合判定
  セクションが追加されている）ことを確認
- Streamlit `AppTest`で`app.py`をロードし、`ui`パッケージのimportを含めて
  例外なく初期表示できることを確認（yfinance等の外部ネットワークが
  必要な実際のティッカー分析実行はサンドボックスのネットワーク制限のため
  未実施。ロジック自体は上記の直接テストで検証済み）
- health_check.py実行、Sprint32検証3件を含め`=== HEALTH: ALL OK ===`を確認

### 追記：health_check.pyのPDF検証をバイト長比較からテキスト内容検証に修正

きたのローカル（Windows）環境で`python health_check.py`を実行したところ、
「PDF report overall param」テストのみFAILした（他はすべてPASS）。
原因は、当初このテストが「overallを渡すとPDFのバイト数が増えるはず」という
バイト長比較で検証していたが、PDF内部構造（フォント・ページ分割・
ID等）の環境差により、増分がサンドボックスでも実行のたびに21〜169バイトと
安定せず、Windows環境ではさらに増加しなかったため。

計算ロジック自体（`generate_pdf_report()`本体）には問題がなく、
テストの検証方法が環境依存で脆弱だったことが原因と判明したため、
`pdfplumber`（既存の依存関係、`earnings_material.py`で決算資料解析に
使用中）でPDFのテキストを直接抽出し、「総合判定」という見出し文字列の
有無で判定する、より直接的で環境非依存な検証に変更した。

### スコア配分（190点満点、Sprint32時点。変更なし）

計算ロジック（`calculate_overall_grade()`・各`_score_X()`）は一切変更して
いない。既存の計算結果を画面・PDFに表示するようにしただけであり、
スコア配分・判定基準（S:167/A:138/B:115/C:92/D:92点未満）に変更なし。

---

## Sprint33 完了内容（未使用コード・重複実装の削除）

きたから「アプリに使われていないコードや冗長な部分、バグがあれば修正してほしい」
と依頼を受け、リポジトリ全体を調査した。実際に動いているロジックに明確な
バグは見つからなかったが、どこからもimportされていない孤立ファイルと、
ルール14（重複処理禁止）に反する重複実装が見つかったため、きたに調査結果を
報告・確認のうえ削除した。

### 発見した問題と対応

**1. どこからもimportされていない孤立ファイル（5件、削除）**

- `services/market_data.py`：Sprint初期のデバッグ用スタブ
  （`print(f"DEBUG: ...")`とダミーデータを返すだけの関数）。どこからも
  参照されていなかった。
- `services/src/checklist_engine.py`：Sprint18の旧import互換ラッパー
  だが、実際には`data_fetcher.py`等の他ラッパーと違いapp.pyからも
  どこからも`import`されていなかった。
- `services/src/overall_eval.py`：同上、未使用の互換ラッパー。
- `services/src/gemini.py`：同上、未使用の互換ラッパー。
- `services/src/engines/dcf_analysis.py`：`engines`パッケージ内の
  重複ラッパー。app.pyは`src`直下の`dcf_analysis.py`経由で
  `engines.dcf_engine`を直接呼んでおり、こちらは完全に迂回されていた。

**2. 重複実装（ルール14違反）かつ未使用（削除）**

- `services/src/engines/checklist_engine.py`内の`create_radar_chart` /
  `create_score_bar` / `create_checklist_display`の3関数：
  `report/report.py`に同名の別実装があり、app.pyが実際に使っているのは
  そちら側。engines側の3関数は丸ごとデッドコードだった（同ファイル内の
  `generate_buffett_checklist_rule`のみ実際に使用されているため、これは
  残した）。ファイル冒頭の`import plotly.graph_objects as go`も、この3関数
  でのみ使われていたため合わせて削除した。
- `services/src/ai/ai_analysis.py`内の`_generate_rule_checklist()`：
  `engines/checklist_engine.py`の`generate_buffett_checklist_rule()`と
  ほぼ同一のロジック（経営圏・MOAT・財務健全性等の判定）を持つ関数だが、
  AI呼び出し失敗時のフォールバックは実際には`generate_buffett_checklist_rule`
  の方を呼んでおり（279行目）、`_generate_rule_checklist`自体はどこからも
  呼ばれていなかった。

**3. Sprint18で作られたが未配線のままのUI部品（Sprint32で見つかった
`render_decision_card`と同じパターン、削除）**

- `services/src/ui/score_card.py`（`render_score_card`）：app.pyは同等の
  表示を`create_score_bar`の直接呼び出しでインライン実装済みで、
  こちらは一度もimportされていなかった。
- `services/src/ui/chart_panel.py`（`render_chart_panel`）：同上、
  `create_radar_chart`の直接呼び出しと重複しており未使用だった。
- `services/src/ui/financial_table.py`（`render_financial_table`）：
  対応する代替のインライン実装すら無く、機能自体がどの画面にも
  表示されていなかった。Sprint32の`render_decision_card`のように
  「配線して活かす」選択肢もきたに提示したが、削除の方針で確認を得た。

`services/src/ui/__init__.py`は、削除した3部品のimportを取り除き
`render_summary_card` / `render_decision_card`のみを公開するよう更新した。

### 検証

- 削除前に、各ファイル・各関数について`grep`でリポジトリ全体を検索し、
  他のどこからも参照されていないことを確認したうえで削除した。
- 削除・編集した既存ファイルはRule 18に従い編集前後でBOM有無を確認した
  （`services/src/ai/ai_analysis.py`はBOM付きUTF-8のため、`_generate_rule_checklist`
  部分のみを置換しBOMを維持。他の削除・書き換えファイルはBOM無しのまま維持）。
- health_check.pyに新規Sprint33検証を1件追加し、削除したファイルが
  実際に存在しないこと、`engines.checklist_engine`に
  `generate_buffett_checklist_rule`のみが残っていること、
  `ai.ai_analysis`から`_generate_rule_checklist`が削除されていること、
  `ui`パッケージが`render_summary_card` / `render_decision_card`のみを
  公開していることを直接検証するようにした。
- 併せて、既存のSprint検証（1件目「legacy wrappers import」と3件目
  「Phase3 members」）が、今回削除した`checklist_engine` / `gemini` /
  `overall_eval`（旧トップレベル互換ラッパー）や
  `render_financial_table` / `render_score_card` / `render_chart_panel`
  （旧UI部品）をimportし続けていたため、削除に合わせてテスト対象の
  リストを更新した（放置すると削除自体がFAILの原因になってしまうため）。
- health_check.py実行、Sprint33検証を含め`=== HEALTH: ALL OK ===`を確認。

### スコア配分（190点満点、Sprint33時点。変更なし）

未使用コードの削除と重複実装の整理のみであり、計算ロジック・スコア配分・
判定基準（S:167/A:138/B:115/C:92/D:92点未満）に変更はない。

### 次のSprintに向けて（設計方針書を新設）

Sprint33完了後、きたと「スコア推移の履歴保存」「複数銘柄一括スクリーニング」
を次の開発対象として決定した。この2機能は、Sprint1〜33を通じて一度も
必要にならなかった「session_stateを超えた永続化」を初めて必要とするため、
実装に入る前に土台となる設計思想を`docs/DESIGN_HISTORY_AND_SCREENING.md`
としてまとめた。次のSprintに着手する際は、このファイルを
AI_HANDOVER.md・PROJECT_RULES.mdと合わせて必ず読むこと。

---

## Sprint34-1 完了内容（DCF未計算バグの修正）

以前の`services/app.py`では、分析開始時に

```python
dcf_result = globals().get("dcf_result") or {}
```

としており、この時点ではまだDCFが一度も計算されていなかった（DCFは定量分析タブの
スライダー操作時に初めて`calculate_dcf()`が呼ばれる構造だったため）。その結果、
`create_analysis_bundle()`へは常に空の`{}`が渡されており、初回分析時のAI総合判定が
DCF結果を反映しないまま生成されていた。

修正は1箇所のみ。

```python
# Sprint34-1: calculate the default DCF before building the analysis bundle.
dcf_result = calculate_dcf(data)
```

（定量分析タブ側でスライダー付きの`calculate_dcf()`呼び出しが別途あるが、これは
ユーザーがパラメータを変更した場合の再計算用であり、Rule 14の重複実装には当たらない。
初回のデフォルトDCFを用意する箇所が抜けていただけ。）

### 検証

- `python -m py_compile services/app.py` → PASS
- 変更前後でBOM有無（BOM付き）・改行コード（LFのみ）が変わっていないことを確認。

### 補足（2026-08-15）

このSprint34-1の修正は、きたがローカルで別途手動適用していたコミット
（`1cc2c36 Sprint34-1: calculate DCF before integrated analysis`）として
GitHub main へ先に反映された。本セッションで作成したbundleは、その
コミットを土台に作り直し、Sprint34-2・Sprint34-3のみを積み増す形に
更新している（内容自体は完全に同一の修正）。

## Sprint34-2 完了内容（データ取得不能を減点扱いにしない）

### 発見した問題

`services/src/engines/scoring_engine.py`の`calculate_buffett_score()`は、
ROE・営業利益率・D/E・PER・FCF・売上成長率・PBR・ROAの8項目を採点するが、
データが取得できない項目は`scores`（達成点リスト）に加算されない一方で、
`max_score`（分母）は常に固定の100点のままだった。そのため、取得できた項目が
少ないほど`total_score`が下がる＝「データが取得できなかっただけ」で暗黙に
減点される構造になっていた。加えて、データなし項目も`"passed": False`と
なるため、UI（`app.py`の採点詳細）では「悪い評価」と見分けがつかず、
どちらも❌アイコンで表示されていた。

### 設計方針

修正は`services/src/engines/scoring_engine.py`のみに閉じた（`overall_eval.py`の
`_score_buffett()`は、0〜100点の`total_score`をバケット分けするだけの既存ロジックを
変更せず利用できるため、190点満点の統合ロジックには一切手を入れていない）。

- 各項目の`details`エントリに`data_available`（bool）を追加。既存の
  `"value": "データなし"`マーカーが8項目すべてで一貫して使われていたため、
  それを再利用して判定し、新たな条件分岐の重複（Rule 14）を避けた。
- `total_score`は、データが取得できた項目の実得点合計 ÷ データが取得できた
  項目の`max_score`合計 × 100 で算出するよう変更（達成率ベースの正規化）。
  データ取得不能な項目は分子・分母の両方から除外されるため、減点として
  作用しなくなる。全項目が取得できない場合のみ`total_score = 0`とする
  フォールバックを維持（採点材料が皆無の場合は「未評価」より「0点」として
  扱い、`data_coverage`側で0%であることを明示する設計とした）。
- 戻り値に`data_coverage`（`available_items` / `total_items` / `coverage_pct`）
  を追加し、何割のデータが取得できたかを外部から参照できるようにした。
- `verdict`（✅/🟡/⚠️/❌）や190点満点の判定基準（S:167等）は変更なし。

### app.py側の対応

- 採点詳細の各項目アイコンを、`data_available`が`False`の場合は❓（未評価）、
  それ以外は従来通り✅/❌（`passed`）で出し分けるよう変更。
- 採点詳細セクションの直下に「データ取得率: n/8項目（xx.x%）」のキャプションを
  追加し、`data_coverage`を可視化した。

### 検証

- `python -m py_compile` → `services/app.py` / `services/src/engines/scoring_engine.py`
  ともにPASS。
- 編集前後でBOM有無・改行コードが変わっていないことを確認
  （`app.py`：BOM付き・LF、`scoring_engine.py`：BOM無し・LF、いずれも維持）。
- health_check.py（Windowsパス依存のためサンドボックスでは一時的にパスのみ
  差し替えて実行）：Gemini APIキー未設定によるFAIL以外は全てPASS。
  既存のSprint29/30/32回帰テスト（app.pyのソースを直接検査するもの）も
  引き続きPASSしており、既存配線を壊していないことを確認した。
- `calculate_buffett_score()`単体で以下4パターンを検証し、期待通りの
  挙動であることを確認：
  1. 全8項目データあり・全て優良 → 100/100
  2. 3項目のみデータあり（全て優良）・残り5項目欠損 →
     100/100（データ取得率37.5%を明示、欠損による減点なし）
  3. 全項目データなし → 0/100（`data_coverage`は0%として明示）
  4. 5項目データあり（全て悪い評価）・3項目欠損 →
     0/100（悪い値は正しく減点され、欠損はスコアに影響しない）

### 副次対応：.gitignoreの文字化け修正

調査時に、`.gitignore`末尾付近でUTF-16とUTF-8が混在した破損データ
（`.envs`の直後にヌルバイト混じりの`print22.patch`という文字列が挿入され、
本来別行のはずの`*.bundle`エントリと結合してしまっていた）を発見した。
きたに確認のうえ、破損箇所を除去し、`*.bundle`エントリのみをクリーンな
1行として復元した（改行コードはCRLFのまま維持）。

### 今回発見したが対応を見送った点（次Sprint以降の候補）

- `services/src/engines/roic_engine.py`など他の採点エンジンにも、
  `scoring_engine.py`と同様に「データ取得不能→暗黙の減点」パターンが
  ある可能性がある（ざっと確認した限り類似コードが見られた）。
  今回はきたの指示通り`scoring_engine.py`（Buffett Score）に対象を絞った。
- `overall_eval.py`の`_confidence()`はBuffett Scoreの値そのものを見て
  Confidence（High/Medium/Low）を判定しているため、データ取得率が
  極端に低いのに達成率が高いケース（例：8項目中2項目しか無いが両方優良）
  では、実態よりConfidenceが高く表示される可能性がある。今回のSprintでは
  スコープを広げず未対応とした。
- Sprint34全体の最終目標（ティッカー入力のみでの自動評価、ニュースの
  総合判定への統合等）は未着手。まずSprint34-2の「データなし≠減点」の
  是正のみを完了した段階。

### 次のSprintに向けて

Sprint34-3の候補：ニュース結果を190点総合判定へどう統合するか、
または上記roic_engine.py等の同型問題への対応。きたと相談のうえ決定する。

---

## Sprint34-3 完了内容（他エンジンの同型「データ欠損=暗黙の減点」バグ調査・修正）

Sprint34-2完了後、きたの指示で`services/src/engines/`配下の全9エンジンを
横断調査し、同種の問題がないか確認した。

### 調査結果

**同型バグが見つかったファイル（2件、修正）**

- `capital_allocation_engine.py`（Sprint22）：`reinvestment_score`
  （4点満点）が、ROICデータ取得不能時に初期値`0`のまま変更されず
  返されていた（最低評価と同じ扱い）。
- `share_buyback_engine.py`（Sprint23）：`consistency_score`・
  `reduction_score`（各3点満点）が、複数年データ不足時に初期値`0`の
  まま変更されず返されていた。同ファイル内の`balance_score`・
  `timing_score`は既に中立評価（1点）で正しく実装されており、
  一貫性がなかった。

**すでに正しく実装されていたファイル（問題なし）**

- `debt_quality_engine.py`（Sprint24）・`moat_strength_engine.py`
  （Sprint25）・`backtest_engine.py`（Sprint26）：全軸とも、データ欠損時は
  最初から中立評価（各軸max3点→1点、max2点→1点）を返す設計になっていた。
- `intrinsic_engine.py`（Sprint21）：「データ不足の方式はスキップし、
  利用可能な方式のみで重みを再正規化する」と設計時から明記されており、
  Sprint34-2と同種の正規化が既に実装済みだった。

**対象外と判断したファイル**

- `roic_engine.py`（Sprint19）・`owner_earnings_engine.py`（Sprint20）：
  固定満点に対する複数項目集計ではなく単一指標（比率）を返す設計のため、
  データ欠損時は`rating: "unknown"`として素直にスキップされ、
  「暗黙の減点」構造自体が存在しない。
- `portfolio_risk_engine.py`：Rule 24によりそもそも単一銘柄190点満点とは
  別枠（複数銘柄のポートフォリオ構成分析）。`score = 0`はHHI計算前の
  初期値であり、データ欠損時の減点とは別種の話のため対象外。

この結果から、「データ欠損=暗黙の減点」バグはSprint19〜23（開発初期）の
エンジンにのみ存在し、Sprint24（debt_quality）以降は開発チーム自身が
学習して既に是正済みだったことが確認できた。

### 修正内容

Sprint34-2で確立した「中立評価」の考え方を、既に是正済みの他エンジン
（debt_quality/moat_strength/backtest）と同じ水準（3点満点軸→1点、
4点満点軸→2点）に合わせて適用した。

- `capital_allocation_engine.py`：`reinvestment_score`の初期値を`0`→`2`
  （4点満点中の中間、`payout_score`/`buyback_score`の既存の欠損時扱いと
  足並みを揃えた）に変更。
- `share_buyback_engine.py`：`consistency_score`・`reduction_score`の
  初期値をそれぞれ`0`→`1`（3点満点中、同ファイルの`balance_score`/
  `timing_score`と同水準）に変更。データが存在するが実績がゼロ
  （例：自社株買い実施年数0年）の場合は、従来通り正しく0点のまま。

`total_score`の判定基準（Excellent/Good/Average等の閾値）・190点満点
構造・他エンジンとの重複判定（Rule 14/24/25）に変更なし。

### 検証

- `python -m py_compile` → 両ファイルともPASS。
- 編集前後でBOM有無（両ファイルともBOM無し）・改行コード（LFのみ）が
  変わっていないことを確認。
- health_check.py（Sprint34-2と同様、サンドボックスでは一時的にパスのみ
  差し替えて実行）：Gemini APIキー未設定によるFAIL（Sprint34-2実行時と
  同一パターン）以外、新規の回帰なし。
- `calculate_capital_allocation()` / `calculate_share_buyback()`
  単体で以下を検証：
  1. 全データ欠損 → `capital_allocation`は4/10（Average）、
     `share_buyback`は4/10（Average）。旧実装ならPoor（0点近辺）に
     なっていたところが中立評価になることを確認。
  2. ROIC優秀（30%）の場合、`reinvestment_score`は従来通り4/4満点。
  3. データはあるが自社株買い実施年数が0年の場合、`consistency_score`は
     従来通り正しく0/3のまま（「悪い」実績への減点は維持されている）。

### 次のSprintに向けて

Sprint34全体の最終目標（ニュース結果の190点総合判定への統合等）は
未着手。次はニュース統合に進むか、きたと相談のうえ決定する。

---

# 互換ラッパーについて

services/src直下には、旧import互換のためのラッパーが残っている。

例）

data_fetcher.py → data/data_fetcher.py

scoring_engine.py → engines/scoring_engine.py

ai_analysis.py → ai/ai_analysis.py

など。

削除する場合は、app.py等のimport先を新パッケージに変更してから行うこと。

---

# 今後のSprint

Sprint34-4まで完了。次SprintはGitHub最新版を再確認したうえで、Sprint34全体の
最終目標（ティッカー入力だけでの自動評価、決算資料PDFのオプション化等）の
残作業を洗い出して決定する。

---

# 注意事項

GitHub最新版を必ず確認。

重複実装禁止。

既存機能を壊さない。

分析ロジックはanalysisへ。

計算ロジックはenginesへ。

画面はuiへ。


## Sprint34-4 完了内容（ニュース結果の総合判定への安全な統合）

### 目的

ニュース取得・Gemini要約は既存実装で完了していたが、ニュース評価が190点満点の
`overall` / BUY-WATCH-PASSへ直接反映されていなかった。Sprint34-4では、
190点満点の各項目を増減させず、重大かつ信頼度の高いネガティブニュースのみを
最終Decisionの安全装置として利用する方式を採用した。

### 設計

- `services/src/ai/ai_analysis.py`
  - `generate_news_summary_result()`を追加。
  - 既存のニュース要約と、`impact / severity / confidence / reason`の構造化評価を
    1回のGemini呼び出しで取得する。
  - APIキー未設定・Gemini失敗・ニュース空の場合は`available=False`を返し、
    総合判定へ一切影響させない。
  - 既存`generate_news_summary()`は後方互換のため文字列を返すラッパーとして維持。
- `services/src/analysis/analysis_bundle.py`
  - `bundle["news_impact"]`を追加。
  - ニュース要約と構造化評価を同時にbundleへ格納。
  - `overall_eval.calculate_overall_grade()`へ`news_impact`を渡す。
- `services/src/analysis/overall_eval.py`
  - 190点満点の`overall_score`と14項目の内訳は変更しない。
  - `negative + high severity + high confidence`のニュースだけ、
    BUY→WATCH、WATCH→PASSへ一段階引き下げる。
  - PASSはさらに下げない。ニュースによってBUYへ昇格させない。
  - `base_decision` / `news_adjusted` / `news_impact`を返す。
- `services/app.py`
  - サマリー/ニュースタブにニュース影響を表示。
  - 「ニュース取得不能」「AI評価不能」は総合判定に影響しないことを明示。
- `health_check.py`
  - ニュース無しで既存判定が変わらないことを検証。
  - 重大・高信頼ネガティブニュースでDecisionだけが一段階下がることを検証。
  - 190点満点のスコアが変わらないことを検証。
  - 信頼度不足ではDecisionを変更しないことを検証。

### 重要な判断

ニュースは新しい採点項目ではないため、190点満点の配点・Grade閾値は変更しない。
またニュース取得失敗やGemini失敗を減点扱いにしない。Rule 13に従いBUY/WATCH/PASSの
決定は`overall_eval.py`だけで行う。
