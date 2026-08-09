# PROJECT_RULES.md

# Buffett Investment Analyzer Ver2

## 開発ルール

---

# 1.

GitHubを唯一の正とする。

ローカルコードを基準にしない。

---

# 2.

Sprint単位で開発する。

Sprint開始時

↓

GitHub最新版確認

↓

重複機能確認

↓

設計確認

↓

実装

↓

テスト

↓

Git Commit

↓

AI_HANDOVER更新

↓

PROJECT_RULES更新

---

# 3.

既存コードを壊さない。

動作中の機能を書き換えない。

必要ならWrapperを追加する。

---

# 4.

app.pyへ分析ロジックを書かない。

Controllerのみ。

---

# 5.

分析処理

src/analysis

---

# 6.

数値計算

src/engines

---

# 7.

画面

src/ui

---

# 8.

データ取得

src/data

---

# 9.

AI

src/ai

---

# 10.

PDF

src/report

---

# 11.

analysis_bundleへ必ず登録する。

新分析追加時

analysis_bundle

↓

overall_eval

↓

UI

↓

PDF

まで追加する。

---

# 12.

分析モジュールは共通形式を返す。

{
    id,
    title,
    score,
    max_score,
    rating,
    summary,
    details,
    warnings
}

---

# 13.

総合判定はoverall_evalだけ。

BUY

WATCH

PASS

ここだけで決定。

---

# 14.

新機能追加時

重複処理禁止。

既存機能を流用する。

---

# 15.

Git Commit

Sprint終了時

必ず

git add .

git commit -m "SprintXX: 内容"

git push origin main

まで行う。

---

# 16.

AIへ依頼するとき

必ず

・AI_HANDOVER.md

・PROJECT_RULES.md

を最初に読ませる。

GitHub最新版を確認させる。

設計ではなく実装を行わせる。

完成版コードのみ作成させる。

---

# 17.

Sprint18で確定したディレクトリ構成。

services/src配下にサブパッケージを置く。

[分析] src/analysis

[計算] src/engines

[データ] src/data

[AI] src/ai

[画面] src/ui

[PDF] src/report

旧配置には互換ラッパーを残す。

新規コードは新パッケージに書く。

---

# 18.

PowerShellスクリプトでファイルを生成・編集する際の文字コード規則（Sprint20で追加）。

`Set-Content -Encoding UTF8`（Windows PowerShell 5.1）は自動的にBOM付きUTF-8として保存する。

ヒアストリング（@'...'@）の中に、AIが誤ってBOM文字（\ufeff）を手動で含めてはならない。
BOMが二重になり、`SyntaxError: invalid non-printable character U+FEFF`が発生する。

既存ファイルを`.Replace()`等で部分編集する場合は、`Get-Content -Raw`で読んだ生データをそのまま使い、
BOM文字を追加/削除しない。

既存ファイルの改行コード（CRLF/LF）が不明な場合は、比較前に`-replace "`r`n", "`n"`でLFに正規化してから
文字列比較を行い、書き込み前に`-replace "`n", "`r`n"`で元の形式に戻す（Windows環境はCRLFが基本）。

# 19.

Sprint22以降のスコア配分（150点満点）。

Buffett Score: 40 / DCF: 20 / MOAT: 15 / ブランド: 10 / 経営者: 10 / Red Team: 5 / ROIC: 15 / Owner Earnings: 10 / Intrinsic Value: 15 / Capital Allocation: 10

判定基準の詳細はAI_HANDOVER.mdを参照。

# 20.

Sprint23以降のスコア配分（160点満点）。

Buffett Score: 40 / DCF: 20 / MOAT: 15 / ブランド: 10 / 経営者: 10 / Red Team: 5 / ROIC: 15 / Owner Earnings: 10 / Intrinsic Value: 15 / Capital Allocation: 10 / Share Buyback: 10

