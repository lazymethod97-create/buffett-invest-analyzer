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

現在Sprint23完了。

次回はSprint24（Debt Quality）から開始。

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

Sprint24

Debt Quality

Sprint25

Economic Moat強化

Sprint26

Backtest

Sprint27

Portfolio Analyzer

Sprint28

Watchlist

Sprint29

Performance改善

Sprint30

Version2.0 Release

---

# 注意事項

GitHub最新版を必ず確認。

重複実装禁止。

既存機能を壊さない。

分析ロジックはanalysisへ。

計算ロジックはenginesへ。

画面はuiへ。
