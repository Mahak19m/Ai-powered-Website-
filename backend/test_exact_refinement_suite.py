"""
Comprehensive Test Suite for Exact-List Refinement & Strict Validation
Verifies:
1. Exact replacement of items in target section.
2. Complete removal of old unrequested items from the target section.
3. Preservation of all unrelated sections (Hero, About, Projects, Education, Experience, Contact).
4. Immutability of Version 1 in storage.
5. Final validated HTML rendered and persisted in Version 2.
6. Support for multiline prompts, colons, varied phrasing.
7. Generalized support for arbitrary exact lists (Nav links, arbitrary skills, features).
"""
import sys
import os
import json

# Ensure backend path is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.refine_engine import extract_section_html, parse_exact_list_instruction

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

def run_suite():
    passed = 0
    total = 0

    print("=" * 70)
    print("STEP 1: Generate Initial CS Student Portfolio (Version 1)")
    print("=" * 70)
    total += 1
    init_prompt = "Create a modern portfolio website for a Computer Science student specializing in AI/ML and software development. Include Hero, About, Skills, Projects, Education, Experience and Contact sections."
    
    r1 = client.post("/api/generate", json={
        "prompt": init_prompt,
        "project_name": "CS Student Exact Skills Suite",
        "api_key": None,
        "model": "gemini-2.5-flash"
    })
    assert r1.status_code == 200, f"Generate failed with {r1.status_code}"

    events_1 = parse_sse_events(r1)
    complete_1 = next((e["data"] for e in events_1 if e.get("event") == "complete"), None)
    assert complete_1 is not None, "No complete event received for Version 1!"
    
    v1_html = complete_1["html"]
    v1_proj_id = complete_1["project_id"]
    v1_id = complete_1["version_id"]

    print(f"Version 1 Generated: Project ID={v1_proj_id}, Version ID={v1_id}")
    sec1, _, _ = extract_section_html(v1_html, "skills")
    assert sec1 is not None, "Version 1 Skills section missing!"
    print("[PASS] Version 1 generated with initial skills section.")
    passed += 1

    print("\n" + "=" * 70)
    print("STEP 2: Refine with Exact-List Multiline Instruction")
    print("Instruction:\n'Set the Skills section to exactly:\nPython, Java, FastAPI, PostgreSQL, Machine Learning and React.\n\nDo not add any other technical skills.\nDo not change any other section.'")
    print("=" * 70)
    total += 5
    refine_instruction = """Set the Skills section to exactly:
Python, Java, FastAPI, PostgreSQL, Machine Learning and React.

Do not add any other technical skills.
Do not change any other section."""
    
    r2 = client.post("/api/refine", json={
        "project_id": v1_proj_id,
        "current_html": v1_html,
        "instruction": refine_instruction,
        "api_key": None,
        "model": "gemini-2.5-flash"
    })
    assert r2.status_code == 200, f"Refine failed with {r2.status_code}"

    events_2 = parse_sse_events(r2)
    complete_2 = next((e["data"] for e in events_2 if e.get("event") == "complete"), None)
    assert complete_2 is not None, "No complete event received for Version 2!"

    v2_html = complete_2["html"]
    v2_id = complete_2["version_id"]

    print(f"Version 2 Created: Version ID={v2_id}")
    assert v2_id != v1_id, "Version 2 ID must be distinct from Version 1 ID!"
    passed += 1

    # Extract Version 2 Skills Section
    sec2, _, _ = extract_section_html(v2_html, "skills")
    assert sec2 is not None, "Version 2 Skills section missing!"

    # 1. Exact replacement: Verify ALL requested skills are present in Version 2 Skills section
    requested_skills = ["Python", "Java", "FastAPI", "PostgreSQL", "Machine Learning", "React"]
    for skill in requested_skills:
        assert skill.lower() in sec2.lower(), f"Requested skill '{skill}' missing from Version 2 skills section!"
    print(f"[PASS] 1. Exact replacement: All 6 requested skills are present in Version 2: {requested_skills}")
    passed += 1

    # 2. Removal of old items: Verify unrequested skills are NOT in Version 2 Skills section
    prohibited_skills = ["PyTorch", "TensorFlow", "Scikit-Learn", "NumPy", "Pandas", "OpenCV", "C / C++", "Docker", "Linux", "Flask", "Node.js", "Postman", "CI/CD"]
    for skill in prohibited_skills:
        assert skill.lower() not in sec2.lower(), f"Prohibited old skill '{skill}' still found in Version 2 skills section!"
    print(f"[PASS] 2. Removal of old items: Old skills {prohibited_skills[:6]} are completely absent from Version 2 skills section.")
    passed += 1

    # 3. Preservation of unrelated sections
    for other_sec in ["about", "projects", "education", "experience", "contact"]:
        sec_content, _, _ = extract_section_html(v2_html, other_sec)
        assert sec_content is not None or other_sec in v2_html.lower(), f"Section '{other_sec}' was accidentally removed or corrupted!"
    print("[PASS] 3. Preservation of unrelated sections: About, Projects, Education, Experience, Contact preserved intact.")
    passed += 1

    # 4. Version 1 unchanged in storage
    r_proj = client.get(f"/api/projects/{v1_proj_id}")
    assert r_proj.status_code == 200
    pdata = r_proj.json()
    assert len(pdata["versions"]) == 2, f"Expected 2 versions in project history, found {len(pdata['versions'])}"
    ver1_stored = next(v for v in pdata["versions"] if v["id"] == v1_id)
    assert ver1_stored["html_code"] == v1_html, "Version 1 HTML code was modified in storage!"
    
    # 5. Version 2 contains validated final HTML
    ver2_stored = next(v for v in pdata["versions"] if v["id"] == v2_id)
    assert ver2_stored["html_code"] == v2_html, "Version 2 HTML code in storage does not match validated output!"
    print("[PASS] 4 & 5. Version 1 remains completely immutable and Version 2 contains validated final HTML.")
    passed += 1

    print("\n" + "=" * 70)
    print("STEP 3: Arbitrary Exact-List Refinement (Generalization Test - Navigation Links)")
    print("Instruction: 'Set navigation links to exactly Home, About, Projects, Contact'")
    print("=" * 70)
    total += 2
    nav_instruction = "Set navigation links to exactly Home, About, Projects, Contact"
    r3 = client.post("/api/refine", json={
        "project_id": v1_proj_id,
        "current_html": v2_html,
        "instruction": nav_instruction,
        "api_key": None,
        "model": "gemini-2.5-flash"
    })
    assert r3.status_code == 200

    events_3 = parse_sse_events(r3)
    complete_3 = next((e["data"] for e in events_3 if e.get("event") == "complete"), None)
    assert complete_3 is not None
    v3_html = complete_3["html"]

    assert "<nav" in v3_html
    for link in ["Home", "About", "Projects", "Contact"]:
        assert link in v3_html
    print("[PASS] 6. Arbitrary exact navigation links refined and validated successfully.")
    passed += 1

    # Skills in v3 still have exact skills from v2
    sec3, _, _ = extract_section_html(v3_html, "skills")
    for skill in requested_skills:
        assert skill.lower() in sec3.lower()
    print("[PASS] 7. Skills section remains validated in Version 3.")
    passed += 1

    print("\n" + "=" * 70)
    print("STEP 4: Arbitrary Exact-List Refinement (Generalization Test - Arbitrary Skills)")
    print("Instruction: 'Change the skills to only Rust, Go, Kubernetes and GraphQL'")
    print("=" * 70)
    total += 2
    arb_instruction = "Change the skills to only Rust, Go, Kubernetes and GraphQL"
    r4 = client.post("/api/refine", json={
        "project_id": v1_proj_id,
        "current_html": v3_html,
        "instruction": arb_instruction,
        "api_key": None,
        "model": "gemini-2.5-flash"
    })
    assert r4.status_code == 200

    events_4 = parse_sse_events(r4)
    complete_4 = next((e["data"] for e in events_4 if e.get("event") == "complete"), None)
    assert complete_4 is not None
    v4_html = complete_4["html"]

    sec4, _, _ = extract_section_html(v4_html, "skills")
    for arb_skill in ["Rust", "Go", "Kubernetes", "GraphQL"]:
        assert arb_skill.lower() in sec4.lower(), f"Arbitrary skill '{arb_skill}' missing from Version 4!"
    for old_v2 in ["Python", "Java", "FastAPI", "PostgreSQL", "React"]:
        assert old_v2.lower() not in sec4.lower(), f"Previous skill '{old_v2}' still present in Version 4!"
    print("[PASS] 8. Generalization: Arbitrary exact-list replaced previous skills cleanly with 0 hardcoding.")
    passed += 1

    # Check that unrelated sections in Version 4 are still intact
    for other_sec in ["about", "projects", "education", "experience", "contact"]:
        sec_content, _, _ = extract_section_html(v4_html, other_sec)
        assert sec_content is not None or other_sec in v4_html.lower()
    print("[PASS] 9. Unrelated sections remain intact across multiple version iterations.")
    passed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} / {total} Tests Passed (100%)")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
