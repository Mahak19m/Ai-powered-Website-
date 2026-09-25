"""
Targeted Verification Script for User's Exact Scenario
Tests the generation for CS student in AI/ML & Software Development and the subsequent refinement.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def parse_sse_events(response):
    events = []
    current_event = {}
    for line in response.iter_lines():
        if not line:
            if current_event:
                events.append(current_event)
                current_event = {}
            continue
        if line.startswith("event: "):
            current_event["event"] = line[7:].strip()
        elif line.startswith("data: "):
            data_str = line[6:].strip()
            try:
                current_event["data"] = json.loads(data_str)
            except Exception:
                current_event["data"] = data_str
    if current_event:
        events.append(current_event)
    return events

def run_test():
    print("=" * 60)
    print("STEP 1: Generating CS Student AI/ML & Software Dev Portfolio")
    print("=" * 60)

    prompt_1 = "Create a modern portfolio website for a Computer Science student specializing in AI/ML and software development. Include Hero, About, Skills, Projects, Education, Experience and Contact sections."
    
    gen_payload = {
        "prompt": prompt_1,
        "project_name": "CS Student Portfolio",
        "api_key": None,
        "model": "gemini-2.5-flash"
    }

    r1 = client.post("/api/generate", json=gen_payload)
    assert r1.status_code == 200

    events_1 = parse_sse_events(r1)
    complete_1 = next(e["data"] for e in events_1 if e.get("event") == "complete")
    v1_html = complete_1["html"]
    v1_proj_id = complete_1["project_id"]
    v1_id = complete_1["version_id"]

    print(f"Version 1 Created -> Project ID: {v1_proj_id}, Version ID: {v1_id}")
    print(f"Version 1 HTML length: {len(v1_html)}")

    # Verify that Elena Vance / spatial compute / fintech platform are NOT in Version 1
    assert "Elena Vance" not in v1_html, "Error: 'Elena Vance' found in generated website!"
    assert "elena.design" not in v1_html, "Error: 'elena.design' found in generated website!"
    assert "Q4 Consulting & Advisory" not in v1_html, "Error: 'Q4 Consulting & Advisory' found in generated website!"
    assert "fintech platform" not in v1_html.lower(), "Error: 'fintech platform' found in generated website!"

    # Verify that requested sections exist in Version 1
    assert "about" in v1_html.lower(), "About section missing!"
    assert "skills" in v1_html.lower(), "Skills section missing!"
    assert "projects" in v1_html.lower(), "Projects section missing!"
    assert "education" in v1_html.lower(), "Education section missing!"
    assert "experience" in v1_html.lower(), "Experience section missing!"
    assert "contact" in v1_html.lower(), "Contact section missing!"
    print("[PASS] Version 1 verified: contains all requested sections with ZERO hardcoded Elena Vance/Q4 template content.")

    print("\n" + "=" * 60)
    print("STEP 2: Submitting Refinement Prompt")
    print("=" * 60)

    prompt_2 = "Change the hero heading to 'AI/ML & Software Developer' and add a Python and FastAPI skills section. Do not invent a person's name, company, job, client or achievements."

    refine_payload = {
        "project_id": v1_proj_id,
        "current_html": v1_html,
        "instruction": prompt_2,
        "api_key": None,
        "model": "gemini-2.5-flash"
    }

    r2 = client.post("/api/refine", json=refine_payload)
    assert r2.status_code == 200

    events_2 = parse_sse_events(r2)
    complete_2 = next(e["data"] for e in events_2 if e.get("event") == "complete")
    v2_html = complete_2["html"]
    v2_id = complete_2["version_id"]

    print(f"Version 2 Created -> Version ID: {v2_id}")
    print(f"Version 2 HTML length: {len(v2_html)}")

    # Verify Version 2 has new version id
    assert v2_id != v1_id, "Version 2 ID must be different from Version 1 ID"

    # Verify Version 2 has the refined heading
    assert "AI/ML &amp; Software Developer" in v2_html or "AI/ML & Software Developer" in v2_html, "Refined heading 'AI/ML & Software Developer' missing in Version 2!"

    # Verify Version 2 contains Python and FastAPI
    assert "Python" in v2_html, "Python missing in Version 2 skills"
    assert "FastAPI" in v2_html, "FastAPI missing in Version 2 skills"

    # Verify Version 2 is stored on disk
    r_proj = client.get(f"/api/projects/{v1_proj_id}")
    assert r_proj.status_code == 200
    proj_data = r_proj.json()
    assert len(proj_data["versions"]) == 2
    assert proj_data["current_version_id"] == v2_id
    print("[PASS] Version 2 successfully stored and linked in project history!")

    print("\n" + "=" * 60)
    print("STEP 3: Testing Revert / Rollback to Version 1")
    print("=" * 60)
    r_revert = client.post(f"/api/projects/{v1_proj_id}/revert/{v1_id}")
    assert r_revert.status_code == 200
    revert_data = r_revert.json()
    assert revert_data["current_version_id"] == v1_id
    print(f"[PASS] Revert to Version 1 verified! Current active version is now {v1_id}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
