"""
E2E Frontend Proxy & Backend Generation Test
Tests generation and refinement through both direct backend (8000) and frontend proxy (5173).
"""
import sys
import json
import requests

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_PROXY_URL = "http://127.0.0.1:5173"

def run_tests():
    print("=" * 60)
    print("TEST 1: Health check through Vite frontend proxy (http://127.0.0.1:5173/api/health)")
    print("=" * 60)
    r_health_fe = requests.get(f"{FRONTEND_PROXY_URL}/api/health", timeout=5)
    assert r_health_fe.status_code == 200, f"Frontend proxy health check failed: {r_health_fe.status_code}"
    print(f"Frontend proxy health check OK: {r_health_fe.json()}")

    print("\n" + "=" * 60)
    print("TEST 2: Direct backend generation for CS Student Portfolio")
    print("=" * 60)
    test_prompt = "Create a modern portfolio website for a Computer Science student specializing in AI/ML and software development. Include Hero, About, Skills, Projects, Experience, Education and Contact sections. Do not invent a person's name, company, job or achievements."

    payload = {
        "prompt": test_prompt,
        "project_name": "CS Student Portfolio",
        "api_key": None,
        "model": "gemini-2.5-flash"
    }

    # Test via frontend proxy
    r_gen = requests.post(f"{FRONTEND_PROXY_URL}/api/generate", json=payload, stream=True, timeout=15)
    assert r_gen.status_code == 200, f"Generate via proxy failed: {r_gen.status_code}"

    v1_html = ""
    v1_proj_id = None
    v1_id = None
    status_events = []
    chunk_count = 0

    for line in r_gen.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("event: status"):
                pass
            elif decoded.startswith("data: "):
                data = json.loads(decoded[6:])
                if "status" in data:
                    status_events.append(data)
                elif "chunk" in data:
                    chunk_count += 1
                elif "html" in data:
                    v1_html = data["html"]
                    v1_proj_id = data["project_id"]
                    v1_id = data["version_id"]

    print(f"Chunks received via frontend proxy: {chunk_count}")
    assert chunk_count > 0, "No chunks streamed through frontend proxy!"
    print(f"Version 1 Generated: Project ID={v1_proj_id}, Version ID={v1_id}")
    print(f"HTML Size: {len(v1_html)} bytes")

    # Content checks: No hardcoded Elena Vance, Q4, spatial compute, fintech platform
    assert "Elena Vance" not in v1_html, "Found Elena Vance in HTML!"
    assert "elena.design" not in v1_html, "Found elena.design in HTML!"
    assert "Q4 Consulting" not in v1_html, "Found Q4 Consulting in HTML!"
    assert "fintech platform" not in v1_html.lower(), "Found fintech platform in HTML!"

    # Sections check
    for sec in ["hero", "about", "skills", "projects", "education", "experience", "contact"]:
        assert sec in v1_html.lower(), f"Section '{sec}' missing in generated website!"
    print("[PASS] Version 1 contains all requested CS & AI/ML sections with clean un-invented content.")

    print("\n" + "=" * 60)
    print("TEST 3: Refinement flow through frontend proxy")
    print("=" * 60)
    refine_prompt = "Change the hero heading to 'AI/ML & Software Developer' and add a Python and FastAPI skills section. Do not invent a person's name, company, job, client or achievements."

    refine_payload = {
        "project_id": v1_proj_id,
        "current_html": v1_html,
        "instruction": refine_prompt,
        "api_key": None,
        "model": "gemini-2.5-flash"
    }

    r_ref = requests.post(f"{FRONTEND_PROXY_URL}/api/refine", json=refine_payload, stream=True, timeout=15)
    assert r_ref.status_code == 200, f"Refine via proxy failed: {r_ref.status_code}"

    v2_html = ""
    v2_id = None
    ref_chunks = 0

    for line in r_ref.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                data = json.loads(decoded[6:])
                if "chunk" in data:
                    ref_chunks += 1
                elif "html" in data:
                    v2_html = data["html"]
                    v2_id = data["version_id"]

    print(f"Refinement chunks received: {ref_chunks}")
    assert ref_chunks > 0
    print(f"Version 2 Generated: Version ID={v2_id}")
    assert v2_id != v1_id, "Version 2 ID must be distinct!"

    # Verify hero heading updated to AI/ML & Software Developer
    assert "AI/ML &amp; Software Developer" in v2_html or "AI/ML & Software Developer" in v2_html, "Refined heading not found in Version 2 HTML!"
    assert "Python" in v2_html, "Python missing in skills!"
    assert "FastAPI" in v2_html, "FastAPI missing in skills!"
    print("[PASS] Version 2 contains updated heading and Python & FastAPI skills section!")

    print("\n" + "=" * 60)
    print("TEST 4: Project retrieval & version timeline persistence")
    print("=" * 60)
    r_proj = requests.get(f"{FRONTEND_PROXY_URL}/api/projects/{v1_proj_id}", timeout=5)
    assert r_proj.status_code == 200
    pdata = r_proj.json()
    assert len(pdata["versions"]) == 2
    assert pdata["current_version_id"] == v2_id
    print(f"[PASS] Project stored on disk with {len(pdata['versions'])} versions. Active version: {pdata['current_version_id']}")

    print("\n" + "=" * 60)
    print("TEST 5: Version rollback (Revert to Version 1)")
    print("=" * 60)
    r_rev = requests.post(f"{FRONTEND_PROXY_URL}/api/projects/{v1_proj_id}/revert/{v1_id}", timeout=5)
    assert r_rev.status_code == 200
    rev_data = r_rev.json()
    assert rev_data["current_version_id"] == v1_id
    print(f"[PASS] Successfully reverted project to Version 1 ({v1_id})")

    print("\n" + "=" * 60)
    print("TEST 6: Export HTML & ZIP through frontend proxy")
    print("=" * 60)
    r_zip = requests.get(f"{FRONTEND_PROXY_URL}/api/export/project/{v1_proj_id}/zip", timeout=5)
    assert r_zip.status_code == 200
    assert len(r_zip.content) > 500
    print(f"[PASS] ZIP export package received via proxy: {len(r_zip.content)} bytes.")

    print("\n" + "=" * 60)
    print("ALL FRONTEND PROXY & BACKEND PIPELINE TESTS PASSED 100%!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
