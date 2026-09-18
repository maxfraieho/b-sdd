"""
Sovereign Autonomous Multi-Agent Consensus & Quorum Arbitration.
Compliant with B-SDD Methodology v1.2, ADR-002 (Pure Python Stdlib), ADR-007, ADR-013, ADR-014.

Implements decentralized quorum voting, ballot tracking, and bitemporal transaction
anchoring for multi-agent architectural mutation proposals across sovereign nodes.
"""
import math
import time
import uuid
import hashlib
import threading
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


class ConsensusProposal:
    """Represents an active or resolved architectural consensus proposal."""

    def __init__(
        self,
        proposal_id: str,
        title: str,
        target_adr: str,
        description: str,
        proposer_id: str,
        created_at: float,
        expires_at: float,
        t_x: str,
        t_v: Dict[str, str],
        status: str = "voting"
    ):
        self.proposal_id = proposal_id
        self.title = title
        self.target_adr = target_adr
        self.description = description
        self.proposer_id = proposer_id
        self.created_at = created_at
        self.expires_at = expires_at
        self.t_x = t_x
        self.t_v = t_v
        self.status = status
        self.votes: Dict[str, Dict[str, Any]] = {}

    def to_dict(self) -> Dict[str, Any]:
        approvals = sum(1 for v in self.votes.values() if v.get("vote") == "approve")
        rejections = sum(1 for v in self.votes.values() if v.get("vote") == "reject")
        abstentions = sum(1 for v in self.votes.values() if v.get("vote") == "abstain")
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "target_adr": self.target_adr,
            "description": self.description,
            "proposer_id": self.proposer_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "t_x": self.t_x,
            "t_v": self.t_v,
            "status": self.status,
            "approvals": approvals,
            "rejections": rejections,
            "abstentions": abstentions,
            "total_votes_cast": len(self.votes),
            "votes": self.votes
        }


class ConsensusEngine:
    """
    Thread-safe decentralized multi-agent quorum and ballot manager.
    Arbitrates architectural consensus with 2/3 majority requirement under ADR-013.
    """

    def __init__(self, total_voters: int = 3, quorum_ratio: float = 2.0 / 3.0):
        self._lock = threading.Lock()
        self.total_voters = max(1, total_voters)
        self.quorum_ratio = quorum_ratio
        self._proposals: Dict[str, ConsensusProposal] = {}

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def propose(
        self,
        title: str,
        target_adr: str = "ADR-GLOBAL",
        description: str = "",
        proposer_id: str = "agent-primary",
        voting_period_sec: int = 60
    ) -> Dict[str, Any]:
        """Submits a new consensus proposal with bitemporal transaction coordinates."""
        with self._lock:
            now = time.time()
            t_x = self._now_iso()
            expires_at = now + voting_period_sec
            t_v = {
                "valid_from": t_x,
                "valid_to": datetime.fromtimestamp(expires_at, timezone.utc).isoformat()
            }
            p_id = f"prop_{int(now)}_{uuid.uuid4().hex[:6]}"

            prop = ConsensusProposal(
                proposal_id=p_id,
                title=title,
                target_adr=target_adr,
                description=description,
                proposer_id=proposer_id,
                created_at=now,
                expires_at=expires_at,
                t_x=t_x,
                t_v=t_v,
                status="voting"
            )
            self._proposals[p_id] = prop
            return prop.to_dict()

    def cast_vote(
        self,
        proposal_id: str,
        voter_id: str,
        vote: str = "approve"
    ) -> Dict[str, Any]:
        """
        Casts a vote ('approve', 'reject', 'abstain') on an active proposal.
        Triggers quorum resolution when threshold N >= 2/3 is reached.
        """
        with self._lock:
            prop = self._proposals.get(proposal_id)
            if not prop:
                return {"accepted": False, "error": f"Proposal '{proposal_id}' not found"}

            now = time.time()
            if prop.status != "voting":
                return {
                    "accepted": False,
                    "error": f"Proposal is already {prop.status}",
                    "status": prop.status
                }

            if now > prop.expires_at:
                prop.status = "expired"
                return {
                    "accepted": False,
                    "error": "Voting period has expired",
                    "status": "expired"
                }

            if voter_id in prop.votes:
                return {
                    "accepted": False,
                    "error": f"Voter '{voter_id}' has already voted",
                    "status": prop.status
                }

            prop.votes[voter_id] = {
                "vote": vote,
                "timestamp": now,
                "t_x": self._now_iso()
            }

            required_approvals = math.ceil(self.total_voters * self.quorum_ratio)
            approvals = sum(1 for v in prop.votes.values() if v.get("vote") == "approve")
            rejections = sum(1 for v in prop.votes.values() if v.get("vote") == "reject")

            quorum_reached = False
            if approvals >= required_approvals:
                prop.status = "accepted"
                quorum_reached = True
            elif rejections > (self.total_voters - required_approvals):
                prop.status = "rejected"
                quorum_reached = True

            res = prop.to_dict()
            res["accepted"] = True
            res["quorum_reached"] = quorum_reached
            return res

    def get_proposals(self) -> List[Dict[str, Any]]:
        """Returns all proposals with active voting tally."""
        with self._lock:
            now = time.time()
            res = []
            for p in self._proposals.values():
                if p.status == "voting" and now > p.expires_at:
                    p.status = "expired"
                res.append(p.to_dict())
            return sorted(res, key=lambda x: x["created_at"], reverse=True)
