"""Upload remaining documentation sources to NotebookLM."""
import urllib.request
import json
from pathlib import Path

MCP_URL = 'http://192.168.3.184:8002/mcp'
NOTEBOOK_ID = '205ee2ec-e0d2-4ba6-badf-44f2de02c7e2'
ROOT_DIR = Path('/home/vokov/projects/b-sdd')

def get_mcp_session():
    init_req = urllib.request.Request(
        MCP_URL,
        headers={'Accept': 'application/json, text/event-stream', 'Content-Type': 'application/json'},
        data=json.dumps({
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'b-sdd-uploader', 'version': '1.0'}
            }
        }).encode('utf-8')
    )
    with urllib.request.urlopen(init_req) as resp:
        session_id = resp.headers.get('mcp-session-id')
        resp.read()
    
    # send initialized notification
    notif_req = urllib.request.Request(
        MCP_URL,
        headers={'Accept': 'application/json, text/event-stream', 'Content-Type': 'application/json', 'mcp-session-id': session_id},
        data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        }).encode('utf-8')
    )
    with urllib.request.urlopen(notif_req) as resp:
        resp.read()
    
    return session_id

def upload_source(session_id, req_id, title, content):
    call_req = urllib.request.Request(
        MCP_URL,
        headers={'Accept': 'application/json, text/event-stream', 'Content-Type': 'application/json', 'mcp-session-id': session_id},
        data=json.dumps({
            'jsonrpc': '2.0',
            'id': req_id,
            'method': 'tools/call',
            'params': {
                'name': 'sources_add_text',
                'arguments': {
                    'notebook_id': NOTEBOOK_ID,
                    'title': title,
                    'content': content
                }
            }
        }).encode('utf-8')
    )
    with urllib.request.urlopen(call_req) as resp:
        raw_res = resp.read().decode('utf-8')
        print(f"Uploaded '{title}' -> response:\n{raw_res}")
        return raw_res

def list_sources(session_id, req_id):
    call_req = urllib.request.Request(
        MCP_URL,
        headers={'Accept': 'application/json, text/event-stream', 'Content-Type': 'application/json', 'mcp-session-id': session_id},
        data=json.dumps({
            'jsonrpc': '2.0',
            'id': req_id,
            'method': 'tools/call',
            'params': {
                'name': 'sources_list',
                'arguments': {'notebook_id': NOTEBOOK_ID}
            }
        }).encode('utf-8')
    )
    with urllib.request.urlopen(call_req) as resp:
        raw_res = resp.read().decode('utf-8')
        for line in raw_res.splitlines():
            if line.startswith('data: '):
                payload = json.loads(line[6:])
                content_text = payload.get('result', {}).get('content', [{}])[0].get('text', '[]')
                sources = json.loads(content_text)
                return sources
        return []

def main():
    session_id = get_mcp_session()
    print("Obtained session:", session_id)

    # 1. Upload Doc 1
    doc1_path = ROOT_DIR / 'docs' / 'notebooklm_sources' / '01_ADR_001_TO_012_CANONICAL_REGISTRY.md'
    doc1_content = doc1_path.read_text(encoding='utf-8')
    print(f"Uploading Doc 1 ({len(doc1_content)} chars)...")
    upload_source(session_id, 10, 'B-SDD Canonical Architecture Registry (ADR-001 to ADR-012)', doc1_content)

    # 2. Upload Doc 2
    doc2_path = ROOT_DIR / 'docs' / 'notebooklm_sources' / '02_ADR_FE_001_ASTRYX_AND_HANDOFF_DIRECTIVES.md'
    doc2_content = doc2_path.read_text(encoding='utf-8')
    print(f"Uploading Doc 2 ({len(doc2_content)} chars)...")
    upload_source(session_id, 11, 'ADR-FE-001, Astryx Directives & Backend Handoff Contract', doc2_content)

    # 3. Final listing
    print("\n--- FINAL NOTEBOOK SOURCES ---")
    sources = list_sources(session_id, 12)
    for idx, s in enumerate(sources, 1):
        print(f"{idx}. [{s.get('id')}] {s.get('title')}")

if __name__ == '__main__':
    main()
