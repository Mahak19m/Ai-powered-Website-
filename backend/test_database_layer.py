"""
Comprehensive verification test suite for the WebCraft AI Database Layer.

Tests:
1. Project creation
2. Project listing
3. Project retrieval
4. Version creation
5. Version retrieval
6. Version rollback
7. Direct SQLite persistence verification via SQLAlchemy session
8. API endpoints integration with database layer
"""

import uuid
from app.db.session import SessionLocal, init_db
from app.db.models import ProjectModel, VersionModel
from app.db.repository import ProjectRepository, project_repo
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_project_creation_and_listing():
    init_db()
    test_id = f"test_{uuid.uuid4().hex[:6]}"
    project = project_repo.create_project(
        name="Test Portfolio App",
        initial_prompt="Create a modern portfolio for a cloud architect",
        initial_html="<html><body><h1>Cloud Architect</h1></body></html>",
        pages=[{"name": "Home", "path": "index.html", "html": "<html><body><h1>Cloud Architect</h1></body></html>"}],
        is_multi_page=False,
        project_id=test_id
    )

    assert project["id"] == test_id
    assert project["name"] == "Test Portfolio App"
    assert len(project["versions"]) == 1
    assert project["current_version_id"] == project["versions"][0]["id"]

    projects = project_repo.list_all()
    assert isinstance(projects, list)
    assert len(projects) > 0
    found = any(p["id"] == test_id for p in projects)
    assert found is True

    # Cleanup
    project_repo.delete_project(test_id)


def test_project_retrieval():
    init_db()
    test_id = f"test_{uuid.uuid4().hex[:6]}"
    project_repo.create_project(
        name="Test Retrieval App",
        initial_prompt="Sample landing page",
        initial_html="<html><body><h1>Sample</h1></body></html>",
        pages=[{"name": "Home", "path": "index.html", "html": "<html><body><h1>Sample</h1></body></html>"}],
        is_multi_page=False,
        project_id=test_id
    )

    project = project_repo.get(test_id)
    assert project is not None
    assert project["id"] == test_id
    assert project["name"] == "Test Retrieval App"
    assert len(project["versions"]) >= 1

    # Cleanup
    project_repo.delete_project(test_id)


def test_version_creation_and_retrieval():
    init_db()
    test_id = f"test_{uuid.uuid4().hex[:6]}"
    project_repo.create_project(
        name="Test Version App",
        initial_prompt="Initial prompt",
        initial_html="<html><body><h1>V1</h1></body></html>",
        pages=[{"name": "Home", "path": "index.html", "html": "<html><body><h1>V1</h1></body></html>"}],
        is_multi_page=False,
        project_id=test_id
    )

    new_version = project_repo.add_version(
        project_id=test_id,
        prompt="Add certifications and AWS badge section",
        html_code="<html><body><h1>Cloud Architect</h1><section>AWS Certified</section></body></html>",
        pages=[{"name": "Home", "path": "index.html", "html": "<html><body><h1>Cloud Architect</h1><section>AWS Certified</section></body></html>"}],
        is_multi_page=False,
        version_type="refinement"
    )

    assert new_version is not None
    assert new_version["prompt"] == "Add certifications and AWS badge section"
    assert new_version["version_type"] == "refinement"

    updated_project = project_repo.get(test_id)
    assert len(updated_project["versions"]) == 2
    assert updated_project["current_version_id"] == new_version["id"]

    version = next((v for v in updated_project["versions"] if v["id"] == new_version["id"]), None)
    assert version is not None
    assert "AWS Certified" in version["html_code"]

    # Cleanup
    project_repo.delete_project(test_id)


