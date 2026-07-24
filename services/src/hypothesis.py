"""
投資仮説管理モジュール
分析結果を基に投資仮説を自動生成し、ステータス管理・手動編集を行う。
"""

import json
import streamlit as st
from dataclasses import dataclass, field
from typing import List
from enum import Enum


class HypothesisStatus(str, Enum):
    UNVERIFIED = "未検証"
    IN_PROGRESS = "検証中"
    VALIDATED = "成立"
    REJECTED = "却下"
    PENDING = "保留"


STATUS_ICON_MAP = {
    HypothesisStatus.UNVERIFIED: "🟡",
    HypothesisStatus.IN_PROGRESS: "🔵",
    HypothesisStatus.VALIDATED: "🟢",
    HypothesisStatus.REJECTED: "🔴",
    HypothesisStatus.PENDING: "⚪",
}


@dataclass
class InvestmentHypothesis:
    id: int
    title: str
    rationale: str
    evidence: List[str] = field(default_factory=list)
    verification_items: List[str] = field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.UNVERIFIED
    source: str = "ai"  # "ai" or "user"

    @property
    def status_icon(self) -> str:
        return STATUS_ICON_MAP.get(self.status, "⚪")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "rationale": self.rationale,
            "evidence": self.evidence,
            "verification_items": self.verification_items,
            "status": self.status.value,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "InvestmentHypothesis":
        try:
            status = HypothesisStatus(d.get("status", "未検証"))
        except ValueError:
            status = HypothesisStatus.UNVERIFIED

        return cls(
            id=d["id"],
            title=d["title"],
            rationale=d["rationale"],
            evidence=d.get("evidence", []),
            verification_items=d.get("verification_items", []),
            status=status,
            source=d.get("source", "ai"),
        )


class HypothesisManager:
    def __init__(self, session_state_key: str = "hypotheses"):
        self.session_state_key = session_state_key

    def _get_list(self) -> List[InvestmentHypothesis]:
        if self.session_state_key not in st.session_state:
            st.session_state[self.session_state_key] = []
        return st.session_state[self.session_state_key]

    def get_all(self) -> List[InvestmentHypothesis]:
        return self._get_list()

    def clear(self):
        st.session_state[self.session_state_key] = []

    def add(self, hypothesis: InvestmentHypothesis) -> InvestmentHypothesis:
        hypotheses = self._get_list()
        # 自動採番
        if hypothesis.id is None or hypothesis.id == 0:
            existing_ids = [h.id for h in hypotheses]
            hypothesis.id = max(existing_ids, default=0) + 1
        hypotheses.append(hypothesis)
        return hypothesis

    def update_status(self, hid: int, status: HypothesisStatus) -> bool:
        hypotheses = self._get_list()
        for h in hypotheses:
            if h.id == hid:
                h.status = status
                return True
        return False

    def delete(self, hid: int) -> bool:
        hypotheses = self._get_list()
        for idx, h in enumerate(hypotheses):
            if h.id == hid:
                hypotheses.pop(idx)
                return True
        return False

    def to_json(self) -> str:
        hypotheses = self._get_list()
        return json.dumps([h.to_dict() for h in hypotheses], ensure_ascii=False, indent=2)

    def load_from_json(self, json_str: str):
        data = json.loads(json_str)
        st.session_state[self.session_state_key] = [
            InvestmentHypothesis.from_dict(d) for d in data
        ]


