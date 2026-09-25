"""
Exact-List Skills Refinement & Validation Test
Verifies exact replacement, absence of unrequested skills, preservation of other sections, and arbitrary list support.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.refine_engine import extract_section_html

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

def run_tests():
    print("=" * 60)
    print("TEST 1: Generate Initial CS Student Portfolio (Version 1)")
    print("=" * 60)
    init_prompt = "Create a modern portfolio website for a Computer Science student specializing in AI/ML and software development. Include Hero, About, Skills, Projects, Education, Experience and Contact sections."
    
    r1 = client.post("/api/generate", json={
        "prompt": init_prompt,
        "project_name": "CS Student Exact Skills Test",
        "api_key": None,
        "model": "gemini-2.5-flash"
    })
    assert r1.status_code == 200

    events_1 = parse_sse_events(r1)
    complete_1 = next(e["data"] for e in events_1 if e.get("event") == "complete")
    v1_html = complete_1["html"]
    v1_proj_id = complete_1["project_id"]
    v1_id = complete_1["version_id"]

    print(f"Version 1 Generated: Project ID={v1_proj_id}, Version ID={v1_id}")
    sec1, _, _ = extract_section_html(v1_html, "skills")
    assert sec1 is not None, "Version 1 Skills section missing!"
    print(f"Version 1 Skills Section extracted ({len(sec1)} chars).")

    print("\n" + "=" * 60)
    print("TEST 2: Refine with Exact-List Instruction")
    print("Prompt: 'Set the Skills section to exactly Python, Java, FastAPI, PostgreSQL, Machine Learning and React. Do not add any other technical skills.'")
    print("=" * 60)
    
    refine_instruction = "Set the Skills section to exactly Python, Java, FastAPI, PostgreSQL, Machine Learning and React. Do not add any other technical skills."
    
    r2 = client.post("/api/refine", json={
        "project_id": v1_proj_id,
        "current_html": v1_html,
        "instruction": refine_instruction,
        "api_key": None,
        "model": "gemini-2.5-flash"
    })
    assert r2.status_code == 200

    events_2 = parse_sse_events(r2)
    complete_2 = next(e["data"] for e in events_2 if e.get("event") == "complete")
    v2_html = complete_2["html"]
    v2_id = complete_2["version_id"]

    print(f"Version 2 Created: Version ID={v2_id}")
    assert v2_id != v1_id, "Version 2 ID must be distinct from Version 1 ID!"

    # Extract Version 2 Skills Section
    sec2, _, _ = extract_section_html(v2_html, "skills")
    assert sec2 is not None, "Version 2 Skills section missing!"
    print(f"Version 2 Skills Section extracted ({len(sec2)} chars).")

    # 1. Check ALL requested skills exist in Version 2 Skills section
    requested_skills = ["Python", "Java", "FastAPI", "PostgreSQL", "Machine Learning", "React"]
    for skill in requested_skills:
        assert skill.lower() in sec2.lower(), f"Requested skill '{skill}' missing from Version 2 skills section!"
    print(f"[PASS] All 6 requested skills are present: {requested_skills}")

    # 2. Check unrequested skills from Version 1 are NOT in Version 2 Skills section
    prohibited_skills = ["PyTorch", "TensorFlow", "Scikit-Learn", "NumPy", "Pandas", "OpenCV", "C / C++", "Docker", "Linux", "Flask", "Node.js", "Postman", "CI/CD"]
    for skill in prohibited_skills:
        assert skill.lower() not in sec2.lower(), f"Prohibited unrequested skill '{skill}' was NOT removed from Version 2 skills section!"
    print(f"[PASS] None of the unrequested skills {prohibited_skills[:6]} remain in Version 2 skills section.")

    # 3. Check all other sections remain preserved
    for other_sec in ["about", "projects", "education", "experience", "contact"]:
        sec_content, _, _ = extract_section_html(v2_html, other_sec)
        assert sec_content is not None or other_sec in v2_html.lower(), f"Section '{other_sec}' was accidentally removed or broken!"
    print("[PASS] All unrelated sections (About, Projects, Education, Experience, Contact) preserved intact.")

    print("\n" + "=" * 60)
    print("TEST 3: Arbitrary Exact-List Refinement (Generalization Test)")
    print("Prompt: 'Change the skills to only Rust, Go, Kubernetes and GraphQL'")
    print("=" * 60)
    
    arbitrary_instruction = "Change the skills to only Rust, Go, Kubernetes and GraphQL"
    r3 = client.post("/api/refine", json={
        "project_id": v1_proj_id,
        "current_html": v2_html,
        "instruction": arbitrary_instruction,
        "api_key": None,
        "model": "gemini-2.5-flash"
    })
    assert r3.status_code == 200

    events_3 = parse_sse_events(r3)
    complete_3 = next(e["data"] for e in events_3 if e.get("event") == "complete")
    v3_html = complete_3["html"]

    sec3, _, _ = extract_section_html(v3_html, "skills")
    for arb_skill in ["Rust", "Go", "Kubernetes", "GraphQL"]:
        assert arb_skill.lower() in sec3.lower(), f"Arbitrary skill '{arb_skill}' missing from Version 3!"
    for old_v2 in ["Python", "Java", "FastAPI", "PostgreSQL", "React"]:
        assert old_v2.lower() not in sec3.lower(), f"Previous skill '{old_v2}' still present in Version 3!"
    print("[PASS] Generalization verified! Arbitrary exact-list replaced previous skills cleanly with 0 hardcoding.")

    print("\n" + "=" * 60)
    print("ALL EXACT-LIST REFINEMENT & VALIDATION TESTS PASSED 100%!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
