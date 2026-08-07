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
