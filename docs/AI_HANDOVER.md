# AI_HANDOVER.md

Project: Buffett Investment Analyzer
Version: Ver2
Current Sprint: Sprint18（実装開始前）

---

# GitHub

Repository

https://github.com/lazymethod97-create/buffett-invest-analyzer

GitHubを唯一の正（Single Source of Truth）とする。

以後は**設計ではなく、必ずGitHubの最新コードを確認してから実装すること。**

---

# 現在の状況

Sprint1～17は実装済み。

Sprint18の設計レビューは完了した。

今回のチャットではSprint18の設計・責務分離・Version2アーキテクチャを決定したが、

**まだGitHub最新コードへは反映していない。**

したがって、

**Sprint18は未完了**

である。

次チャットでは

GitHub最新版

↓

現状解析

↓

Sprint18実装

から開始する。

---

# 今回決定したVersion2設計

Version2では

```
app.py
```

は画面制御のみ。

分析ロジックは禁止。

Gemini呼び出しは禁止。

---

新しい構成

```
services/

app.py

src/

analysis/

ui/
```

analysis

分析・計算のみ

```
overall_eval.py

dcf_analysis.py

scoring_engine.py

ai_analysis.py
```

ui

画面表示のみ

```
summary_card.py

decision_card.py

quantitative_tab.py

qualitative_tab.py

news_tab.py

portfolio_tab.py

compare_tab.py

earnings_tab.py
```

---

# Sprint18で実装する内容

① analysis/

overall_eval.py

追加

返却値

```
Overall Score

Overall Grade

Risk

Confidence

Action
```

AIは使用しない。

---

② ui/

summary_card.py

追加

Summaryタブ表示専用。

---

③ ui/

decision_card.py

追加

Strong Buy

Buy

Watch

Hold

Avoid

表示専用。

---

④ ai_analysis.py

```
generate_overall_summary()
```

追加。

Geminiは文章生成のみ。

判定は禁止。

---

⑤ app.py

analysis_bundle

導入。

```
analysis_bundle

↓

Summary

Quantitative

Qualitative

News

Portfolio

Compare

Earnings
```

へ受け渡す。

UIからGeminiを呼ばない。

---

# analysis_bundle構成

```
analysis_bundle = {

company

score

dcf

moat

brand

management

red_team

overall

overall_summary

news

}
```

Version2では

この辞書だけをUIへ渡す。

---

# GitHubで最初に行うこと

次チャット開始後、

必ず

GitHub最新版

またはZIP

を確認する。

以下を最優先で実施。

1.

現在のディレクトリ構成確認

2.

app.py解析

3.

重複機能調査

4.

analysis/uiへ移動できる機能整理

5.

依存関係確認

6.

既存コードを壊さない実装計画作成

設計だけで進めないこと。

---

# Sprint18実装手順

Sprint18-1

Version2構成作成

```
analysis/

ui/
```

追加

Git Commit

```
Sprint18-1
Create Version2 Architecture
```

---

Sprint18-2

overall_eval.py

実装

Git Commit

```
Sprint18-2
Implement Overall Evaluation Engine
```

---

Sprint18-3

summary_card.py

decision_card.py

実装

Git Commit

```
Sprint18-3
Split Summary UI
```

---

Sprint18-4

analysis_bundle

導入

app.py軽量化

Gemini呼び出し一本化

Git Commit

```
Sprint18-4
Centralize Analysis Bundle
```

---

Sprint18-5

不要コード整理

PROJECT_RULES更新

AI_HANDOVER更新

GitHubレビュー

Git Commit

```
Sprint18-5
Complete Sprint18 Version2
```

---

# 実装ルール

今回から最重要ルールを変更する。

単にコードを書くことをSprint完了としない。

以下すべて終えて初めてSprint完了とする。

・GitHub構成変更

・必要なファイル分割

・不要コード整理

・重複コード削除

・app.py軽量化

・PROJECT_RULES更新

・AI_HANDOVER更新

・Gitコミット単位作成

・完成レビュー

---

# 次チャット開始時の最初の指示

以下をそのままAIへ送る。

---

あなたはBuffett Investment Analyzer Ver2の主任ソフトウェアエンジニアです。

AI_HANDOVER.mdとPROJECT_RULES.mdを最初に読んでください。

GitHubを唯一の正とします。

今回は設計ではなく実装を行います。

必ずGitHub最新版（またはアップロードしたZIP）のコードを確認してから開始してください。

現在の構成・依存関係・重複機能を調査し、Sprint18をGitHub構成変更・ファイル分割・PROJECT_RULES更新・AI_HANDOVER更新・Gitコミットまで含めて完成させてください。

既存コードは壊さず、コピペで動く完成版のみを作成してください。

Sprint18完了後にSprint19（ROIC分析）へ進めます。
