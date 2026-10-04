"""
Script to locate Google OAuth client credentials and format the authorization URL.
"""
import json
import urllib.parse
from pathlib import Path

SEARCH_PATHS = [
    Path("/home/vokov/projects/b-sdd-legal/credentials.json"),
    Path("/home/vokov/projects/b-sdd-legal/client_secret.json"),
    Path("/home/vokov/projects/send-to-kindle/credentials.json"),
    Path("/home/vokov/projects/send-to-kindle/client_secret.json"),
    Path("/home/vokov/.config/b-sdd-legal/credentials.json"),
    Path("/home/vokov/.config/b-sdd-legal/client_secret.json"),
    Path("/home/vokov/projects/b-sdd/credentials.json")
]

OUT_FILE = Path("/home/vokov/projects/b-sdd/docs/OAUTH_LINK.md")

def run():
    client_id = None
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    found_file = None
    
    for p in SEARCH_PATHS:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    app_data = data.get("installed") or data.get("web") or {}
                    cid = app_data.get("client_id")
                    if cid:
                        client_id = cid
                        auth_uri = app_data.get("auth_uri", auth_uri)
                        found_file = str(p)
                        break
            except Exception:
                pass
                
    if not client_id:
        # Check token.json for client_id if available
        for p in [Path("/home/vokov/projects/b-sdd-legal/token.json"), Path("/home/vokov/projects/send-to-kindle/token.json")]:
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cid = data.get("client_id")
                        if cid:
                            client_id = cid
                            found_file = str(p)
                            break
                except Exception:
                    pass

    if client_id:
        params = {
            "client_id": client_id,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "scope": "https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.compose",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        oauth_url = f"{auth_uri}?{urllib.parse.urlencode(params)}"
        content = f"# Google OAuth 2.0 Authorization Link\n\nFound credentials in: `{found_file}`\n\n[Click here to Authorize Gmail Send]({oauth_url})\n\nDirect URL:\n```\n{oauth_url}\n```\n"
    else:
        content = "# Google OAuth Credentials Missing\n\nCould not find `credentials.json` in scanned paths.\n"

    OUT_FILE.write_text(content, encoding="utf-8")
    print("WROTE_OAUTH_LINK")

if __name__ == "__main__":
    run()
