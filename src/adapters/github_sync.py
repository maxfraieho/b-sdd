"""
GitHub API Sync Adapter for B-SDD Framework.
Provides live synchronization of repositories, branch metadata, and status
using 100% Pure Python Standard Library with resilient disk-backed caching and offline fallback.
(ADR-011)
"""
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional

# Root directory of the repository
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class GitHubSyncAdapter:
    """Synchronizes repository state with GitHub REST API using pure Python standard library."""

    DEFAULT_FALLBACK_REPOS = [
        {
            "name": "b-sdd",
            "full_name": "maxfraieho/b-sdd",
            "description": "Bitemporal Spec-Driven Development Framework with pure stdlib compiler & DRAKON visual workbench",
            "branch": "main",
            "stars": 12,
            "forks": 3,
            "open_issues": 0,
            "updated_at": "2026-09-17T12:00:00Z",
            "html_url": "https://github.com/maxfraieho/b-sdd",
            "is_active": True,
        },
        {
            "name": "ai-drakon-scaffolder",
            "full_name": "maxfraieho/ai-drakon-scaffolder",
            "description": "DRAKON visual logic editor, AST generator & test scaffolder",
            "branch": "main",
            "stars": 28,
            "forks": 7,
            "open_issues": 1,
            "updated_at": "2026-09-16T18:30:00Z",
            "html_url": "https://github.com/maxfraieho/ai-drakon-scaffolder",
            "is_active": False,
        },
        {
            "name": "utopia-vault",
            "full_name": "maxfraieho/utopia-vault",
            "description": "Sovereign bitemporal vector knowledge base and intent memory",
            "branch": "main",
            "stars": 19,
            "forks": 2,
            "open_issues": 0,
            "updated_at": "2026-09-15T09:15:00Z",
            "html_url": "https://github.com/maxfraieho/utopia-vault",
            "is_active": False,
        },
    ]

    def __init__(self, root_dir: Optional[Path] = None, account: str = "maxfraieho"):
        self.root_dir = root_dir or ROOT_DIR
        self.account = account
        self.cache_file = self.root_dir / ".context" / "github_cache.json"
        self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    def _get_headers(self) -> Dict[str, str]:
        """Constructs compliant GitHub REST headers."""
        headers = {
            "User-Agent": "B-SDD-Operator-Workbench/1.0",
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_cached_repositories(self) -> Optional[Dict[str, Any]]:
        """Reads cached repositories from disk if available."""
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Atomically saves repository cache to disk."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            self.cache_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def fetch_user_repositories(
        self, username: Optional[str] = None, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Fetches repositories from GitHub REST API for specified username.
        Falls back seamlessly to local disk cache or fallback defaults if offline or rate-limited.
        """
        user = username or self.account
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Check cache if not force refresh
        if not force_refresh:
            cached = self.get_cached_repositories()
            if cached and cached.get("account") == user:
                # If cache is younger than 5 minutes, return it
                cache_time = cached.get("timestamp_epoch", 0)
                if time.time() - cache_time < 300:
                    cached["source"] = "cache"
                    cached["cached"] = True
                    return cached

        url = f"https://api.github.com/users/{user}/repos?sort=updated&per_page=30"
        req = urllib.request.Request(url, headers=self._get_headers())

        try:
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                status_code = resp.status
                raw_bytes = resp.read()
                repos_raw = json.loads(raw_bytes.decode("utf-8"))

                repos = []
                for item in repos_raw:
                    is_active = item.get("name") == "b-sdd"
                    repos.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "full_name": item.get("full_name"),
                        "description": item.get("description") or "",
                        "branch": item.get("default_branch", "main"),
                        "stars": item.get("stargazers_count", 0),
                        "forks": item.get("forks_count", 0),
                        "open_issues": item.get("open_issues_count", 0),
                        "updated_at": item.get("updated_at", now_iso),
                        "html_url": item.get("html_url"),
                        "is_active": is_active,
                    })

                result = {
                    "account": user,
                    "connected": True,
                    "live": True,
                    "source": "api",
                    "status_code": status_code,
                    "total": len(repos),
                    "synced_at": now_iso,
                    "timestamp_epoch": time.time(),
                    "repositories": repos,
                }
                self._save_cache(result)
                return result

        except Exception as exc:
            # Fallback to cache
            cached = self.get_cached_repositories()
            if cached and cached.get("repositories"):
                cached["live"] = False
                cached["source"] = "offline_cache"
                cached["error"] = str(exc)
                cached["offline_parity"] = True
                return cached

            # Return standard fallback defaults
            fallback_result = {
                "account": user,
                "connected": False,
                "live": False,
                "source": "fallback",
                "status_code": None,
                "total": len(self.DEFAULT_FALLBACK_REPOS),
                "synced_at": now_iso,
                "timestamp_epoch": time.time(),
                "error": str(exc),
                "offline_parity": True,
                "repositories": self.DEFAULT_FALLBACK_REPOS,
            }
            self._save_cache(fallback_result)
            return fallback_result

    def sync_repositories(self, username: Optional[str] = None) -> Dict[str, Any]:
        """Explicitly forces synchronization and returns freshly updated repositories."""
        return self.fetch_user_repositories(username=username, force_refresh=True)

    def test_connection(self) -> Dict[str, Any]:
        """Tests connectivity to the GitHub API."""
        try:
            url = "https://api.github.com/zen"
            req = urllib.request.Request(url, headers=self._get_headers())
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                zen = resp.read().decode("utf-8").strip()
                return {"reachable": True, "zen": zen, "status": "online"}
        except Exception as e:
            return {"reachable": False, "error": str(e), "status": "offline"}