def test_version_rollback():
    init_db()
    test_id = f"test_{uuid.uuid4().hex[:6]}"
    proj = project_repo.create_project(
        name="Test Rollback App",
        initial_prompt="V1 Prompt",
        initial_html="<html><body><h1>Version 1</h1></body></html>",
        pages=[{"name": "Home", "path": "index.html", "html": "<html><body><h1>Version 1</h1></body></html>"}],
        is_multi_page=False,
        project_id=test_id
    )
    v1_id = proj["current_version_id"]

    v2 = project_repo.add_version(
        project_id=test_id,
        prompt="V2 Refinement",
        html_code="<html><body><h1>Version 2</h1></body></html>",
        pages=[{"name": "Home", "path": "index.html", "html": "<html><body><h1>Version 2</h1></body></html>"}],
        is_multi_page=False,
        version_type="refinement"
    )
    v2_id = v2["id"]

    project = project_repo.get(test_id)
    assert project["current_version_id"] == v2_id

    # Roll back to initial version
    reverted_project = project_repo.revert_version(test_id, v1_id)
    assert reverted_project["current_version_id"] == v1_id

    # Confirm by re-fetching
    fetched = project_repo.get(test_id)
    assert fetched["current_version_id"] == v1_id

    # Cleanup
    project_repo.delete_project(test_id)


def test_database_persistence():
    init_db()
    test_id = f"test_{uuid.uuid4().hex[:6]}"
    project_repo.create_project(
        name="Test DB Persistence App",
        initial_prompt="Initial prompt",
        initial_html="<html><body>Persistence Test</body></html>",
        pages=[{"name": "Home", "path": "index.html", "html": "<html><body>Persistence Test</body></html>"}],
        is_multi_page=False,
        project_id=test_id
    )
    project_repo.add_version(
        project_id=test_id,
        prompt="Update v2",
        html_code="<html><body>Persistence Test v2</body></html>",
        pages=[{"name": "Home", "path": "index.html", "html": "<html><body>Persistence Test v2</body></html>"}],
        is_multi_page=False,
        version_type="refinement"
    )

    # Verify directly using raw SQLAlchemy SessionLocal
    with SessionLocal() as db:
        proj_model = db.query(ProjectModel).filter(ProjectModel.id == test_id).first()
        assert proj_model is not None
        assert proj_model.id == test_id
        assert len(proj_model.versions) == 2

        versions = db.query(VersionModel).filter(VersionModel.project_id == test_id).all()
        assert len(versions) == 2

    # Cleanup
    project_repo.delete_project(test_id)


def test_api_endpoints_db_integration():
    init_db()
    # Test GET /api/projects
    res = client.get("/api/projects")
    assert res.status_code == 200
    projects = res.json()
    assert isinstance(projects, list)
    assert len(projects) > 0

    # Test POST /api/projects
    create_payload = {
        "name": "API DB Test Website",
        "initial_prompt": "Landing page for cybersecurity startup",
        "initial_html": "<html><body>CyberShield Landing</body></html>",
        "pages": [{"name": "Home", "path": "index.html", "html": "<html><body>CyberShield Landing</body></html>"}],
        "is_multi_page": False
    }
    create_res = client.post("/api/projects", json=create_payload)
    assert create_res.status_code == 200
    created = create_res.json()
    pid = created["id"]
    vid = created["current_version_id"]

    # Test GET /api/projects/{id}
    get_res = client.get(f"/api/projects/{pid}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "API DB Test Website"

    # Test POST /api/projects/{id}/revert/{vid}
    revert_res = client.post(f"/api/projects/{pid}/revert/{vid}")
    assert revert_res.status_code == 200
    assert revert_res.json()["current_version_id"] == vid

    # Clean up test project
    delete_res = client.delete(f"/api/projects/{pid}")
    assert delete_res.status_code == 200


if __name__ == "__main__":
    init_db()
    test_project_creation_and_listing()
    print("  [PASS] test_project_creation_and_listing")
    test_project_retrieval()
    print("  [PASS] test_project_retrieval")
    test_version_creation_and_retrieval()
    print("  [PASS] test_version_creation_and_retrieval")
    test_version_rollback()
    print("  [PASS] test_version_rollback")
    test_database_persistence()
    print("  [PASS] test_database_persistence (Direct SQLAlchemy check)")
    test_api_endpoints_db_integration()
    print("  [PASS] test_api_endpoints_db_integration")
    print("=" * 60)
    print("ALL DATABASE LAYER TESTS PASSED SUCCESSFULLY! 100% OK")
    print("=" * 60)
