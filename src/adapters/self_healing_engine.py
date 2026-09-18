"""
Sovereign Agent Self-Correction & Automated Rollback Compensation Engine
Standard: B-SDD Methodology v1.2 (ADR-001, ADR-002, ADR-005, ADR-010, ADR-013)

Invariants:
- 100% Pure Python 3 Standard Library (ADR-002). Zero external pip dependencies.
- Bitemporal transaction coordinates:
  - Tx: system transaction recording time (ISO-8601 UTC)
  - Tv: valid time range (valid_from, valid_to)
- Thread-safe checkpoint registry and compensation audit log.
- AST parsing diagnostics with actionable repair heuristics.
"""

import ast
import hashlib
import json
import os
import re
import threading
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class ASTCheckpoint:
    checkpoint_id: str
    file_path: str
    content: str
    content_hash: str
    author: str
    reason: str
    t_x: str
    t_v: Dict[str, str]
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CompensationEvent:
    event_id: str
    checkpoint_id: str
    file_path: str
    reason: str
    reverted_bytes: int
    t_x: str
    t_v: Dict[str, str]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SelfHealingEngine:
    """
    Engine for creating transactional checkpoints of code artifacts,
    analyzing AST syntax failures, and performing automated rollback compensation.
    """

    def __init__(self, max_checkpoints: int = 100):
        self.max_checkpoints = max_checkpoints
        self._lock = threading.RLock()
        self._checkpoints: Dict[str, ASTCheckpoint] = {}
        self._checkpoint_order: List[str] = []
        self._audit_trail: List[CompensationEvent] = []

    def calculate_hash(self, text: str) -> str:
        """Returns SHA-256 hash of text content."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def create_checkpoint(
        self,
        file_path: str,
        content: str,
        author: str = "autonomous-agent",
        reason: str = "Pre-mutation checkpoint"
    ) -> ASTCheckpoint:
        """
        Creates and stores an atomic AST checkpoint with bitemporal coordinates.
        """
        now_ts = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()
        chk_id = f"chk_{int(now_ts)}_{hashlib.sha256(f'{file_path}:{now_ts}'.encode()).hexdigest()[:6]}"
        
        c_hash = self.calculate_hash(content)
        t_v = {
            "valid_from": now_iso,
            "valid_to": "9999-12-31T23:59:59Z"
        }

        checkpoint = ASTCheckpoint(
            checkpoint_id=chk_id,
            file_path=file_path,
            content=content,
            content_hash=c_hash,
            author=author,
            reason=reason,
            t_x=now_iso,
            t_v=t_v,
            created_at=now_ts
        )

        with self._lock:
            self._checkpoints[chk_id] = checkpoint
            self._checkpoint_order.append(chk_id)
            if len(self._checkpoint_order) > self.max_checkpoints:
                oldest_id = self._checkpoint_order.pop(0)
                self._checkpoints.pop(oldest_id, None)

        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Optional[ASTCheckpoint]:
        """Retrieves checkpoint by ID."""
        with self._lock:
            return self._checkpoints.get(checkpoint_id)

    def get_latest_checkpoint_for_file(self, file_path: str) -> Optional[ASTCheckpoint]:
        """Retrieves the newest checkpoint recorded for a given file path."""
        with self._lock:
            for chk_id in reversed(self._checkpoint_order):
                cp = self._checkpoints[chk_id]
                if cp.file_path == file_path:
                    return cp
        return None

    def analyze_ast(self, source_code: str) -> Dict[str, Any]:
        """
        Analyzes Python source code using pure stdlib ast parser.
        If a SyntaxError occurs, generates actionable repair hints.
        """
        try:
            tree = ast.parse(source_code)
            return {
                "is_valid": True,
                "error_type": None,
                "error_message": None,
                "line": None,
                "column": None,
                "healing_hints": []
            }
        except SyntaxError as exc:
            hints: List[str] = []
            msg = exc.msg or "SyntaxError"
            lineno = exc.lineno or 1
            colno = exc.offset or 0

            # Generate heuristic repair suggestions based on common error patterns
            if "unexpected EOF" in msg.lower() or "expected an indented block" in msg.lower():
                hints.append("Check for unclosed parenthesis, brackets, quotes, or empty indented blocks (e.g. add 'pass').")
            elif "invalid syntax" in msg.lower():
                hints.append("Check previous tokens on or near line " + str(lineno) + " for missing colons, commas, or unclosed string literals.")
            elif "was never closed" in msg.lower():
                hints.append("Unclosed delimiter detected. Verify matching brackets: (), [], or {}.")
            else:
                hints.append(f"Syntactic anomaly near line {lineno}, col {colno}: verify grammatical correctness.")

            return {
                "is_valid": False,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "line": lineno,
                "column": colno,
                "healing_hints": hints
            }
        except Exception as exc:
            return {
                "is_valid": False,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "line": None,
                "column": None,
                "healing_hints": ["Unexpected parsing failure: inspect source encoding and structure."]
            }

    def compensate_rollback(
        self,
        checkpoint_id: str,
        target_path: Optional[str] = None,
        reason: str = "Automated rollback compensation"
    ) -> Dict[str, Any]:
        """
        Reverts target file content to the checkpoint snapshot and logs compensation event.
        """
        with self._lock:
            cp = self._checkpoints.get(checkpoint_id)
            if not cp:
                return {
                    "success": False,
                    "error": f"Checkpoint '{checkpoint_id}' not found",
                    "checkpoint_id": checkpoint_id
                }

            dest_path = target_path or cp.file_path
            reverted_bytes = len(cp.content.encode("utf-8"))

            try:
                # If path exists or is a valid file system path, write the original content back
                if dest_path:
                    p = Path(dest_path)
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(cp.content, encoding="utf-8")
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to restore file {dest_path}: {e}",
                    "checkpoint_id": checkpoint_id
                }

            now_ts = time.time()
            now_iso = datetime.now(timezone.utc).isoformat()
            event_id = f"comp_{int(now_ts)}_{hashlib.sha256(f'{checkpoint_id}:{now_ts}'.encode()).hexdigest()[:6]}"
            
            event = CompensationEvent(
                event_id=event_id,
                checkpoint_id=checkpoint_id,
                file_path=dest_path,
                reason=reason,
                reverted_bytes=reverted_bytes,
                t_x=now_iso,
                t_v={"valid_from": now_iso, "valid_to": "9999-12-31T23:59:59Z"},
                timestamp=now_ts
            )
            self._audit_trail.append(event)

            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "event_id": event_id,
                "file_path": dest_path,
                "reverted_bytes": reverted_bytes,
                "reason": reason,
                "timestamp": now_iso
            }

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Returns list of compensation events."""
        with self._lock:
            return [e.to_dict() for e in self._audit_trail]

    def get_status(self) -> Dict[str, Any]:
        """Returns status summary of self-healing engine."""
        with self._lock:
            return {
                "status": "ok",
                "total_checkpoints": len(self._checkpoints),
                "total_compensations": len(self._audit_trail),
                "recent_checkpoints": [
                    {
                        "checkpoint_id": cp.checkpoint_id,
                        "file_path": cp.file_path,
                        "author": cp.author,
                        "created_at": cp.created_at,
                        "t_x": cp.t_x
                    }
                    for cp in list(self._checkpoints.values())[-10:]
                ],
                "recent_compensations": [e.to_dict() for e in self._audit_trail[-10:]]
            }
