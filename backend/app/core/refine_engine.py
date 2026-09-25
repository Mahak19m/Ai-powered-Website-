"""
Generalized Section Refinement & Validation Engine
Handles arbitrary exact-list replacements, targeted section mutations, and strict post-refinement validation.
"""

import re
import logging

logger = logging.getLogger("refine_engine")

SECTION_ALIASES = {
    "skills": ["skills", "skill", "technologies", "tech stack", "technical skills", "competencies", "tools", "languages & frameworks", "tech proficiency"],
    "projects": ["projects", "project", "portfolio", "featured work", "work", "implementations"],
    "education": ["education", "academic", "academics", "qualifications", "degree", "academic background"],
    "experience": ["experience", "career", "employment", "internships", "jobs", "career journey"],
    "about": ["about", "about me", "bio", "background", "story"],
    "features": ["features", "feature", "capabilities", "services", "key features"],
    "pricing": ["pricing", "plans", "tiers", "pricing plans", "subscription"],
    "contact": ["contact", "get in touch", "reach out", "contact me", "connect"],
    "nav": ["navigation", "navbar", "nav links", "menu", "header links", "navigation links", "links"],
    "faq": ["faq", "faqs", "questions", "frequently asked questions"]
}

TECH_ICONS = {
    "python": "code",
    "java": "coffee",
    "fastapi": "zap",
    "postgresql": "database",
    "postgres": "database",
    "sql": "database",
    "mysql": "database",
    "mongodb": "database",
    "machine learning": "brain",
    "ml": "brain",
    "ai": "cpu",
    "deep learning": "brain",
    "react": "atom",
    "vue": "layout",
    "angular": "shield",
    "next.js": "globe",
    "node.js": "server",
    "docker": "container",
    "kubernetes": "layers",
    "k8s": "layers",
    "git": "git-branch",
    "linux": "terminal",
    "typescript": "file-code",
    "javascript": "file-code",
    "rust": "shield",
    "go": "zap",
    "golang": "zap",
    "graphql": "share-2",
    "c++": "terminal",
    "c#": "code",
    "c / c++": "terminal",
    "aws": "cloud",
    "gcp": "cloud",
    "azure": "cloud",
    "tailwind": "palette",
    "pytorch": "flame",
    "tensorflow": "cpu",
    "redis": "database",
    "rest api": "network",
    "microservices": "boxes",
    "ci/cd": "refresh-cw",
    "devops": "wrench"
}

def resolve_section_name(raw_name: str) -> str:
    """Maps a user-mentioned section phrase to a canonical section ID."""
    clean = raw_name.lower().strip()
    for canonical, aliases in SECTION_ALIASES.items():
        if any(a in clean for a in aliases):
            return canonical
    return clean

def parse_items_list(text: str) -> list[str]:
    """
    Parses arbitrary delimited item strings into a clean list of individual items.
    Handles delimiters: commas, 'and', '&', bullets, newlines, tabs, slashes.
    """
    cleaned = text.strip().strip("'\"").strip()
    cleaned = re.sub(r"\s+(?:and|&)\s+", ", ", cleaned, flags=re.IGNORECASE)
    parts = re.split(r"[,•\n\r\t]+", cleaned)
    
    items = []
    stop_phrases = [
        "do not add any other technical skills",
        "do not add any other skills",
        "do not add any other",
        "do not add other technical skills",
        "do not add other skills",
        "do not add other",
        "do not add",
        "do not change any other section",
        "do not change other sections",
        "do not change",
        "do not invent",
        "do not modify",
        "none other",
        "no other technical skills",
        "no other skills",
        "no other",
        "only include",
        "technical skills",
        "skills",
        "etc"
    ]
    
    for p in parts:
        item = p.strip().strip("'\"").strip(".:;-* \t\n\r")
        if not item:
            continue
        for stop in stop_phrases:
            if stop in item.lower():
                item = re.split(re.escape(stop), item, flags=re.IGNORECASE)[0].strip().strip("'\"").strip(".:;-* \t\n\r")
        # Remove trailing standalone words like 'only' or 'exclusively'
        item = re.sub(r"\b(only|exclusively)\b", "", item, flags=re.IGNORECASE).strip().strip("'\"").strip(".:;-* \t\n\r")
        if item and len(item) > 1 and item.lower() not in ["and", "or", "&", "the", "with"]:
            items.append(item)
            
    return items