判定基準（S:140 / A:117 / B:97 / C:77 / D:77未満）の詳細はAI_HANDOVER.mdを参照。

# 21.

Sprint24以降のスコア配分（170点満点）。

Buffett Score: 40 / DCF: 20 / MOAT: 15 / ブランド: 10 / 経営者: 10 / Red Team: 5 / ROIC: 15 / Owner Earnings: 10 / Intrinsic Value: 15 / Capital Allocation: 10 / Share Buyback: 10 / Debt Quality: 10

判定基準（S:149 / A:124 / B:103 / C:82 / D:82未満）の詳細はAI_HANDOVER.mdを参照。

# 22.

Sprint25以降のスコア配分（180点満点）。

Buffett Score: 40 / DCF: 20 / MOAT: 15 / ブランド: 10 / 経営者: 10 / Red Team: 5 / ROIC: 15 / Owner Earnings: 10 / Intrinsic Value: 15 / Capital Allocation: 10 / Share Buyback: 10 / Debt Quality: 10 / Economic Moat強化: 10

判定基準（S:158 / A:131 / B:109 / C:87 / D:87未満）の詳細はAI_HANDOVER.mdを参照。

Economic Moat強化（moat_strength）は、既存のMOAT定性判定（Sprint18、単年断面データのAI判定）とは
評価データ・評価軸ともに重複しない、複数年の定量トレンドによる独立したルールベース検証軸である
（ルール14）。既存MOAT判定は再計算せず、整合性チェックの引数として受け取るのみとする。

# 23.

Sprint26以降のスコア配分（190点満点）。

Buffett Score: 40 / DCF: 20 / MOAT: 15 / ブランド: 10 / 経営者: 10 / Red Team: 5 / ROIC: 15 / Owner Earnings: 10 / Intrinsic Value: 15 / Capital Allocation: 10 / Share Buyback: 10 / Debt Quality: 10 / Economic Moat強化: 10 / Backtest: 10

判定基準（S:167 / A:138 / B:115 / C:92 / D:92未満）の詳細はAI_HANDOVER.mdを参照。

Backtest（backtest）は、過去の任意時点でフルのBuffett Score（DCF・AI定性MOAT判定・
Red Team等を含む）を再計算することが事実上不可能なため、Sprint23〜25で取得済みの
複数年データ（ROE・営業利益率・売上高・総負債の推移）からAI判定やDCFを含まない
簡易品質スコア代理指標をルールベースで算出し、実際のフォワードリターンと突き合わせて
検証する独立エンジンである（重複実装禁止・ルール14。既存のscoring_engine.pyは
再利用のみで再実装しない）。

フォワードリターンは「決算期から現在までの累積リターン」ではなく「翌決算期
（直近年のみ現在）までの約1年間」に統一する。決算期が古いほど保有期間が長くなり
複利で見かけ上リターンが伸びる交絡（期間長の効果）を避けるためである。

# 24.

スコア配分（190点満点）はSprint26以降変更なし。Sprint27（Portfolio Risk）は
190点満点に含めない。

Portfolio Risk（保有ポートフォリオのリスク分散評価、engines/portfolio_risk_engine.py /
analysis/portfolio_risk.py）は、Sprint19〜26までの全分析軸と異なり「複数銘柄からなる
ポートフォリオ全体」を評価単位とする。単一銘柄の190点満点スコア・BUY/WATCH/PASS判定
（overall_eval.py）とは評価単位が根本的に異なるため、analysis_bundle.py /
overall_eval.pyには組み込まない、独立した10点満点の分析として実装する。

今後、複数銘柄・ポートフォリオ全体を評価単位とする機能を追加する場合も、
単一銘柄の190点満点スコアには含めず、同様に独立した分析として実装すること。
逆に、単一銘柄を評価単位とする新規分析軸は、Sprint19〜26と同様に
analysis_bundle.py → overall_eval.py → app.py → report/ → health_check.pyまで
一通り配線すること（ルール11）。

