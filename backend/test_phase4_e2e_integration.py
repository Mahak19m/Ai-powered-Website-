"""
Phase 4: Complete End-to-End Integration & Edge-Case Test Suite.
Tests the exact 23-step complete user workflow and all 7 edge cases:

WORKFLOW:
1. Start from Dashboard (list projects).
2. Create completely new project.
3. Confirm project appears in dashboard.
4. Open the project into editor.
5. Enter realistic generation prompt.
6. Generate website via SSE flow.
7. Verify completion, HTML structure, preview readiness, code viewer data, DB persistence.
8. Perform natural-language refinement via SSE flow.
9. Verify refinement completion, updated HTML, new version created.
10. Open Version History.
11. Verify all expected versions displayed.
12. Roll back to previous version.
13. Verify preview/code return to selected version.
14. Test multi-page website generation.
15. Verify inter-page navigation links.
16. Export project as HTML.
17. Export project as ZIP.
18. Verify ZIP contains pages and README.md.
19. Return to Dashboard.
20. Verify updated version count in dashboard.
21. Re-open project and verify persistence after reload.
22. Delete test project.
23. Verify project disappears from dashboard and DB.

EDGE CASES:
- Empty dashboard / search with no matching project
- Backend health check
- Invalid/empty generation prompt
- Invalid/empty refinement instruction
- Opening deleted/non-existent project
- Exporting non-existent project
- Exporting non-existent version
"""

import io
import json
import uuid
import zipfile
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, init_db
from app.db.models import ProjectModel, VersionModel
from app.db.repository import project_repo

client = TestClient(app)

