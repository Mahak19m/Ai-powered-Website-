"""
Streaming generation and refinement API endpoints using Server-Sent Events (SSE).
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.config import settings
from app.core.llm_service import generate_website_stream, refine_website_stream, clean_extracted_html
from app.core.refine_engine import apply_smart_refinement, parse_exact_list_instruction, extract_section_html, validate_exact_list_refinement
from app.api.routes_projects import PROJECTS_STORE, save_project_to_disk, get_project_file_path

from app.core.multi_page_engine import detect_multi_page_request, generate_multi_page_project, refine_multi_page_project

router = APIRouter(prefix="/api", tags=["generation"])

class GenerateRequest(BaseModel):
    prompt: str
    project_id: str | None = None
    project_name: str | None = None
    api_key: str | None = None
    model: str | None = None

class RefineRequest(BaseModel):
    project_id: str
    current_html: str
    instruction: str
    active_page_path: str | None = None
    pages: list[dict] | None = None
    is_multi_page: bool | None = None
    api_key: str | None = None
    model: str | None = None

@router.post("/generate")
async def generate_website(req: GenerateRequest):
    """
    SSE stream for generating a full website from prompt (supports single-page and multi-page projects).
    """
    async def event_generator():
        is_multi, page_descriptors = detect_multi_page_request(req.prompt)
        start_msg = f"Synthesizing {len(page_descriptors)}-page project architecture and styling..." if is_multi else "Synthesizing UI architecture and styling..."
        yield f"event: status\ndata: {json.dumps({'status': 'started', 'message': start_msg})}\n\n"

        accumulated_text = []
        try:
            async for chunk in generate_website_stream(
                prompt=req.prompt,
                api_key=req.api_key,
                model=req.model
            ):
                accumulated_text.append(chunk)
                payload = json.dumps({"chunk": chunk})
                yield f"event: chunk\ndata: {payload}\n\n"

            raw_output = "".join(accumulated_text)
            clean_html = clean_extracted_html(raw_output)

            # Build full page list
            if is_multi:
                pages = generate_multi_page_project(req.prompt, page_descriptors)
                # Primary page html
                if pages:
                    clean_html = pages[0]["html"]
            else:
                pages = [{
                    "name": "Home",
                    "path": "index.html",
                    "html": clean_html
                }]

            # Manage project state
            project_id = req.project_id or str(uuid.uuid4())[:8]
            version_id = str(uuid.uuid4())[:8]
            now = datetime.now().isoformat()

            new_version = {
                "id": version_id,
                "prompt": req.prompt,
                "html_code": clean_html,
                "pages": pages,
                "is_multi_page": is_multi,
                "created_at": now,
                "version_type": "generation"
            }

            if project_id not in PROJECTS_STORE:
                path = get_project_file_path(project_id)
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        PROJECTS_STORE[project_id] = json.load(f)

            if project_id in PROJECTS_STORE:
                proj = PROJECTS_STORE[project_id]
                proj["versions"].append(new_version)
                proj["current_version_id"] = version_id
                proj["updated_at"] = now
            else:
                proj = {
                    "id": project_id,
                    "name": req.project_name or (req.prompt[:30] + "..." if len(req.prompt) > 30 else req.prompt),
                    "created_at": now,
                    "updated_at": now,
                    "current_version_id": version_id,
                    "versions": [new_version]
                }
                PROJECTS_STORE[project_id] = proj

            save_project_to_disk(proj)

            complete_payload = json.dumps({
                "project_id": project_id,
                "version_id": version_id,
                "html": clean_html,
                "prompt": req.prompt,
                "pages": pages,
                "is_multi_page": is_multi,
                "active_page_path": pages[0]["path"] if pages else "index.html"
            })
            yield f"event: complete\ndata: {complete_payload}\n\n"

        except Exception as e:
            err_payload = json.dumps({"error": str(e)})
            yield f"event: error\ndata: {err_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/refine")
async def refine_website(req: RefineRequest):
    """
    SSE stream for iteratively refining existing website HTML (supports single-page and multi-page projects).
    """
    async def event_generator():
        yield f"event: status\ndata: {json.dumps({'status': 'refining', 'message': 'Applying requested modifications...'})}\n\n"

        # Check project state to know if it's multi-page
        project_id = req.project_id
        if project_id not in PROJECTS_STORE:
            path = get_project_file_path(project_id)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    PROJECTS_STORE[project_id] = json.load(f)

        proj = PROJECTS_STORE.get(project_id, {})
        curr_ver = next((v for v in proj.get("versions", []) if v["id"] == proj.get("current_version_id")), None)
        
        is_multi = req.is_multi_page if req.is_multi_page is not None else (curr_ver.get("is_multi_page", False) if curr_ver else False)
        existing_pages = req.pages or (curr_ver.get("pages", []) if curr_ver else [])

        accumulated_text = []
        try:
            if is_multi and existing_pages:
                # Multi-page refinement pipeline
                updated_pages = refine_multi_page_project(
                    pages=existing_pages,
                    instruction=req.instruction,
                    active_page_path=req.active_page_path
                )
                
                # Active page html
                target_path = req.active_page_path or "index.html"
                active_page = next((p for p in updated_pages if p["path"] == target_path), updated_pages[0])
                clean_html = active_page["html"]

                # Simulate streaming of active page html
                wrapped_text = f"```html\n{clean_html}\n```"
                chunk_size = 140
                for i in range(0, len(wrapped_text), chunk_size):
                    chunk = wrapped_text[i:i + chunk_size]
                    yield f"event: chunk\ndata: {json.dumps({'chunk': chunk})}\n\n"
                    await asyncio.sleep(0.005)

                final_pages = updated_pages
            else:
                # Single-page refinement pipeline
                async for chunk in refine_website_stream(
                    current_html=req.current_html,
                    instruction=req.instruction,
                    api_key=req.api_key,
                    model=req.model
                ):
                    accumulated_text.append(chunk)
                    payload = json.dumps({"chunk": chunk})
                    yield f"event: chunk\ndata: {payload}\n\n"

                raw_output = "".join(accumulated_text)
                clean_html = clean_extracted_html(raw_output)

                # Strict validation for exact-list instructions on the final HTML
                is_exact, sec_name, req_items = parse_exact_list_instruction(req.instruction)
                if is_exact and sec_name and req_items:
                    old_sec, _, _ = extract_section_html(req.current_html, sec_name)
                    is_valid, err_msg = validate_exact_list_refinement(clean_html, sec_name, req_items, old_sec)
                    if not is_valid:
                        clean_html = apply_smart_refinement(clean_html, req.instruction)
                        is_valid, err_msg = validate_exact_list_refinement(clean_html, sec_name, req_items, old_sec)
                        if not is_valid:
                            raise ValueError(err_msg)

                final_pages = [{
                    "name": "Home",
                    "path": "index.html",
                    "html": clean_html
                }]

            version_id = str(uuid.uuid4())[:8]
            now = datetime.now().isoformat()

            new_version = {
                "id": version_id,
                "prompt": req.instruction,
                "html_code": clean_html,
                "pages": final_pages,
                "is_multi_page": is_multi,
                "created_at": now,
                "version_type": "refinement"
            }

            if project_id in PROJECTS_STORE:
                proj = PROJECTS_STORE[project_id]
                proj["versions"].append(new_version)
                proj["current_version_id"] = version_id
                proj["updated_at"] = now
                save_project_to_disk(proj)

            complete_payload = json.dumps({
                "project_id": project_id,
                "version_id": version_id,
                "html": clean_html,
                "prompt": req.instruction,
                "pages": final_pages,
                "is_multi_page": is_multi,
                "active_page_path": req.active_page_path or "index.html"
            })
            yield f"event: complete\ndata: {complete_payload}\n\n"

        except Exception as e:
            err_payload = json.dumps({"error": str(e)})
            yield f"event: error\ndata: {err_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
