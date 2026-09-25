"""
Comprehensive Automated Test Suite for WebCraft AI
Tests all backend and proxy endpoints, generation, refinement, persistence, rollback, export, and fallback handling.
"""
import sys
import json
import io
import zipfile
import requests

BASE_BACKEND_URL = "http://127.0.0.1:8000"
BASE_FRONTEND_URL = "http://127.0.0.1:5173"

def print_step(title):
    print(f"\n{'='*60}\n>> [TEST] {title}\n{'='*60}")

def test_all():
    passed = 0
    total = 0

    # -------------------------------------------------------------
    # 1. Health and Root Check
    # -------------------------------------------------------------
    print_step("1. Backend Health & Root Status")
    total += 2
    r_root = requests.get(f"{BASE_BACKEND_URL}/", timeout=5)
    assert r_root.status_code == 200, f"Root failed: {r_root.status_code}"
    root_data = r_root.json()
    print(f"Root response: {root_data}")
    passed += 1

    r_health = requests.get(f"{BASE_BACKEND_URL}/api/health", timeout=5)
    assert r_health.status_code == 200, f"Health check failed: {r_health.status_code}"
    health_data = r_health.json()
    print(f"Health response: {health_data}")
    passed += 1

    # -------------------------------------------------------------
    # 2. Frontend Connectivity
    # -------------------------------------------------------------
    print_step("2. Frontend Dev Server Connectivity")
    total += 1
    r_fe = requests.get(f"{BASE_FRONTEND_URL}/", timeout=5)
    assert r_fe.status_code == 200, f"Frontend failed: {r_fe.status_code}"
    assert "<title>AI Website Builder" in r_fe.text or "root" in r_fe.text
    print("Frontend HTML loaded successfully from http://127.0.0.1:5173")
    passed += 1

    # -------------------------------------------------------------
    # 3. Test Full Website Generation Flow (SSE Streaming)
    # -------------------------------------------------------------
    print_step("3. Full Website Generation Flow (SSE Streaming)")
    total += 3
    gen_payload = {
        "prompt": "Autonomous AI Agent Swarm Platform with dark glassmorphism UI",
        "project_name": "AI Swarm Matrix",
        "api_key": None,  # Test zero-config fallback
        "model": "gemini-2.5-flash"
    }
    r_gen = requests.post(f"{BASE_BACKEND_URL}/api/generate", json=gen_payload, stream=True, timeout=15)
    assert r_gen.status_code == 200, f"Generate request failed: {r_gen.status_code}"

    statuses = []
    chunks = []
    complete_event = None

    buffer = ""
    for line in r_gen.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("event: "):
                curr_event = decoded[7:].strip()
            elif decoded.startswith("data: "):
                data_json = json.loads(decoded[6:].strip())
                if curr_event == "status":
                    statuses.append(data_json)
                elif curr_event == "chunk":
                    chunks.append(data_json.get("chunk", ""))
                elif curr_event == "complete":
                    complete_event = data_json

    print(f"Received {len(statuses)} status events, {len(chunks)} streaming chunks.")
    assert len(chunks) > 0, "No chunks streamed!"
    passed += 1

    assert complete_event is not None, "Complete event missing!"
    project_id = complete_event.get("project_id")
    version_1_id = complete_event.get("version_id")
    generated_html = complete_event.get("html", "")
    print(f"Generation Complete! Project ID: {project_id}, Version: {version_1_id}")
    print(f"Generated HTML size: {len(generated_html)} chars, has <!DOCTYPE html>: {'<!DOCTYPE html>' in generated_html or '<html' in generated_html}")
    assert "<!DOCTYPE html>" in generated_html or "<html" in generated_html
    passed += 1
    passed += 1

    # -------------------------------------------------------------
    # 4. Test Refine / Edit Flow (SSE Streaming)
    # -------------------------------------------------------------
    print_step("4. Website Refinement Flow (SSE Streaming)")
    total += 3
    refine_payload = {
        "project_id": project_id,
        "current_html": generated_html,
        "instruction": "Change primary color scheme to dark emerald and add a pricing badge",
        "api_key": None,
        "model": "gemini-2.5-flash"
    }
    r_ref = requests.post(f"{BASE_BACKEND_URL}/api/refine", json=refine_payload, stream=True, timeout=15)
    assert r_ref.status_code == 200, f"Refine request failed: {r_ref.status_code}"

    refine_chunks = []
    refine_complete = None
    for line in r_ref.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("event: "):
                curr_event = decoded[7:].strip()
            elif decoded.startswith("data: "):
                data_json = json.loads(decoded[6:].strip())
                if curr_event == "chunk":
                    refine_chunks.append(data_json.get("chunk", ""))
                elif curr_event == "complete":
                    refine_complete = data_json

    print(f"Refinement chunks received: {len(refine_chunks)}")
    assert len(refine_chunks) > 0
    passed += 1

    assert refine_complete is not None, "Refinement complete event missing!"
    version_2_id = refine_complete.get("version_id")
    refined_html = refine_complete.get("html", "")
    print(f"Refinement Complete! New Version ID: {version_2_id}")
    print(f"Refined HTML size: {len(refined_html)} chars")
    assert version_2_id != version_1_id
    passed += 1
    passed += 1

    # -------------------------------------------------------------
    # 5. Test Project Persistence & Listing
    # -------------------------------------------------------------
    print_step("5. Project Persistence & Listing")
    total += 3
    r_list = requests.get(f"{BASE_BACKEND_URL}/api/projects", timeout=5)
    assert r_list.status_code == 200
    projects = r_list.json()
    print(f"Projects count: {len(projects)}")
    found = next((p for p in projects if p["id"] == project_id), None)
    assert found is not None, f"Project {project_id} not found in listing!"
    print(f"Found project in listing: {found}")
    assert found["versions_count"] == 2
    passed += 1
    passed += 1

    # Fetch full project
    r_detail = requests.get(f"{BASE_BACKEND_URL}/api/projects/{project_id}", timeout=5)
    assert r_detail.status_code == 200
    detail = r_detail.json()
    assert len(detail["versions"]) == 2
    assert detail["current_version_id"] == version_2_id
    print(f"Project details verified: {len(detail['versions'])} versions stored on disk.")
    passed += 1

    # -------------------------------------------------------------
    # 6. Test Version Revert / Rollback
    # -------------------------------------------------------------
    print_step("6. Version Revert / Rollback")
    total += 2
    r_revert = requests.post(f"{BASE_BACKEND_URL}/api/projects/{project_id}/revert/{version_1_id}", timeout=5)
    assert r_revert.status_code == 200, f"Revert failed: {r_revert.status_code}"
    reverted_proj = r_revert.json()
    assert reverted_proj["current_version_id"] == version_1_id, "Revert did not update current_version_id!"
    print(f"Successfully reverted project {project_id} active version back to: {version_1_id}")
    passed += 1
    passed += 1

    # -------------------------------------------------------------
    # 7. Test HTML Export
    # -------------------------------------------------------------
    print_step("7. Single File HTML Export")
    total += 2
    export_payload = {
        "html": generated_html,
        "filename": "landing-page.html"
    }
    r_exp_html = requests.post(f"{BASE_BACKEND_URL}/api/export/html", json=export_payload, timeout=5)
    assert r_exp_html.status_code == 200
    assert "attachment; filename=\"landing-page.html\"" in r_exp_html.headers.get("Content-Disposition", "")
    assert len(r_exp_html.content) == len(generated_html.encode("utf-8"))
    print(f"HTML Export successful: {len(r_exp_html.content)} bytes received with proper attachment header.")
    passed += 1
    passed += 1

    # -------------------------------------------------------------
    # 8. Test ZIP Bundle Export
    # -------------------------------------------------------------
    print_step("8. Complete Deployment ZIP Export")
    total += 3
    r_exp_zip = requests.get(f"{BASE_BACKEND_URL}/api/export/project/{project_id}/zip", timeout=5)
    assert r_exp_zip.status_code == 200
    assert "application/zip" in r_exp_zip.headers.get("Content-Type", "")
    zip_bytes = r_exp_zip.content
    print(f"ZIP package received: {len(zip_bytes)} bytes.")
    passed += 1

    # Inspect ZIP structure
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        file_list = z.namelist()
        print(f"Files inside ZIP archive: {file_list}")
        assert "index.html" in file_list, "index.html missing from ZIP archive"
        assert "README.md" in file_list, "README.md missing from ZIP archive"
        index_content = z.read("index.html").decode("utf-8")
        assert len(index_content) > 100
        passed += 1
        passed += 1

    # -------------------------------------------------------------
    # 9. Test Error Handling & Edge Cases
    # -------------------------------------------------------------
    print_step("9. Error Handling & Edge Cases")
    total += 2
    # Non-existent project
    r_not_found = requests.get(f"{BASE_BACKEND_URL}/api/projects/non_existent_999", timeout=5)
    assert r_not_found.status_code == 404
    print("Non-existent project returned 404 as expected.")
    passed += 1

    # Non-existent version revert
    r_bad_revert = requests.post(f"{BASE_BACKEND_URL}/api/projects/{project_id}/revert/non_existent_ver", timeout=5)
    assert r_bad_revert.status_code == 404
    print("Non-existent version revert returned 404 as expected.")
    passed += 1

    print_step("TEST RESULTS SUMMARY")
    print(f"Tests Passed: {passed} / {total} ({int(passed/total*100)}%)")
    return passed == total

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
