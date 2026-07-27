####################################################
# portfolio.py
# Sprint13: Portfolio（保有銘柄管理）
#
# このモジュールは「保有銘柄のデータを保持する」ことだけを担当する。
# hypothesis.py（投資仮説管理）と同じ設計パターン：
#   - データを表すクラス（PortfolioHolding）
#   - 登録・削除・一覧取得を行う管理クラス（PortfolioManager）
#
# 現在株価の取得（data_fetcher.py）やBuffett Scoreの計算
# （scoring_engine.py）はこのモジュールでは行わない。
# それらはapp.py側で、既存の関数をそのまま呼び出して行う
# （新しいGemini呼び出しは一切追加していない。すべてルールベース）。
####################################################


class PortfolioHolding:
	"""1つの保有銘柄を表すクラス。

	Attributes:
		id (int): PortfolioManagerが自動採番するID
		ticker (str): ティッカーシンボル（例: "AAPL", "7203"）
		shares (float): 保有株数
		cost_basis (float): 取得単価（1株あたり）
	"""

	def __init__(self, id, ticker, shares, cost_basis):
		self.id = id
		self.ticker = ticker
		self.shares = shares
		self.cost_basis = cost_basis


class PortfolioManager:
	"""保有銘柄の登録・削除・一覧取得を管理するクラス。

	Sprint13時点ではセッション中のみデータを保持する
	（JSON保存/読込は行わない。Sprint14以降で検討）。
	"""

	def __init__(self):
		self.holdings = []
		self._next_id = 1

	def add(self, holding):
		"""保有銘柄を1件追加する。idはこのメソッド内で自動採番する。"""
		holding.id = self._next_id
		self._next_id += 1
		self.holdings.append(holding)

	def delete(self, holding_id):
		"""指定したidの保有銘柄を削除する。"""
		self.holdings = [h for h in self.holdings if h.id != holding_id]

	def get_all(self):
		"""登録されている保有銘柄を全件返す。"""
		return self.holdings

	def clear(self):
		"""全ての保有銘柄を削除する。"""
		self.holdings = []