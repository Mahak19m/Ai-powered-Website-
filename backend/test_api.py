"""
Automated smoke test for FastAPI backend endpoints.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("Testing backend connectivity...")
    # 1. Health
    r = client.get("/api/health")
    print(f"Health check: {r.status_code} -> {r.json()}")
    assert r.status_code == 200

    # 2. Generate with SSE
    print("\nTesting SSE website generation...")
    gen_payload = {
        "prompt": "Modern AI Agent Swarm Platform",
        "project_name": "Test Project Nexus"
    }
    r = client.post("/api/generate", json=gen_payload)
    assert r.status_code == 200

    received_chunks = 0
    project_id = None
    for line in r.iter_lines():
        if line:
            if line.startswith("data: "):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    if "chunk" in data:
                        received_chunks += 1
                    if "project_id" in data:
                        project_id = data["project_id"]
                        print(f"Complete event received! Project ID: {project_id}, Version: {data.get('version_id')}")
                except Exception:
                    pass

    print(f"Total chunks received: {received_chunks}")
    assert received_chunks > 0
    assert project_id is not None

    # 3. List projects
    print("\nTesting list projects...")
    r = client.get("/api/projects")
    assert r.status_code == 200
    projects = r.json()
    print(f"Found {len(projects)} projects: {[p['name'] for p in projects]}")

    # 4. Test ZIP export
    print(f"\nTesting ZIP export for project {project_id}...")
    r = client.get(f"/api/export/project/{project_id}/zip")
    assert r.status_code == 200
    assert len(r.content) > 500
    print(f"ZIP export successful! Byte size: {len(r.content)}")

    print("\nAll backend smoke tests PASSED successfully!")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