def parse_exact_list_instruction(instruction: str) -> tuple[bool, str | None, list[str]]:
    """
    Detects if an instruction is an exact-list replacement request for an arbitrary section.
    Returns: (is_exact_list, section_name, list_of_items)
    """
    inst = instruction.strip()
    inst_lower = inst.lower()

    has_exact_intent = any(k in inst_lower for k in [
        "exactly", "only", "do not add any other", "do not add other", "replace the",
        "set the", "set ", "limit to", "exclusively", "restrict to", "no other",
        "change the", "update the", "should be", "must be", "to be exactly"
    ])

    if not has_exact_intent:
        return False, None, []

    patterns = [
        # "Set the Skills section to exactly: Python, Java..."
        r"(?:set|replace|change|update)\s+(?:the\s+)?([\w\s]+?)\s*(?:section)?\s*(?:to|with|as)\s*(?:exactly|only)?\s*[:\s]*([\s\S]+?)(?:\.\s*do not|\.\s*no other|\n\s*do not|\n\s*no other|\n\s*do not add|$|\.|\!)",
        # "Skills section to be exactly: Python, Java..."
        r"(?:the\s+)?([\w\s]+?)\s*(?:section)?\s*(?:to|should be|must be|is)\s*(?:exactly|only)?\s*[:\s]*([\s\S]+?)(?:\.\s*do not|\.\s*no other|\n\s*do not|\n\s*no other|$|\.|\!)",
        # "Only include ... in skills"
        r"(?:only|exactly)\s+(?:include|have|show|list)\s+([\s\S]+?)\s+in\s+(?:the\s+)?([\w\s]+?)(?:section|\.|$|\n)",
    ]

    for pat in patterns:
        m = re.search(pat, inst, re.IGNORECASE)
        if m:
            groups = m.groups()
            if len(groups) == 2:
                g0_sec = resolve_section_name(groups[0])
                if g0_sec in SECTION_ALIASES:
                    sec_cand = g0_sec
                    items_cand = parse_items_list(groups[1])
                else:
                    g1_sec = resolve_section_name(groups[1])
                    if g1_sec in SECTION_ALIASES:
                        sec_cand = g1_sec
                        items_cand = parse_items_list(groups[0])
                    else:
                        sec_cand = g0_sec
                        items_cand = parse_items_list(groups[1])
                
                if items_cand:
                    return True, sec_cand, items_cand

    for canonical, aliases in SECTION_ALIASES.items():
        if any(a in inst_lower for a in aliases):
            for alias in aliases:
                m_list = re.search(rf"{alias}\s*(?:section)?\s*(?:to|is|with|as|should be|must be)?\s*(?:exactly|only)?\s*[:\s]*([\s\S]+?)(?:\.\s*do not|\n\s*do not|\n\s*no other|$|\.|\!)", inst, re.IGNORECASE)
                if m_list:
                    items = parse_items_list(m_list.group(1))
                    if items:
                        return True, canonical, items

    return False, None, []

def extract_section_html(html_code: str, section_name: str) -> tuple[str | None, int, int]:
    """Finds and extracts the full HTML block of a target section or navigation element."""
    if section_name in ["nav", "navigation", "navbar"]:
        m = re.search(r'(<nav[^>]*>[\s\S]*?</nav>)', html_code, re.IGNORECASE)
        if m:
            return m.group(1), m.start(1), m.end(1)

    patterns = [
        rf'(<section[^>]*id=["\']{section_name}["\'][^>]*>[\s\S]*?</section>)',
        rf'(<section[^>]*class=["\'][^"\']*{section_name}[^"\']*["\'][^>]*>[\s\S]*?</section>)',
        rf'(<section[^>]*>[\s\S]*?<h[23][^>]*>[^<]*{section_name}[^<]*</h[23]>[\s\S]*?</section>)'
    ]
    for pat in patterns:
        m = re.search(pat, html_code, re.IGNORECASE)
        if m:
            return m.group(1), m.start(1), m.end(1)
    return None, -1, -1

