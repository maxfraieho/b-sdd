"""
Sovereign Realtime Agent Collaboration & Distributed Multi-Host Synchronization.
Compliant with B-SDD Methodology v1.2, ADR-002 (Pure Python Stdlib), ADR-007, ADR-013.

Coordinates distributed lock leases, heartbeat broadcasting, and peer discovery
across sovereign cluster nodes (192.168.3.161, 192.168.3.184, 192.168.3.251).
"""
import time
import uuid
import socket
import threading
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

SOVEREIGN_NODES = [
    {
        "id": "node-dev-161",
        "name": "AGY Dev Station",
        "host": "192.168.3.161",
        "role": "primary_operator",
        "port": 8765
    },
    {
        "id": "node-runner-184",
        "name": "Sovereign Runner & Gateway",
        "host": "192.168.3.184",
        "role": "production_gateway",
        "port": 8765
    },
    {
        "id": "node-utopia-251",
        "name": "Utopia DB Bitemporal Ledger",
        "host": "192.168.3.251",
        "role": "bitemporal_ledger",
        "port": 9922
    }
]


class ClusterNodeRegistry:
    """Discovers and maintains availability status of sovereign cluster nodes."""

    def __init__(self, nodes: Optional[List[Dict[str, Any]]] = None):
        self.nodes = nodes or list(SOVEREIGN_NODES)

    def check_node_reachable(self, host: str, port: int, timeout_sec: float = 0.2) -> bool:
        """Quick TCP probe to verify node availability without blocking."""
        try:
            with socket.create_connection((host, port), timeout=timeout_sec):
                return True
        except (socket.timeout, OSError):
            return False

    def get_nodes(self, probe: bool = False) -> List[Dict[str, Any]]:
        """Returns registered cluster nodes with optional live reachability probe."""
        result = []
        for n in self.nodes:
            item = dict(n)
            if probe:
                item["reachable"] = self.check_node_reachable(n["host"], n["port"])
                item["status"] = "online" if item["reachable"] else "unreachable"
            else:
                item["status"] = "registered"
            result.append(item)
        return result


class ClusterLeaseManager:
    """
    Thread-safe distributed lease and workspace reservation manager.
    Enforces ADR-013 bitemporal transaction coordinates (T_x, T_v) and optimistic concurrency.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._leases: Dict[str, Dict[str, Any]] = {}

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def acquire_lease(
        self,
        resource_id: str,
        holder_id: str,
        holder_host: str = "127.0.0.1",
        ttl_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Acquires or renews a lease on a given resource with bitemporal transaction coordinates.
        If held by another active holder, acquisition is rejected with conflict details.
        """
        with self._lock:
            now = time.time()
            existing = self._leases.get(resource_id)

            # Check if existing lease has expired
            if existing and existing.get("expires_at", 0) <= now:
                existing = None
                del self._leases[resource_id]

            # Conflict check: active and held by a different agent
            if existing and existing.get("holder_id") != holder_id:
                return {
                    "acquired": False,
                    "conflict_with": existing["holder_id"],
                    "holder_host": existing.get("holder_host"),
                    "expires_at": existing.get("expires_at"),
                    "ttl_remaining": round(existing.get("expires_at", now) - now, 2),
                    "resource_id": resource_id
                }

            renewed = existing is not None and existing.get("holder_id") == holder_id
            tx_id = f"tx_lease_{int(now)}_{uuid.uuid4().hex[:6]}"
            t_x = self._now_iso()
            expires_at = now + ttl_seconds
            t_v = {
                "valid_from": t_x,
                "valid_to": datetime.fromtimestamp(expires_at, timezone.utc).isoformat()
            }

            lease_record = {
                "tx_id": tx_id,
                "resource_id": resource_id,
                "holder_id": holder_id,
                "holder_host": holder_host,
                "t_x": t_x,
                "t_v": t_v,
                "acquired_at": now,
                "expires_at": expires_at,
                "ttl_seconds": ttl_seconds,
                "status": "active"
            }
            self._leases[resource_id] = lease_record

            return {
                "acquired": True,
                "renewed": renewed,
                "tx_id": tx_id,
                "resource_id": resource_id,
                "holder_id": holder_id,
                "holder_host": holder_host,
                "t_x": t_x,
                "t_v": t_v,
                "expires_at": expires_at,
                "ttl_seconds": ttl_seconds
            }

    def release_lease(self, resource_id: str, holder_id: str) -> Dict[str, Any]:
        """Releases an active lease if caller is the designated holder."""
        with self._lock:
            existing = self._leases.get(resource_id)
            if not existing:
                return {"released": True, "resource_id": resource_id, "message": "Lease was not held"}

            if existing.get("holder_id") != holder_id:
                return {
                    "released": False,
                    "error": "Holder mismatch: cannot release lease held by another agent",
                    "holder_id": existing.get("holder_id")
                }

            del self._leases[resource_id]
            return {"released": True, "resource_id": resource_id}

    def get_active_leases(self) -> List[Dict[str, Any]]:
        """Prunes expired leases and returns a snapshot of active leases."""
        with self._lock:
            now = time.time()
            active = []
            to_remove = []
            for res_id, lease in self._leases.items():
                if lease.get("expires_at", 0) > now:
                    active.append(dict(lease))
                else:
                    to_remove.append(res_id)
            for res_id in to_remove:
                del self._leases[res_id]
            return active
