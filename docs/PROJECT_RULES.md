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
