####################################################
# watchlist.py
# Sprint14: ウォッチリスト（保有はしていないが気になっている銘柄の管理）
#
# portfolio.py（保有銘柄管理）と同じ設計パターン：
#   - データを表すクラス（WatchListItem）
#   - 登録・削除・一覧取得を行う管理クラス（WatchListManager）
#
# 現在株価の取得（data_fetcher.py）やBuffett Scoreの計算
# （scoring_engine.py）はこのモジュールでは行わない。
# それらはapp.py側で、既存の関数をそのまま呼び出して行う
# （新しいGemini呼び出しは一切追加していない。すべてルールベース）。
####################################################


class WatchListItem:
	"""ウォッチリストに登録する1銘柄を表すクラス。

	Attributes:
		id (int): WatchListManagerが自動採番するID
		ticker (str): ティッカーシンボル（例: "AAPL", "7203"）
		target_price (float | None): 目標株価（未設定の場合はNone）
		memo (str): 任意のメモ
	"""

	def __init__(self, id, ticker, target_price=None, memo=""):
		self.id = id
		self.ticker = ticker
		self.target_price = target_price
		self.memo = memo


class WatchListManager:
	"""ウォッチリストの登録・削除・一覧取得を管理するクラス。

	Sprint14時点ではセッション中のみデータを保持する
	（JSON保存/読込は行わない。保有銘柄管理と同様の方針）。
	"""

	def __init__(self):
		self.items = []
		self._next_id = 1

	def add(self, item):
		"""ウォッチリストに1件追加する。idはこのメソッド内で自動採番する。"""
		item.id = self._next_id
		self._next_id += 1
		self.items.append(item)

	def delete(self, item_id):
		"""指定したidの項目を削除する。"""
		self.items = [i for i in self.items if i.id != item_id]

	def get_all(self):
		"""登録されている項目を全件返す。"""
		return self.items

	def clear(self):
		"""全ての項目を削除する。"""
		self.items = []