def detect_color_theme(html_code: str) -> str:
    """Detect primary accent color from HTML classes."""
    for color in ["emerald", "indigo", "blue", "cyan", "violet", "purple", "rose", "teal", "sky", "amber"]:
        if f"{color}-500" in html_code or f"{color}-400" in html_code or f"{color}-600" in html_code:
            return color
    return "emerald"

def build_exact_skills_html(items: list[str], old_section_html: str | None = None, full_html: str = "") -> str:
    """Generates clean, modern Tailwind markup containing ONLY the exact requested skills while preserving existing section styling."""
    accent = detect_color_theme(old_section_html or full_html)
    
    # Preserve existing header block if present in old_section_html
    header_html = None
    if old_section_html:
        m_head = re.search(r'(<div[^>]*class=["\'][^"\']*text-center[^"\']*["\'][^>]*>[\s\S]*?</div>)', old_section_html, re.IGNORECASE)
        if m_head:
            header_html = m_head.group(1)

    if not header_html:
        header_html = f"""      <div class="text-center max-w-2xl mx-auto mb-12">
        <h2 class="text-xs font-bold text-{accent}-400 uppercase tracking-widest font-mono mb-2">Technical Proficiency</h2>
        <h3 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Core Technical Skills</h3>
      </div>"""

    # Choose responsive grid layout
    grid_cols = "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3" if len(items) <= 6 else "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4"

    badge_cards = []
    for item in items:
        icon_name = TECH_ICONS.get(item.lower().strip(), "check-circle-2")
        badge_cards.append(f"""        <div class="p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-{accent}-500/40 transition flex items-center gap-3.5 shadow-sm">
          <div class="w-10 h-10 rounded-xl bg-{accent}-950/70 border border-{accent}-500/30 flex items-center justify-center text-{accent}-400 flex-shrink-0">
            <i data-lucide="{icon_name}" class="w-5 h-5"></i>
          </div>
          <div>
            <span class="text-sm font-bold text-white block">{item}</span>
            <span class="text-[10px] font-mono text-{accent}-400">Technical Skill</span>
          </div>
        </div>""")

    cards_markup = "\n".join(badge_cards)

    return f"""  <!-- Skills Section -->
  <section id="skills" class="py-16 border-t border-slate-900 bg-slate-900/30">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
{header_html}

      <div class="grid {grid_cols} gap-5 max-w-4xl mx-auto">
{cards_markup}
      </div>
    </div>
  </section>"""

def build_exact_nav_html(links: list[str], old_nav_html: str | None = None, full_html: str = "") -> str:
    """Generates clean nav element for exact navigation links while preserving layout and styles."""
    accent = detect_color_theme(old_nav_html or full_html)
    link_tags = []
    for link in links:
        slug = link.lower().replace(" ", "-")
        link_tags.append(f'<a href="#{slug}" class="hover:text-{accent}-400 transition">{link}</a>')
    links_str = "\n        ".join(link_tags)
    return f"""<nav class="hidden md:flex items-center gap-6 text-xs font-medium text-slate-400">
        {links_str}
      </nav>"""

def build_exact_features_html(items: list[str], old_section_html: str | None = None, full_html: str = "") -> str:
    """Generates clean features grid containing only requested features."""
    accent = detect_color_theme(old_section_html or full_html)
    cards = []
    default_icons = ["cpu", "shield-check", "zap", "gauge", "layers", "sparkles", "database", "globe"]
    for i, item in enumerate(items):
        icon = default_icons[i % len(default_icons)]
        cards.append(f"""        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-{accent}-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="{icon}" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">{item}</h4>
          <p class="text-slate-400 text-sm leading-relaxed">High-performance capability engineered for precision, reliability and production scale.</p>
        </div>""")
    cards_str = "\n".join(cards)
    return f"""  <!-- Features Section -->
  <section id="features" class="py-24 bg-slate-900/50 border-t border-slate-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-3xl mx-auto mb-16">
        <h2 class="text-xs font-bold text-{accent}-400 uppercase tracking-widest mb-3">Core Capabilities</h2>
        <h3 class="text-3xl sm:text-4xl font-bold text-white tracking-tight">Engineered for Maximum Velocity</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
{cards_str}
      </div>
    </div>
  </section>"""

