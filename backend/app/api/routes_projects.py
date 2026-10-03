"""
Project and version management routes.
Supports both single-page and multi-page website projects with full snapshot persistence and rollback.
Backed by the modular SQLAlchemy database layer with fallback disk sync.
"""

import os
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings
from app.db.repository import project_repo

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

# In-memory cache + file sync for backward compatibility
PROJECTS_STORE: dict[str, dict] = {}

def get_project_file_path(project_id: str) -> str:
    return os.path.join(settings.PROJECTS_DIR, f"{project_id}.json")

def save_project_to_disk(project_data: dict):
    path = get_project_file_path(project_data["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

def sync_projects():
    """Initializes and migrates any existing disk projects to DB and cache."""
    project_repo.migrate_from_json()
    for summary in project_repo.list_all():
        pid = summary["id"]
        proj = project_repo.get(pid)
        if proj:
            PROJECTS_STORE[pid] = proj

sync_projects()

class CreateProjectRequest(BaseModel):
    name: str
    initial_prompt: str = "Initial project creation"
    initial_html: str = ""
    pages: list[dict] | None = None
    is_multi_page: bool = False


@router.get("")
def list_projects():
    """Returns a list of all projects summary from database."""
    summaries = project_repo.list_all()
    # Ensure cache is synced
    for s in summaries:
        pid = s["id"]
        if pid not in PROJECTS_STORE:
            proj = project_repo.get(pid)
            if proj:
                PROJECTS_STORE[pid] = proj
    return summaries


@router.get("/{project_id}")
def get_project(project_id: str):
    """Retrieve full project including all versions from database."""
    proj = project_repo.get(project_id)
    if not proj:
        # Fallback to in-memory store or disk
        if project_id in PROJECTS_STORE:
            proj = PROJECTS_STORE[project_id]
        else:
            path = get_project_file_path(project_id)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        proj = json.load(f)
                        PROJECTS_STORE[project_id] = proj
                except Exception:
                    raise HTTPException(status_code=500, detail="Failed to load project from disk")
            else:
                raise HTTPException(status_code=404, detail="Project not found")

    PROJECTS_STORE[project_id] = proj
    return proj


@router.post("")
def create_project(req: CreateProjectRequest):
    """Create a new project with initial version in database."""
    project_data = project_repo.create_project(
        name=req.name,
        initial_prompt=req.initial_prompt,
        initial_html=req.initial_html,
        pages=req.pages,
        is_multi_page=req.is_multi_page
    )
    PROJECTS_STORE[project_data["id"]] = project_data
    return project_data


@router.post("/{project_id}/revert/{version_id}")
def revert_version(project_id: str, version_id: str):
    """Revert current active version to an older snapshot."""
    try:
        project_data = project_repo.revert_version(project_id, version_id)
        PROJECTS_STORE[project_id] = project_data
        return project_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revert version: {str(e)}")


@router.delete("/{project_id}")
def delete_project(project_id: str):
    """Delete a project and all its versions from database and storage."""
    deleted = project_repo.delete_project(project_id)
    PROJECTS_STORE.pop(project_id, None)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "success", "message": f"Project {project_id} deleted"}
