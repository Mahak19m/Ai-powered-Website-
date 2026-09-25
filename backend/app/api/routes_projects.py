"""
Project and version management routes.
Supports both single-page and multi-page website projects with full snapshot persistence and rollback.
"""

import os
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter(prefix="/api/projects", tags=["projects"])

class PageItem(BaseModel):
    name: str
    path: str
    html: str

class Version(BaseModel):
    id: str
    prompt: str
    html_code: str
    pages: list[dict] | None = None
    is_multi_page: bool = False
    created_at: str
    version_type: str = "generation"  # generation or refinement

class Project(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    current_version_id: str
    versions: list[Version]

# In-memory cache + file sync
PROJECTS_STORE: dict[str, dict] = {}

def get_project_file_path(project_id: str) -> str:
    return os.path.join(settings.PROJECTS_DIR, f"{project_id}.json")

def save_project_to_disk(project_data: dict):
    path = get_project_file_path(project_data["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

def load_projects_from_disk():
    if not os.path.exists(settings.PROJECTS_DIR):
        return
    for filename in os.listdir(settings.PROJECTS_DIR):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(settings.PROJECTS_DIR, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    PROJECTS_STORE[data["id"]] = data
            except Exception:
                pass

load_projects_from_disk()

class CreateProjectRequest(BaseModel):
    name: str
    initial_prompt: str
    initial_html: str
    pages: list[dict] | None = None
    is_multi_page: bool = False

@router.get("")
def list_projects():
    """Returns a list of all projects summary."""
    summaries = []
    for pid, proj in PROJECTS_STORE.items():
        curr_ver = next((v for v in proj.get("versions", []) if v["id"] == proj.get("current_version_id")), None)
        is_multi = curr_ver.get("is_multi_page", False) if curr_ver else False
        pages_count = len(curr_ver.get("pages", [])) if (curr_ver and curr_ver.get("pages")) else 1

        summaries.append({
            "id": proj["id"],
            "name": proj["name"],
            "created_at": proj["created_at"],
            "updated_at": proj["updated_at"],
            "versions_count": len(proj.get("versions", [])),
            "current_version_id": proj.get("current_version_id"),
            "is_multi_page": is_multi,
            "pages_count": pages_count
        })
    # Sort by updated_at desc
    summaries.sort(key=lambda x: x["updated_at"], reverse=True)
    return summaries

@router.get("/{project_id}")
def get_project(project_id: str):
    """Retrieve full project including all versions."""
    if project_id not in PROJECTS_STORE:
        path = get_project_file_path(project_id)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    PROJECTS_STORE[project_id] = json.load(f)
            except Exception:
                raise HTTPException(status_code=500, detail="Failed to load project from disk")
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    return PROJECTS_STORE[project_id]

@router.post("")
def create_project(req: CreateProjectRequest):
    """Create a new project with initial version."""
    project_id = str(uuid.uuid4())[:8]
    version_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()

    initial_version = {
        "id": version_id,
        "prompt": req.initial_prompt,
        "html_code": req.initial_html,
        "pages": req.pages,
        "is_multi_page": req.is_multi_page,
        "created_at": now,
        "version_type": "generation"
    }

    project_data = {
        "id": project_id,
        "name": req.name or f"Website #{project_id}",
        "created_at": now,
        "updated_at": now,
        "current_version_id": version_id,
        "versions": [initial_version]
    }

    PROJECTS_STORE[project_id] = project_data
    save_project_to_disk(project_data)
    return project_data

@router.post("/{project_id}/revert/{version_id}")
def revert_version(project_id: str, version_id: str):
    """Revert current active version to an older snapshot."""
    if project_id not in PROJECTS_STORE:
        path = get_project_file_path(project_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                PROJECTS_STORE[project_id] = json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Project not found")

    proj = PROJECTS_STORE[project_id]
    target_version = next((v for v in proj["versions"] if v["id"] == version_id), None)
    if not target_version:
        raise HTTPException(status_code=404, detail="Version not found")

    proj["current_version_id"] = version_id
    proj["updated_at"] = datetime.now().isoformat()
    save_project_to_disk(proj)
    return proj