def build_generalized_section_html(section_name: str, items: list[str], old_section_html: str | None = None, full_html: str = "") -> str:
    """Dispatches to appropriate section builder preserving design consistency."""
    if section_name == "skills":
        return build_exact_skills_html(items, old_section_html, full_html)
    elif section_name in ["nav", "navigation", "navbar"]:
        return build_exact_nav_html(items, old_section_html, full_html)
    elif section_name == "features":
        return build_exact_features_html(items, old_section_html, full_html)
    else:
        accent = detect_color_theme(old_section_html or full_html)
        cards = []
        for item in items:
            cards.append(f"""        <div class="p-6 rounded-2xl bg-slate-900 border border-slate-800">
          <h4 class="text-lg font-bold text-white mb-2">{item}</h4>
          <p class="text-sm text-slate-400">Validated component for {section_name}.</p>
        </div>""")
        cards_str = "\n".join(cards)
        return f"""  <!-- {section_name.title()} Section -->
  <section id="{section_name}" class="py-16 border-t border-slate-900">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-2xl mx-auto mb-12">
        <h2 class="text-xs font-bold text-{accent}-400 uppercase tracking-widest font-mono mb-2">{section_name.title()}</h2>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
{cards_str}
      </div>
    </div>
  </section>"""

def replace_section_in_html(current_html: str, section_name: str, new_section_html: str, items: list[str] | None = None) -> str:
    """Replaces target section in full HTML document while preserving all other markup."""
    updated = current_html
    if section_name in ["nav", "navigation", "navbar"]:
        old_sec, start, end = extract_section_html(updated, section_name)
        if old_sec:
            updated = updated[:start] + new_section_html + updated[end:]
        # Synchronize mobile drawer links if present
        if items and 'id="mobile-menu"' in updated:
            accent = detect_color_theme(updated)
            mob_links = []
            for link in items:
                slug = link.lower().replace(" ", "-")
                mob_links.append(f'<a href="#{slug}" class="block py-1.5 text-slate-300 hover:text-{accent}-400">{link}</a>')
            mob_str = "\n      ".join(mob_links)
            updated = re.sub(
                r'(<div id="mobile-menu"[^>]*>)([\s\S]*?)(</div>)',
                rf'\1\n      {mob_str}\n    \3',
                updated
            )
        return updated

    old_sec, start, end = extract_section_html(updated, section_name)
    if old_sec:
        return updated[:start] + new_section_html + updated[end:]

    # Fallback placement if section was not previously in document
    if '<section id="projects"' in updated:
        return updated.replace('<section id="projects"', f'{new_section_html}\n\n  <section id="projects"')
    elif '<section id="contact"' in updated:
        return updated.replace('<section id="contact"', f'{new_section_html}\n\n  <section id="contact"')
    elif '</body>' in updated:
        return updated.replace('</body>', f'{new_section_html}\n</body>')
    return updated + "\n" + new_section_html

