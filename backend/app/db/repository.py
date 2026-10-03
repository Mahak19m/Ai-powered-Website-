"""
ProjectRepository: Clean repository pattern abstraction for Project and Version CRUD.
Supports SQLite (default) and PostgreSQL with JSON backward-compatibility and migration.
"""

import os
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal, init_db
from app.db.models import ProjectModel, VersionModel


class ProjectRepository:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
        # Ensure schema tables exist
        init_db()

    def get(self, project_id: str) -> dict | None:
        """Retrieves a full project including all versions by ID."""
        with self.session_factory() as db:
            proj = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
            if proj:
                return proj.to_dict()
        return None

    def list_all(self) -> list[dict]:
        """Lists summaries of all projects sorted by updated_at descending."""
        with self.session_factory() as db:
            projects = (
                db.query(ProjectModel)
                .order_by(ProjectModel.updated_at.desc())
                .all()
            )
            summaries = []
            for p in projects:
                versions = p.versions
                curr_ver = next((v for v in versions if v.id == p.current_version_id), None)
                if not curr_ver and versions:
                    curr_ver = versions[-1]

                is_multi = bool(curr_ver.is_multi_page) if curr_ver else False
                pages_count = 1
                if curr_ver and curr_ver.pages_json:
                    try:
                        pages_list = json.loads(curr_ver.pages_json)
                        if isinstance(pages_list, list) and len(pages_list) > 0:
                            pages_count = len(pages_list)
                    except Exception:
                        pass

                summaries.append({
                    "id": p.id,
                    "name": p.name,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at,
                    "versions_count": len(versions),
                    "current_version_id": p.current_version_id,
                    "is_multi_page": is_multi,
                    "pages_count": pages_count,
                })
            return summaries

    def create_project(
        self,
        name: str,
        initial_prompt: str,
        initial_html: str,
        pages: list[dict] | None = None,
        is_multi_page: bool = False,
        project_id: str | None = None,
    ) -> dict:
        """Creates a new project along with its initial version."""
        pid = project_id or str(uuid.uuid4())[:8]
        vid = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()

        pages_json = json.dumps(pages, ensure_ascii=False) if pages else None

        with self.session_factory() as db:
            # Check if project ID already exists
            existing = db.query(ProjectModel).filter(ProjectModel.id == pid).first()
            if existing:
                return existing.to_dict()

            project = ProjectModel(
                id=pid,
                name=name,
                created_at=now,
                updated_at=now,
                current_version_id=vid,
            )
            version = VersionModel(
                id=vid,
                project_id=pid,
                prompt=initial_prompt,
                html_code=initial_html,
                pages_json=pages_json,
                is_multi_page=is_multi_page,
                version_type="generation",
                created_at=now,
            )
            db.add(project)
            db.add(version)
            db.commit()
            db.refresh(project)
            project_data = project.to_dict()

        # Mirror to disk for backward-compatibility during verification
        self._mirror_to_disk(project_data)
        return project_data

    def add_version(
        self,
        project_id: str,
        prompt: str,
        html_code: str,
        pages: list[dict] | None = None,
        is_multi_page: bool = False,
        version_type: str = "refinement",
    ) -> dict:
        """Adds a new version to an existing project and sets it as current."""
        vid = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        pages_json = json.dumps(pages, ensure_ascii=False) if pages else None

        with self.session_factory() as db:
            project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
            if not project:
                raise ValueError(f"Project with ID '{project_id}' not found.")

            version = VersionModel(
                id=vid,
                project_id=project_id,
                prompt=prompt,
                html_code=html_code,
                pages_json=pages_json,
                is_multi_page=is_multi_page,
                version_type=version_type,
                created_at=now,
            )
            project.current_version_id = vid
            project.updated_at = now
            db.add(version)
            db.commit()
            db.refresh(project)
            full_project = project.to_dict()
            version_data = version.to_dict()

        self._mirror_to_disk(full_project)
        return version_data

    def revert_version(self, project_id: str, version_id: str) -> dict:
        """Reverts current_version_id of the project to a previous version."""
        with self.session_factory() as db:
            project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
            if not project:
                raise ValueError(f"Project with ID '{project_id}' not found.")

            target_version = (
                db.query(VersionModel)
                .filter(VersionModel.project_id == project_id, VersionModel.id == version_id)
                .first()
            )
            if not target_version:
                raise ValueError(f"Version with ID '{version_id}' not found in project '{project_id}'.")

            project.current_version_id = version_id
            project.updated_at = datetime.now().isoformat()
            db.commit()
            db.refresh(project)
            project_data = project.to_dict()

        self._mirror_to_disk(project_data)
        return project_data

    def delete_project(self, project_id: str) -> bool:
        """Deletes a project and all associated versions."""
        with self.session_factory() as db:
            project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
            if not project:
                return False
            db.delete(project)
            db.commit()

        # Remove mirrored file if exists
        file_path = os.path.join(settings.PROJECTS_DIR, f"{project_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return True

    def migrate_from_json(self, json_dir: str = settings.PROJECTS_DIR) -> int:
        """
        Migrates all existing JSON project files into the database.
        Safe to run multiple times: skips projects that are already in the DB.
        """
        if not os.path.exists(json_dir):
            return 0

        migrated_count = 0
        with self.session_factory() as db:
            existing_ids = {p.id for p in db.query(ProjectModel.id).all()}

            for filename in os.listdir(json_dir):
                if not filename.endswith(".json"):
                    continue

                filepath = os.path.join(json_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    pid = data.get("id")
                    if not pid or pid in existing_ids:
                        continue

                    project = ProjectModel(
                        id=pid,
                        name=data.get("name", "Untitled Project"),
                        created_at=data.get("created_at", datetime.now().isoformat()),
                        updated_at=data.get("updated_at", datetime.now().isoformat()),
                        current_version_id=data.get("current_version_id"),
                    )
                    db.add(project)

                    for v_data in data.get("versions", []):
                        vid = v_data.get("id", str(uuid.uuid4())[:8])
                        pages = v_data.get("pages")
                        pages_json = json.dumps(pages, ensure_ascii=False) if pages else None

                        version = VersionModel(
                            id=vid,
                            project_id=pid,
                            prompt=v_data.get("prompt", ""),
                            html_code=v_data.get("html_code", ""),
                            pages_json=pages_json,
                            is_multi_page=bool(v_data.get("is_multi_page", False)),
                            version_type=v_data.get("version_type", "generation"),
                            created_at=v_data.get("created_at", datetime.now().isoformat()),
                        )
                        db.add(version)

                    db.commit()
                    existing_ids.add(pid)
                    migrated_count += 1
                except Exception as e:
                    db.rollback()
                    print(f"Warning: Failed to migrate {filename}: {e}")

        return migrated_count

    def _mirror_to_disk(self, project_data: dict):
        """Mirrors project data to disk storage for fallback preservation."""
        try:
            os.makedirs(settings.PROJECTS_DIR, exist_ok=True)
            path = os.path.join(settings.PROJECTS_DIR, f"{project_data['id']}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


# Default singleton instance
project_repo = ProjectRepository()
