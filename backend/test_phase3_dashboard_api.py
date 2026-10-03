"""
Comprehensive API and Integration Test Suite for Phase 3:
Tests Dashboard & Editor API operations:
1. List projects (Dashboard view)
2. Create new project from Dashboard (POST /api/projects)
3. Open/Retrieve project into Editor (GET /api/projects/{id})
4. Generate site for pre-created project (POST /api/generate)
5. Refine website in Editor (POST /api/refine)
6. Rollback version in Editor (POST /api/projects/{id}/revert/{version_id})
7. Export project ZIP (GET /api/export/project/{id}/zip)
8. Delete project from Dashboard (DELETE /api/projects/{id})
9. Verify deletion cascade in database and list endpoint
"""
import uuid
import json
import io
import zipfile
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, init_db
from app.db.models import ProjectModel, VersionModel
from app.db.repository import project_repo

client = TestClient(app)

def run_phase3_tests():
    print("=" * 60)
    print("RUNNING PHASE 3 DASHBOARD & WORKFLOW TEST SUITE")
    print("=" * 60)
    init_db()

    # 1. Test Project Listing (Dashboard query)
    res = client.get("/api/projects")
    assert res.status_code == 200, f"Failed listing projects: {res.text}"
    projects_list = res.json()
    assert isinstance(projects_list, list)
    print(f"  [PASS] 1. Dashboard project listing returned {len(projects_list)} projects.")

    # 2. Test Create Project from Dashboard
    proj_name = f"Phase 3 Test App {uuid.uuid4().hex[:4]}"
    create_res = client.post("/api/projects", json={"name": proj_name})
    assert create_res.status_code == 200, f"Create project failed: {create_res.text}"
    created_proj = create_res.json()
    project_id = created_proj["id"]
    assert created_proj["name"] == proj_name
    assert "current_version_id" in created_proj
    print(f"  [PASS] 2. Dashboard create project succeeded: ID={project_id}, Name='{proj_name}'")

    # 3. Test Open/Retrieve Project into Editor
    get_res = client.get(f"/api/projects/{project_id}")
    assert get_res.status_code == 200, f"Retrieve project failed: {get_res.text}"
    opened_proj = get_res.json()
    assert opened_proj["id"] == project_id
    assert opened_proj["name"] == proj_name
    assert len(opened_proj["versions"]) >= 1
    print(f"  [PASS] 3. Open project into Editor succeeded with full version state.")

    # 4. Test Website Generation into the Pre-Created Project
    gen_res = client.post("/api/generate", json={
        "prompt": "Modern cybersecurity platform landing page",
        "project_id": project_id,
        "project_name": proj_name
    })
    assert gen_res.status_code == 200, f"Generation failed: {gen_res.text}"

    gen_complete_data = None
    for line in gen_res.text.split("\n\n"):
        if "event: complete" in line:
            for subline in line.split("\n"):
                if subline.startswith("data: "):
                    gen_complete_data = json.loads(subline[6:])
    assert gen_complete_data is not None, "Did not receive complete event in SSE generation"
    assert gen_complete_data["project_id"] == project_id
    assert len(gen_complete_data["html"]) > 100
    v1_id = gen_complete_data["version_id"]
    print(f"  [PASS] 4. SSE generation on pre-created project succeeded: Version ID={v1_id}")

    # 5. Test Iterative Refinement
    refine_res = client.post("/api/refine", json={
        "project_id": project_id,
        "current_html": gen_complete_data["html"],
        "instruction": "Add a 24/7 incident response hotline banner at the top",
        "active_page_path": "index.html",
        "pages": gen_complete_data["pages"],
        "is_multi_page": gen_complete_data["is_multi_page"]
    })
    assert refine_res.status_code == 200, f"Refine failed: {refine_res.text}"

    refine_complete_data = None
    for line in refine_res.text.split("\n\n"):
        if "event: complete" in line:
            for subline in line.split("\n"):
                if subline.startswith("data: "):
                    refine_complete_data = json.loads(subline[6:])
    assert refine_complete_data is not None, "Did not receive complete event in SSE refinement"
    v2_id = refine_complete_data["version_id"]
    assert v2_id != v1_id
    print(f"  [PASS] 5. SSE refinement succeeded: New Version ID={v2_id}")

    # 6. Test Version Rollback in Editor
    revert_res = client.post(f"/api/projects/{project_id}/revert/{v1_id}")
    assert revert_res.status_code == 200, f"Rollback failed: {revert_res.text}"
    reverted_proj = revert_res.json()
    assert reverted_proj["current_version_id"] == v1_id
    print(f"  [PASS] 6. Rollback to version v1 succeeded: Active version is {v1_id}")

    # 7. Test Export Project ZIP
    zip_res = client.get(f"/api/export/project/{project_id}/zip")
    assert zip_res.status_code == 200, f"Export ZIP failed: {zip_res.text}"
    assert zip_res.headers["content-type"] == "application/zip"
    zf = zipfile.ZipFile(io.BytesIO(zip_res.content))
    assert "index.html" in zf.namelist()
    assert "README.md" in zf.namelist()
    print(f"  [PASS] 7. Export ZIP package succeeded: Bundled {len(zf.namelist())} files.")

    # 8. Test Delete Project from Dashboard
    del_res = client.delete(f"/api/projects/{project_id}")
    assert del_res.status_code == 200, f"Delete failed: {del_res.text}"
    assert del_res.json()["status"] == "success"
    print(f"  [PASS] 8. Delete project from Dashboard succeeded.")

    # 9. Verify Project is completely removed from DB & Listing
    get_after_del = client.get(f"/api/projects/{project_id}")
    assert get_after_del.status_code == 404, "Project should be 404 after deletion"

    with SessionLocal() as db:
        model_check = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        assert model_check is None, "Project model should be deleted from DB"
        ver_check = db.query(VersionModel).filter(VersionModel.project_id == project_id).all()
        assert len(ver_check) == 0, "All versions should be cascade deleted from DB"
    print(f"  [PASS] 9. Cascade deletion verified in DB session and API query.")

    print("=" * 60)
    print("ALL PHASE 3 DASHBOARD & WORKFLOW TESTS PASSED (100% OK)!")
    print("=" * 60)

if __name__ == "__main__":
    run_phase3_tests()
