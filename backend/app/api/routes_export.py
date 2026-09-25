"""
Website export endpoints (single-file HTML download and ZIP package with multi-page support).
"""

import os
import io
import json
import zipfile
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.config import settings
from app.api.routes_projects import PROJECTS_STORE, get_project_file_path

router = APIRouter(prefix="/api/export", tags=["export"])

class ExportHtmlRequest(BaseModel):
    html: str
    filename: str = "index.html"

class ExportProjectRequest(BaseModel):
    project_id: str
    version_id: str | None = None

README_TEMPLATE = """# Exported Website Project

This website was generated with **WebCraft AI**.

## Structure
{structure}

## Quick Start

### 1. Open Directly
Double-click `index.html` to view the website in any modern web browser.

### 2. Local Development Server
Run a local static server to test relative navigation:
```bash
# Using Node.js
npx serve .

# Using Python
python -m http.server 3000
```
Then visit `http://localhost:3000`.

### 3. Free Cloud Deployment
You can drag and drop this entire folder directly to:
- [Netlify Drop](https://app.netlify.com/drop)
- [Vercel](https://vercel.com) (`npx vercel .`)
- [GitHub Pages](https://pages.github.com)

Built with modern HTML5, Tailwind CSS, and Lucide Icons.
"""

@router.post("/html")
def export_html(req: ExportHtmlRequest):
    """Directly download the current HTML code as an attachment."""
    filename = req.filename if req.filename.endswith(".html") else f"{req.filename}.html"
    return Response(
        content=req.html.encode("utf-8"),
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/project/{project_id}/zip")
def export_project_zip(project_id: str, version_id: str | None = None):
    """Bundle the project into a downloadable ZIP archive containing all pages and assets."""
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

    proj = PROJECTS_STORE[project_id]
    target_vid = version_id or proj.get("current_version_id")
    version = next((v for v in proj.get("versions", []) if v["id"] == target_vid), None)

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        file_list_md = []
        if version.get("is_multi_page") and version.get("pages"):
            for page in version["pages"]:
                zip_file.writestr(page["path"], page["html"])
                file_list_md.append(f"- `{page['path']}` — {page['name']} Page")
        else:
            zip_file.writestr("index.html", version["html_code"])
            file_list_md.append("- `index.html` — Main Website")

        structure_text = "\n".join(file_list_md)
        zip_file.writestr("README.md", README_TEMPLATE.format(structure=structure_text))

    zip_buffer.seek(0)
    safe_name = "".join(c for c in proj.get("name", "website") if c.isalnum() or c in ("-", "_")).rstrip()
    if not safe_name:
        safe_name = "website"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.zip"'}
    )
