####################################################
# journal.py
# Sprint16: AI投資日誌（実体は「投資日誌」。手入力のみ、AI呼び出しなし）
#
# hypothesis.py（投資仮説管理）と同じ設計パターン：
#   - データを表すクラス（JournalEntry）
#   - 登録・削除・一覧取得・JSON保存/読込を行う管理クラス（JournalManager）
#
# ユーザーが日付・銘柄・売買判断・理由を自分で記録するための機能。
# Gemini（AI）は一切使用しない（手入力のみ）。
# 投資仮説管理と同様、日誌は長期保存したい人が多いため、JSON形式での
# 保存（ダウンロード）／読込（アップロード）に対応する。
####################################################

import json


class JournalEntry:
	"""1件の投資日誌エントリを表すクラス。

	Attributes:
		id (int): JournalManagerが自動採番するID
		date (str): 日付（"YYYY-MM-DD"形式の文字列）
		ticker (str): ティッカーシンボル（任意。空文字も許容）
		decision (str): 売買の判断（例："買い", "売り", "様子見", "保有継続"）
		reason (str): 判断の理由（自由記述）
	"""

	def __init__(self, id, date, ticker, decision, reason):
		self.id = id
		self.date = date
		self.ticker = ticker
		self.decision = decision
		self.reason = reason

	def to_dict(self):
		return {
			"id": self.id,
			"date": self.date,
			"ticker": self.ticker,
			"decision": self.decision,
			"reason": self.reason,
		}

	@staticmethod
	def from_dict(d):
		return JournalEntry(
			id=d.get("id", 0),
			date=d.get("date", ""),
			ticker=d.get("ticker", ""),
			decision=d.get("decision", ""),
			reason=d.get("reason", ""),
		)


class JournalManager:
	"""投資日誌の登録・削除・一覧取得・JSON保存/読込を管理するクラス。

	Sprint16時点ではJSON保存/読込に対応する
	（Portfolio／ウォッチリストとは異なり、日誌は長期保存のニーズが
	高いと想定されるため。ユーザー確認済み）。
	"""

	def __init__(self):
		self.entries = []
		self._next_id = 1

	def add(self, entry):
		"""日誌を1件追加する。idはこのメソッド内で自動採番する。"""
		entry.id = self._next_id
		self._next_id += 1
		self.entries.append(entry)

	def delete(self, entry_id):
		"""指定したidの日誌を削除する。"""
		self.entries = [e for e in self.entries if e.id != entry_id]

	def get_all(self):
		"""登録されている日誌を、日付が新しい順に並べて返す。"""
		return sorted(self.entries, key=lambda e: e.date, reverse=True)

	def clear(self):
		"""全ての日誌を削除する。"""
		self.entries = []

	def to_json(self):
		"""登録されている日誌をJSON文字列に変換する（保存用）。"""
		return json.dumps(
			[e.to_dict() for e in self.entries], ensure_ascii=False, indent=2
		)

	def load_from_json(self, json_str):
		"""JSON文字列から日誌を読み込む（読込用）。既存の日誌は置き換えられる。"""
		data = json.loads(json_str)
		self.entries = []
		max_id = 0
		for d in data:
			entry = JournalEntry.from_dict(d)
			self.entries.append(entry)
			if entry.id and entry.id > max_id:
				max_id = entry.id
		self._next_id = max_id + 1