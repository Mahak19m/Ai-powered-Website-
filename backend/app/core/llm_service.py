"""
LLM Service for streaming website code generation using Google Gemini API.
Includes dynamic template generation, multi-page project synthesis, generalized section refinement, and exact-list validation.
"""

import asyncio
import logging
import re
from typing import AsyncGenerator
from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT, REFINE_SYSTEM_PROMPT, get_generation_prompt, get_refine_prompt
from app.core.mock_templates import get_matching_mock_template
from app.core.refine_engine import apply_smart_refinement, parse_exact_list_instruction, extract_section_html, validate_exact_list_refinement
from app.core.multi_page_engine import detect_multi_page_request, generate_multi_page_project, refine_multi_page_project

logger = logging.getLogger("llm_service")

def clean_extracted_html(text: str) -> str:
    """Extract HTML code block if wrapped in markdown ```html ... ``` or ``` ... ```."""
    html_match = re.search(r"```(?:html)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if html_match:
        return html_match.group(1).strip()
    return text.strip()

async def stream_mock_response(template_html: str, chunk_size: int = 140) -> AsyncGenerator[str, None]:
    """Simulates realistic streaming chunks for mock/demo mode."""
    wrapped_text = f"```html\n{template_html}\n```"
    total_len = len(wrapped_text)
    for i in range(0, total_len, chunk_size):
        chunk = wrapped_text[i:i + chunk_size]
        yield chunk
        await asyncio.sleep(0.01)

async def generate_website_stream(
    prompt: str,
    api_key: str | None = None,
    model: str | None = None
) -> AsyncGenerator[str, None]:
    """
    Streams generated website HTML chunk by chunk (for single-page or multi-page primary page).
    """
    effective_key = api_key or settings.GEMINI_API_KEY
    chosen_model = model or settings.DEFAULT_MODEL

    # Check if multi-page request
    is_multi, page_descriptors = detect_multi_page_request(prompt)

    if not effective_key:
        logger.info(f"Generating website (multi_page={is_multi}) via dynamic generator.")
        if is_multi:
            pages = generate_multi_page_project(prompt, page_descriptors)
            primary_html = pages[0]["html"]
            async for chunk in stream_mock_response(primary_html):
                yield chunk
        else:
            mock_html = get_matching_mock_template(prompt)
            async for chunk in stream_mock_response(mock_html):
                yield chunk
        return

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=effective_key)
        full_user_prompt = get_generation_prompt(prompt)

        response_stream = client.models.generate_content_stream(
            model=chosen_model,
            contents=full_user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
        )

        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
                await asyncio.sleep(0.005)

    except Exception as e:
        logger.error(f"Gemini API generation failed: {e}", exc_info=True)
        raise RuntimeError(f"Gemini API generation failed ({type(e).__name__}): {str(e)}")

async def refine_website_stream(
    current_html: str,
    instruction: str,
    api_key: str | None = None,
    model: str | None = None
) -> AsyncGenerator[str, None]:
    """
    Streams refined website HTML chunk by chunk based on user instruction.
    Applies strict exact-list replacement and post-refinement validation.
    """
    effective_key = api_key or settings.GEMINI_API_KEY
    chosen_model = model or settings.DEFAULT_MODEL

    if not effective_key:
        logger.info("Applying smart refinement engine.")
        updated_html = apply_smart_refinement(current_html, instruction)
        async for chunk in stream_mock_response(updated_html):
            yield chunk
        return

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=effective_key)
        full_refine_prompt = get_refine_prompt(current_html, instruction)

        response_stream = client.models.generate_content_stream(
            model=chosen_model,
            contents=full_refine_prompt,
            config=types.GenerateContentConfig(
                system_instruction=REFINE_SYSTEM_PROMPT,
                temperature=0.3,
            )
        )

        accumulated = []
        for chunk in response_stream:
            if chunk.text:
                accumulated.append(chunk.text)
                yield chunk.text
                await asyncio.sleep(0.005)

        # Post-generation exact-list validation
        full_raw = "".join(accumulated)
        clean_result = clean_extracted_html(full_raw)
        is_exact, section_name, items = parse_exact_list_instruction(instruction)
        if is_exact and section_name and items:
            old_sec, _, _ = extract_section_html(current_html, section_name)
            valid, err_msg = validate_exact_list_refinement(clean_result, section_name, items, old_sec)
            if not valid:
                logger.error(f"AI refinement failed exact list validation: {err_msg}")
                raise ValueError(err_msg)

    except Exception as e:
        logger.error(f"Gemini API refine failed: {e}", exc_info=True)
        raise RuntimeError(f"Gemini API refine failed ({type(e).__name__}): {str(e)}")