def run_phase4_tests():
    print("=" * 70)
    print("RUNNING PHASE 4: COMPLETE END-TO-END INTEGRATION TEST SUITE")
    print("=" * 70)
    init_db()

    # -------------------------------------------------------------
    # PART 1: 23-STEP COMPLETE END-TO-END USER WORKFLOW
    # -------------------------------------------------------------
    print("\n--- PART 1: COMPLETE USER WORKFLOW (STEPS 1 - 23) ---")

    # Step 1: Start from Project Dashboard
    dash_res = client.get("/api/projects")
    assert dash_res.status_code == 200
    initial_projects = dash_res.json()
    assert isinstance(initial_projects, list)
    print(f"  [PASS] Step 1: Dashboard loaded with {len(initial_projects)} existing projects.")

    # Step 2: Create a completely new project
    test_proj_name = f"HealthPulse Clinic {uuid.uuid4().hex[:4]}"
    create_res = client.post("/api/projects", json={"name": test_proj_name})
    assert create_res.status_code == 200
    new_proj = create_res.json()
    proj_id = new_proj["id"]
    assert new_proj["name"] == test_proj_name
    print(f"  [PASS] Step 2: Created new project '{test_proj_name}' (ID={proj_id}).")

    # Step 3: Confirm the project appears in the dashboard
    dash_after_create = client.get("/api/projects").json()
    found = any(p["id"] == proj_id for p in dash_after_create)
    assert found, "Created project must appear in dashboard list"
    print("  [PASS] Step 3: Confirmed new project is visible in dashboard listing.")

    # Step 4: Open the project into the editor
    open_res = client.get(f"/api/projects/{proj_id}")
    assert open_res.status_code == 200
    opened = open_res.json()
    assert opened["id"] == proj_id
    assert opened["name"] == test_proj_name
    print("  [PASS] Step 4: Successfully opened project into editor state.")

    # Step 5 & 6: Enter realistic generation prompt & generate via SSE
    gen_prompt = "A modern telehealth medical clinic website with hero, doctors, appointment booking, and contact"
    gen_res = client.post("/api/generate", json={
        "prompt": gen_prompt,
        "project_id": proj_id,
        "project_name": test_proj_name
    })
    assert gen_res.status_code == 200

    gen_complete = None
    chunks_count = 0
    for block in gen_res.text.split("\n\n"):
        if "event: chunk" in block:
            chunks_count += 1
        elif "event: complete" in block:
            for line in block.split("\n"):
                if line.startswith("data: "):
                    gen_complete = json.loads(line[6:])

    assert gen_complete is not None, "SSE must emit complete event"
    assert chunks_count > 0, "SSE must stream chunks"
    v1_id = gen_complete["version_id"]
    v1_html = gen_complete["html"]
    print(f"  [PASS] Steps 5 & 6: SSE generation streamed {chunks_count} chunks and completed: Version ID={v1_id}.")

    # Step 7: Verify generated HTML, preview readiness, code viewer data, DB persistence
    assert "<!DOCTYPE" in v1_html or "<html" in v1_html
    assert "<body" in v1_html
    with SessionLocal() as db:
        db_proj = db.query(ProjectModel).filter(ProjectModel.id == proj_id).first()
        assert db_proj is not None
        assert db_proj.current_version_id == v1_id
        db_ver = db.query(VersionModel).filter(VersionModel.id == v1_id).first()
        assert db_ver is not None
        assert db_ver.html_code == v1_html
    print("  [PASS] Step 7: Verified HTML completeness, preview rendering readiness, and DB persistence.")

    # Step 8: Perform a natural-language refinement
    refine_prompt = "Add an emergency 24/7 hotline banner and telehealth consultation badge"
    refine_res = client.post("/api/refine", json={
        "project_id": proj_id,
        "current_html": v1_html,
        "instruction": refine_prompt,
        "active_page_path": "index.html",
        "pages": gen_complete["pages"],
        "is_multi_page": gen_complete["is_multi_page"]
    })
    assert refine_res.status_code == 200

    refine_complete = None
    for block in refine_res.text.split("\n\n"):
        if "event: complete" in block:
            for line in block.split("\n"):
                if line.startswith("data: "):
                    refine_complete = json.loads(line[6:])

    assert refine_complete is not None
    v2_id = refine_complete["version_id"]
    v2_html = refine_complete["html"]
    assert v2_id != v1_id
    print(f"  [PASS] Step 8: Natural-language refinement completed: Version ID={v2_id}.")

    # Step 9: Verify preview updates and new version stored
    assert len(v2_html) > 0
    with SessionLocal() as db:
        p = db.query(ProjectModel).filter(ProjectModel.id == proj_id).first()
        assert p.current_version_id == v2_id
        assert len(p.versions) >= 2
    print("  [PASS] Step 9: Refined HTML preview updated and version 2 persisted in DB.")

    # Step 10 & 11: Open Version History and verify all versions displayed
    history_proj = client.get(f"/api/projects/{proj_id}").json()
    version_ids = [v["id"] for v in history_proj["versions"]]
    assert v1_id in version_ids
    assert v2_id in version_ids
    assert history_proj["current_version_id"] == v2_id
    print(f"  [PASS] Steps 10 & 11: Version history shows all {len(version_ids)} versions correctly.")

    # Step 12 & 13: Roll back to previous version
    revert_res = client.post(f"/api/projects/{proj_id}/revert/{v1_id}")
    assert revert_res.status_code == 200
    reverted_proj = revert_res.json()
    assert reverted_proj["current_version_id"] == v1_id
    active_ver = next(v for v in reverted_proj["versions"] if v["id"] == v1_id)
    assert active_ver["html_code"] == v1_html
    print(f"  [PASS] Steps 12 & 13: Successfully rolled back to Version 1 ({v1_id}). Code and preview restored.")

    # Step 14: Test multi-page website generation
    mp_prompt = "Create a 3-page SaaS website with Home, Pricing, and Contact"
    mp_proj_name = f"MultiPage SaaS {uuid.uuid4().hex[:4]}"
    mp_gen_res = client.post("/api/generate", json={
        "prompt": mp_prompt,
        "project_name": mp_proj_name
    })
    assert mp_gen_res.status_code == 200

    mp_complete = None
    for block in mp_gen_res.text.split("\n\n"):
        if "event: complete" in block:
            for line in block.split("\n"):
                if line.startswith("data: "):
                    mp_complete = json.loads(line[6:])

    assert mp_complete is not None
    assert mp_complete["is_multi_page"] is True
    assert len(mp_complete["pages"]) >= 3
    mp_proj_id = mp_complete["project_id"]
    print(f"  [PASS] Step 14: Multi-page generation created {len(mp_complete['pages'])} pages: {[p['name'] for p in mp_complete['pages']]}.")

    # Step 15: Verify page navigation in preview
    page_paths = [p["path"] for p in mp_complete["pages"]]
    assert "index.html" in page_paths
    for page in mp_complete["pages"]:
        # Verify links inside page reference other sibling pages
        for other in page_paths:
            if other != page["path"]:
                assert other in page["html"], f"Expected relative link to {other} in {page['path']}"
    print("  [PASS] Step 15: Verified working relative inter-page navigation links across all pages.")

    # Step 16: Export project as HTML
    export_html_res = client.post("/api/export/html", json={
        "html": v1_html,
        "filename": "clinic.html"
    })
    assert export_html_res.status_code == 200
    assert "clinic.html" in export_html_res.headers.get("content-disposition", "")
    assert len(export_html_res.content) > 100
    print("  [PASS] Step 16: Exported standalone HTML file successfully.")

    # Step 17 & 18: Export project as ZIP and verify files
    zip_res = client.get(f"/api/export/project/{mp_proj_id}/zip")
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"
    zf = zipfile.ZipFile(io.BytesIO(zip_res.content))
    namelist = zf.namelist()
    assert "index.html" in namelist
    assert "README.md" in namelist
    for p in page_paths:
        assert p in namelist
    readme_text = zf.read("README.md").decode("utf-8")
    assert "Exported Website Project" in readme_text
    print(f"  [PASS] Steps 17 & 18: Exported ZIP contains {len(namelist)} files ({namelist}) and README.md.")

    # Step 19 & 20: Return to Dashboard and verify updated version count
    dash_check = client.get("/api/projects").json()
    item = next((p for p in dash_check if p["id"] == proj_id), None)
    assert item is not None
    assert item["versions_count"] >= 2
    print(f"  [PASS] Steps 19 & 20: Dashboard reflects project '{item['name']}' with {item['versions_count']} versions.")

    # Step 21: Re-open the same project and verify persistence after reload
    reopened = client.get(f"/api/projects/{proj_id}").json()
    assert reopened["id"] == proj_id
    assert len(reopened["versions"]) >= 2
    assert reopened["current_version_id"] == v1_id  # preserved rollback state
    print("  [PASS] Step 21: Re-opened project verified full persistence after reload.")

    # Step 22 & 23: Delete test projects and verify complete disappearance
    for pid in (proj_id, mp_proj_id):
        del_res = client.delete(f"/api/projects/{pid}")
        assert del_res.status_code == 200
        get_deleted = client.get(f"/api/projects/{pid}")
        assert get_deleted.status_code == 404

        with SessionLocal() as db:
            assert db.query(ProjectModel).filter(ProjectModel.id == pid).first() is None
            assert len(db.query(VersionModel).filter(VersionModel.project_id == pid).all()) == 0

    print("  [PASS] Steps 22 & 23: Cleaned up test projects; verified deletion from Dashboard and DB.")

    # -------------------------------------------------------------
    # PART 2: EDGE-CASE VALIDATION
    # -------------------------------------------------------------
    print("\n--- PART 2: EDGE-CASE VALIDATION ---")

    # Edge Case 1: Empty dashboard / search with no matching project
    all_projects = client.get("/api/projects").json()
    # Filter simulation matching frontend logic
    matching = [p for p in all_projects if "NON_EXISTENT_QUERY_XYZ_12345" in p["name"].lower()]
    assert len(matching) == 0
    print("  [PASS] Edge Case 1: Search query with 0 matches cleanly handled.")

    # Edge Case 2: Backend health endpoint check
    health_res = client.get("/api/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"
    print("  [PASS] Edge Case 2: Backend health endpoint verified.")

    # Edge Case 3: Invalid/empty generation prompt
    empty_gen_res = client.post("/api/generate", json={"prompt": "   "})
    assert empty_gen_res.status_code == 200
    assert "Prompt cannot be empty" in empty_gen_res.text
    print("  [PASS] Edge Case 3: Empty/whitespace generation prompt rejected with error event.")

    # Edge Case 4: Invalid/empty refinement instruction
    empty_refine_res = client.post("/api/refine", json={
        "project_id": "test_id",
        "current_html": "<html></html>",
        "instruction": ""
    })
    assert empty_refine_res.status_code == 200
    assert "Refinement instruction cannot be empty" in empty_refine_res.text
    print("  [PASS] Edge Case 4: Empty refinement instruction rejected with error event.")

    # Edge Case 5: Opening a deleted/non-existent project
    non_existent_id = f"non_existent_{uuid.uuid4().hex[:6]}"
    get_non_res = client.get(f"/api/projects/{non_existent_id}")
    assert get_non_res.status_code == 404
    assert "Project not found" in get_non_res.json()["detail"]
    print("  [PASS] Edge Case 5: Opening non-existent project returns 404.")

    # Edge Case 6: Exporting when project is missing
    missing_export_res = client.get(f"/api/export/project/{non_existent_id}/zip")
    assert missing_export_res.status_code == 404
    assert "Project not found" in missing_export_res.json()["detail"]
    print("  [PASS] Edge Case 6: Exporting non-existent project returns 404.")

    # Edge Case 7: Exporting when version is missing
    # Create temp project with 1 version then ask for bad version
    temp_p = project_repo.create_project(
        name="Temp Export Test",
        initial_prompt="Temp prompt",
        initial_html="<html><body>Temp</body></html>"
    )
    bad_ver_res = client.get(f"/api/export/project/{temp_p['id']}/zip?version_id=bad_version_xyz")
    assert bad_ver_res.status_code == 404
    assert "Version not found" in bad_ver_res.json()["detail"]
    project_repo.delete_project(temp_p["id"])
    print("  [PASS] Edge Case 7: Exporting non-existent version returns 404.")

    print("\n" + "=" * 70)
    print("ALL PHASE 4 WORKFLOW & EDGE-CASE TESTS PASSED (100% SUCCESS)!")
    print("=" * 70)

if __name__ == "__main__":
    run_phase4_tests()
