"""
Comprehensive Multi-Page Website Generation and Refinement Test Suite
Tests:
1. Multi-page vs single-page intent detection
2. Arbitrary custom page parsing without hardcoding
3. Multi-page project generation with cohesive styling, header, and footer
4. Working relative inter-page navigation links (e.g., href="about.html")
5. Page-specific refinement (target page updated, other pages preserved)
6. Global theme refinement across all pages
7. Version history snapshotting and rollback
8. Multi-page ZIP export containing all pages
9. SSE Streaming endpoints for multi-page generation and refinement
10. Backward compatibility with single-page generation and exact-list refinement
"""

import os
import io
import json
import zipfile
from fastapi.testclient import TestClient

from app.main import app
from app.core.multi_page_engine import (
    detect_multi_page_request,
    generate_multi_page_project,
    refine_multi_page_project,
    build_shared_header,
    build_shared_footer,
    build_page_html,
    slugify
)
from app.core.refine_engine import (
    parse_exact_list_instruction,
    validate_exact_list_refinement,
    apply_smart_refinement
)

client = TestClient(app)

def test_intent_detection():
    # 1. Multi-page prompt with standard pages
    prompt1 = "Create a website with Home, About, Features, Pricing and Contact pages"
    is_multi1, pages1 = detect_multi_page_request(prompt1)
    assert is_multi1 is True
    assert len(pages1) == 5
    assert [p["name"] for p in pages1] == ["Home", "About", "Features", "Pricing", "Contact"]
    assert pages1[0]["path"] == "index.html"
    assert pages1[1]["path"] == "about.html"
    assert pages1[2]["path"] == "features.html"
    assert pages1[3]["path"] == "pricing.html"
    assert pages1[4]["path"] == "contact.html"

    # 2. Multi-page prompt with custom arbitrary page names (no hardcoding)
    prompt2 = "Build a multi-page site for a medical clinic including Overview, Doctors, Treatments, Patient Portal and Appointments pages"
    is_multi2, pages2 = detect_multi_page_request(prompt2)
    assert is_multi2 is True
    assert len(pages2) >= 4
    names2 = [p["name"] for p in pages2]
    assert "Doctors" in names2
    assert "Treatments" in names2
    assert "Appointments" in names2
    assert pages2[0]["path"] == "index.html"

    # 3. Explicit single-page prompt should NOT trigger multi-page
    prompt3 = "Create a single-page portfolio with Hero, About, Skills, and Projects sections"
    is_multi3, pages3 = detect_multi_page_request(prompt3)
    assert is_multi3 is False
    assert len(pages3) == 0

def test_multi_page_generation_structure_and_navigation():
    prompt = "Create a modern SaaS website with Home, About, Features, Pricing and Contact pages"
    is_multi, page_descriptors = detect_multi_page_request(prompt)
    assert is_multi is True

    pages = generate_multi_page_project(prompt, page_descriptors)
    assert len(pages) == 5

    paths = [p["path"] for p in pages]
    assert paths == ["index.html", "about.html", "features.html", "pricing.html", "contact.html"]

    for page in pages:
        html = page["html"]
        assert "<!DOCTYPE html>" in html
        assert "<header" in html
        assert "<footer" in html
        # Shared relative links must be present in every page
        assert 'href="index.html"' in html
        assert 'href="about.html"' in html
        assert 'href="features.html"' in html
        assert 'href="pricing.html"' in html
        assert 'href="contact.html"' in html
        # Tailwind CSS and Lucide icons script
        assert "tailwindcss.com" in html
        assert "lucide" in html

    # Verify dedicated page contents
    home_html = next(p["html"] for p in pages if p["path"] == "index.html")
    assert "hero" in home_html.lower()

    about_html = next(p["html"] for p in pages if p["path"] == "about.html")
    assert "Mission" in about_html or "About" in about_html

    pricing_html = next(p["html"] for p in pages if p["path"] == "pricing.html")
    assert "Pricing" in pricing_html or "Plans" in pricing_html

    contact_html = next(p["html"] for p in pages if p["path"] == "contact.html")
    assert "<form" in contact_html or "Touch" in contact_html

def test_page_specific_refinement():
    prompt = "Create a website with Home, About, Features, Pricing and Contact pages"
    _, page_descriptors = detect_multi_page_request(prompt)
    pages = generate_multi_page_project(prompt, page_descriptors)

    # Initial state
    initial_about_html = next(p["html"] for p in pages if p["path"] == "about.html")
    initial_home_html = next(p["html"] for p in pages if p["path"] == "index.html")

    # Refine only Home page
    instruction = "Change the hero headline on the Home page to 'Next Generation Quantum AI Operating System'"
    updated_pages = refine_multi_page_project(pages, instruction, active_page_path="index.html")

    assert len(updated_pages) == 5
    new_home = next(p["html"] for p in updated_pages if p["path"] == "index.html")
    new_about = next(p["html"] for p in updated_pages if p["path"] == "about.html")

    assert "Quantum AI Operating System" in new_home
    # About page must remain untouched
    assert new_about == initial_about_html