def validate_exact_list_refinement(
    html_code: str,
    section_name: str,
    requested_items: list[str],
    old_section_html: str | None = None
) -> tuple[bool, str]:
    """
    Validation step for exact-list refinements:
    1. Extracts target section from resulting HTML.
    2. Verifies all requested items exist in the section.
    3. Verifies prohibited/old items are NOT present in that section.
    """
    sec_html, _, _ = extract_section_html(html_code, section_name)
    if not sec_html:
        return False, f"Section '{section_name}' missing from resulting HTML."

    sec_lower = sec_html.lower()

    # 1. Verify all requested items exist
    missing = [item for item in requested_items if item.lower() not in sec_lower]
    if missing:
        return False, f"Validation failed: Requested item(s) {missing} not found in {section_name} section."

    # 2. Extract potential old items from old section HTML
    if old_section_html:
        noise = {
            "div", "span", "section", "class", "text", "bg", "border", "rounded", "font", "py", "px",
            "id", "lucide", "data", "flex", "grid", "p", "h1", "h2", "h3", "h4", "svg", "i", "a", "href",
            "technical", "competencies", "skills", "proficiency", "verified", "verified proficiency",
            "core", "core technical skills", "featured", "languages", "backend", "frontend", "tools",
            "infra", "frameworks", "services", "overview", "section", "stack", "list", "items",
            "and", "with", "for", "all", "more", "view", "active", "skill"
        }
        stripped_old = re.sub(r"<h[1-4][^>]*>[\s\S]*?</h[1-4]>", "", old_section_html, flags=re.IGNORECASE)
        raw_tokens = re.findall(r">([^<]+)<", stripped_old)
        old_words = set()
        for t in raw_tokens:
            for phrase in re.split(r"[,/•\n\t]+", t):
                cleaned_p = phrase.strip().strip(".:;\"'")
                if cleaned_p and len(cleaned_p) > 1 and cleaned_p.lower() not in noise:
                    words = [w.lower() for w in cleaned_p.split()]
                    if not all(w in noise for w in words):
                        old_words.add(cleaned_p)

        req_lower_set = {r.lower() for r in requested_items}
        prohibited = []
        for ow in old_words:
            if ow.lower() not in req_lower_set and not any(r in ow.lower() for r in req_lower_set):
                if len(ow) > 2 and re.search(rf"\b{re.escape(ow)}\b", sec_html, re.IGNORECASE):
                    prohibited.append(ow)

        if prohibited:
            return False, f"Validation failed: Prohibited unrequested items {prohibited[:5]} are still present in {section_name} section."

    return True, "Validation successful"

def apply_smart_refinement(current_html: str, instruction: str) -> str:
    """
    Main entry point for smart section refinement.
    Handles exact-list replacement, heading changes, color modifications, and validation.
    """
    updated = current_html
    inst = instruction.strip()

    # 1. Exact-list replacement detection
    is_exact, section_name, items = parse_exact_list_instruction(inst)
    if is_exact and section_name and items:
        logger.info(f"Exact-list replacement detected for section '{section_name}': {items}")
        old_sec, _, _ = extract_section_html(current_html, section_name)
        new_sec = build_generalized_section_html(section_name, items, old_sec, current_html)
        updated = replace_section_in_html(updated, section_name, new_sec, items)
        
        # Run validation step
        valid, msg = validate_exact_list_refinement(updated, section_name, items, old_sec)
        if not valid:
            logger.error(f"Validation error: {msg}")
            raise ValueError(msg)

    # 2. Hero heading replacement
    heading_quotes_match = re.search(r"(?:heading|title|headline|text)\b.*?(?:to|as|be|should be)\s+['\"]([^'\"]+)['\"]", inst, re.IGNORECASE)
    if heading_quotes_match:
        new_heading = heading_quotes_match.group(1).strip()
        h1_pattern = re.compile(r"(<h1[^>]*>)([\s\S]*?)(</h1>)", re.IGNORECASE)
        if h1_pattern.search(updated):
            updated = h1_pattern.sub(rf"\1{new_heading}\3", updated)

    # 3. Clean invented names if requested
    if any(k in inst.lower() for k in ["invent", "name", "remove"]):
        replacements = [
            ("Elena Vance", "Computer Science Developer"),
            ("elena.design", "dev.ai"),
            ("Available for Q4 Consulting & Advisory", "Open for Software Engineering Opportunities"),
            ("Aether Capital", "Autonomous Task Engine"),
            ("Chronos AI", "Neural Vision Core"),
            ("hello@elenavance.design", "contact@example.com")
        ]
        for old, new in replacements:
            updated = updated.replace(old, new)

    # 4. Color adjustments
    if "emerald" in inst.lower():
        updated = updated.replace("indigo-600", "emerald-600").replace("indigo-500", "emerald-500").replace("indigo-400", "emerald-400")
    elif "cyan" in inst.lower() or "blue" in inst.lower():
        updated = updated.replace("emerald-600", "cyan-600").replace("emerald-500", "cyan-500").replace("emerald-400", "cyan-400")

    return updated