def generate_default_hypotheses(
    data: dict,
    score_result: dict,
    checklist: list,
    moat: dict,
    brand: dict,
    mgmt: dict,
    red_team: dict,
) -> List[InvestmentHypothesis]:
    """
    分析結果からデフォルトの投資仮説をルールベースで生成する。
    API未設定時やフォールバックとして使用。
    """
    hypotheses = []
    total_score = score_result.get("total_score", 0)
    verdict = score_result.get("verdict", "")

    # 仮説1: 財務健全性・スコア
    if total_score >= 75:
        hypotheses.append(InvestmentHypothesis(
            id=1,
            title="高水準のBuffett Scoreと財務指標による投資適格性",
            rationale="財務スコアが75点以上で、バフェット基準を高水準でクリアしている。",
            evidence=[
                f"Buffett Score: {total_score}/100",
                f"判定: {verdict}",
                f"ROE: {data.get('roe')}",
                f"営業利益率: {data.get('operating_margin')}",
            ],
            verification_items=[
                "次期決算でROEが基準（15%以上）を維持するか",
                "営業利益率の低下傾向がないか（四半期トレンド）",
                "FCFが継続的にプラスであるか",
            ],
            status=HypothesisStatus.UNVERIFIED,
            source="ai",
        ))
    elif total_score >= 55:
        hypotheses.append(InvestmentHypothesis(
            id=1,
            title="条件付き投資適格性（追加調査必要）",
            rationale="財務スコアは55点以上だが、一部基準未達のため条件付き。",
            evidence=[
                f"Buffett Score: {total_score}/100",
                f"判定: {verdict}",
            ],
            verification_items=[
                "未達項目の改善計画・進捗の確認",
                "業界特有の理由で低い指標が正当化されるか",
                "次期決算でのスコア回復可能性",
            ],
            status=HypothesisStatus.PENDING,
            source="ai",
        ))
    else:
        hypotheses.append(InvestmentHypothesis(
            id=1,
            title="財務スコアによる投資非推奨",
            rationale="Buffett Scoreが55点未満で、バフェット基準を大きく下回っている。",
            evidence=[
                f"Buffett Score: {total_score}/100",
            ],
            verification_items=[
                "業界再編や事業転換で指標が改善する可能性",
                "一時的な要因（再投資期・景気後退）による低下か",
            ],
            status=HypothesisStatus.REJECTED,
            source="ai",
        ))

    # 仮説2: MOAT
    moat_rating = moat.get("rating", "none") if isinstance(moat, dict) else "none"
    if moat_rating == "wide":
        stars = moat.get('stars', 0) or 0
        hypotheses.append(InvestmentHypothesis(
            id=2,
            title="広い経済的堀（Wide MOAT）による長期競争優位性",
            rationale="MOAT評価がWideで、持続的な競争優位性が認められる。",
            evidence=[
                f"MOAT評価: Wide（{'★' * stars}{'☆' * (5 - stars)}）",
                moat.get("quantitative", {}).get("roe_evidence", ""),
                moat.get("quantitative", {}).get("margin_evidence", ""),
            ],
            verification_items=[
                "競合の新製品・サービスがMOATを脅かしていないか",
                "規制変更・技術変化で堀が無意味にならないか",
                "次期決算で高いROE・利益率が維持されるか",
            ],
            status=HypothesisStatus.UNVERIFIED,
            source="ai",
        ))
    elif moat_rating == "narrow":
        hypotheses.append(InvestmentHypothesis(
            id=2,
            title="狭い経済的堀（Narrow MOAT）に依存する投資",
            rationale="MOATはあるが狭く、競争環境の変化に注意が必要。",
            evidence=[
                f"MOAT評価: Narrow",
            ],
            verification_items=[
                "業界変化の速度（DX・規制緩和・新規参入）",
                "MOATの維持・拡大に向けた企業の投資動向",
            ],
            status=HypothesisStatus.PENDING,
            source="ai",
        ))

    # 仮説3: ブランド
    brand_stars = (brand.get("stars", 0) or 0) if isinstance(brand, dict) else 0
    if brand_stars >= 4:
        hypotheses.append(InvestmentHypothesis(
            id=3,
            title="強いブランド力による価格決定力と顧客ロックイン",
            rationale="ブランド力評価が高く、プレミアム価格とロイヤルティが期待できる。",
            evidence=[
                f"ブランドスコア: {'★' * brand_stars}{'☆' * (5 - brand_stars)}",
                f"ブランドタイプ: {brand.get('brand_type', '不明')}",
            ],
            verification_items=[
                "若年層のブランド認知度・ロイヤルティ調査",
                "値上げ後の需要動向（価格弾力性の実証）",
                "ブランド維持コスト（宣伝費）の変化",
            ],
            status=HypothesisStatus.UNVERIFIED,
            source="ai",
        ))

    # 仮説4: 経営者
    mgmt_stars = (mgmt.get("stars", 0) or 0) if isinstance(mgmt, dict) else 0
    if mgmt_stars >= 4:
        hypotheses.append(InvestmentHypothesis(
            id=4,
            title="優秀な経営者による資本効率と株主還元",
            rationale="経営者評価が高く、資本配分と財務運営に信頼性がある。",
            evidence=[
                f"経営者スコア: {'★' * mgmt_stars}{'☆' * (5 - mgmt_stars)}",
                mgmt.get("quantitative", {}).get("roe_evidence", ""),
                mgmt.get("quantitative", {}).get("fcf_evidence", ""),
            ],
            verification_items=[
                "次期の資本配分計画（配当・自社買い・再投資のバランス）",
                "経営者報酬と株主価値の連動性",
                "後継者計画の有無（創業者依存の場合）",
            ],
            status=HypothesisStatus.UNVERIFIED,
            source="ai",
        ))

    # 仮説5: バリュエーション（Red Team視点を踏まえた慎重仮説）
    pe = data.get("pe_ratio")
    pb = data.get("pb_ratio")
    if pe is not None and 0 < pe <= 15 and pb is not None and 0 < pb <= 1.5:
        hypotheses.append(InvestmentHypothesis(
            id=5,
            title="割安バリュエーションによる安全余裕（Margin of Safety）",
            rationale="PER・PBRが低く、ダウンサイドリスクが限定的。",
            evidence=[
                f"PER: {pe:.1f}倍",
                f"PBR: {pb:.1f}倍",
            ],
            verification_items=[
                "来期EPS予想の下方修正リスク",
                "業界平均PER・PBRとの相対比較",
                "決算発表後の株価変動と安全余裕の確認",
            ],
            status=HypothesisStatus.UNVERIFIED,
            source="ai",
        ))
    elif pe is not None and pe > 25:
        hypotheses.append(InvestmentHypothesis(
            id=5,
            title="高PERによる安全余裕不足（リスク要因）",
            rationale="PERが25倍以上で、成長期待が過大に織り込まれている可能性。",
            evidence=[
                f"PER: {pe:.1f}倍",
            ],
            verification_items=[
                "成長率がPERに見合う水準（PEGレシオ）か",
                "決算ミス時の株価下落幅のシミュレーション",
            ],
            status=HypothesisStatus.REJECTED,
            source="ai",
        ))

    # 連続採番を整える
    for idx, h in enumerate(hypotheses, start=1):
        h.id = idx

    return hypotheses