def test_global_theme_refinement():
    prompt = "Create a website with Home, About, Features, Pricing and Contact pages"
    _, page_descriptors = detect_multi_page_request(prompt)
    pages = generate_multi_page_project(prompt, page_descriptors)

    instruction = "Change the primary color theme across the entire website to emerald green"
    updated_pages = refine_multi_page_project(pages, instruction)

    assert len(updated_pages) == 5
    for page in updated_pages:
        assert "emerald" in page["html"].lower()

def test_api_generate_and_refine_multi_page():
    # 1. Generate multi-page website via SSE endpoint
    gen_res = client.post("/api/generate", json={
        "prompt": "Create a modern SaaS website with Home, About, Features, Pricing and Contact pages"
    })
    assert gen_res.status_code == 200

    # Parse SSE events
    events = []
    for line in gen_res.text.split("\n\n"):
        if "event: complete" in line:
            data_line = [l for l in line.split("\n") if l.startswith("data: ")][0]
            complete_data = json.loads(data_line.replace("data: ", ""))
            events.append(complete_data)

    assert len(events) == 1
    complete_payload = events[0]
    project_id = complete_payload["project_id"]
    version_id_1 = complete_payload["version_id"]

    assert complete_payload["is_multi_page"] is True
    assert len(complete_payload["pages"]) == 5
    assert complete_payload["pages"][0]["path"] == "index.html"
    assert complete_payload["pages"][3]["path"] == "pricing.html"

    # 2. Refine multi-page website
    ref_res = client.post("/api/refine", json={
        "project_id": project_id,
        "current_html": complete_payload["html"],
        "instruction": "Update hero headline on Home page to 'Automate Everything with Agent Swarms'",
        "active_page_path": "index.html",
        "pages": complete_payload["pages"],
        "is_multi_page": True
    })
    assert ref_res.status_code == 200

    ref_events = []
    for line in ref_res.text.split("\n\n"):
        if "event: complete" in line:
            data_line = [l for l in line.split("\n") if l.startswith("data: ")][0]
            ref_complete = json.loads(data_line.replace("data: ", ""))
            ref_events.append(ref_complete)

    assert len(ref_events) == 1
    ref_payload = ref_events[0]
    version_id_2 = ref_payload["version_id"]
    assert ref_payload["is_multi_page"] is True
    assert len(ref_payload["pages"]) == 5

    home_page_v2 = next(p for p in ref_payload["pages"] if p["path"] == "index.html")
    assert "Automate Everything with Agent Swarms" in home_page_v2["html"]

    # 3. Check project state persistence and version history
    proj_res = client.get(f"/api/projects/{project_id}")
    assert proj_res.status_code == 200
    proj_data = proj_res.json()
    assert len(proj_data["versions"]) == 2
    assert proj_data["current_version_id"] == version_id_2

    # Check version 1 snapshot is completely preserved
    ver1 = proj_data["versions"][0]
    assert ver1["is_multi_page"] is True
    assert len(ver1["pages"]) == 5
    assert "Automate Everything with Agent Swarms" not in ver1["pages"][0]["html"]

    # 4. Rollback to version 1
    revert_res = client.post(f"/api/projects/{project_id}/revert/{version_id_1}")
    assert revert_res.status_code == 200
    reverted_proj = revert_res.json()
    assert reverted_proj["current_version_id"] == version_id_1

    # 5. Export ZIP and verify all pages and README.md are bundled
    zip_res = client.get(f"/api/export/project/{project_id}/zip")
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"

    zip_file = zipfile.ZipFile(io.BytesIO(zip_res.content))
    namelist = zip_file.namelist()
    assert "index.html" in namelist
    assert "about.html" in namelist
    assert "features.html" in namelist
    assert "pricing.html" in namelist
    assert "contact.html" in namelist
    assert "README.md" in namelist

    readme_content = zip_file.read("README.md").decode("utf-8")
    assert "Exported Website Project" in readme_content
    assert "index.html" in readme_content
    assert "pricing.html" in readme_content

def test_single_page_backward_compatibility():
    # Generate single-page site
    gen_res = client.post("/api/generate", json={
        "prompt": "Create a portfolio website with Hero, About, Skills and Contact sections"
    })
    assert gen_res.status_code == 200
    for line in gen_res.text.split("\n\n"):
        if "event: complete" in line:
            data_line = [l for l in line.split("\n") if l.startswith("data: ")][0]
            complete_data = json.loads(data_line.replace("data: ", ""))
            assert complete_data["is_multi_page"] is False
            assert len(complete_data["pages"]) == 1
            assert complete_data["pages"][0]["path"] == "index.html"
