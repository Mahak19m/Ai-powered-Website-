"""
Multi-Page Website Engine for WebCraft AI
Handles:
- Intelligent detection of multi-page vs single-page intent from prompts
- Arbitrary page extraction and slug/path resolution
- Cohesive multi-page project generation with shared design systems, navigation, and footers
- Dedicated page layouts (Home, About, Features, Pricing, Contact, Blog, Docs, Portfolio, etc.)
- Working relative inter-page navigation links
- Page-specific and global theme/shared-element refinement
"""

import re
import logging
from app.core.refine_engine import apply_smart_refinement, detect_color_theme

logger = logging.getLogger("multi_page_engine")

def slugify(text: str) -> str:
    """Converts page name to safe filename slug."""
    clean = re.sub(r"[^\w\s-]", "", text.strip().lower())
    clean = re.sub(r"[\s_-]+", "-", clean).strip("-")
    return clean or "page"

def detect_multi_page_request(prompt: str) -> tuple[bool, list[dict]]:
    """
    Detects whether the user prompt requests a multi-page website and extracts page names.
    Returns: (is_multi_page, list_of_page_descriptors)
    Each descriptor: {"name": "Home", "path": "index.html", "slug": "home"}
    """
    p = prompt.strip()
    p_lower = p.lower()

    if any(k in p_lower for k in ["single page", "single-page", "one-page", "one page", "single page website", "single-page website"]):
        return False, []

    multi_page_indicators = [
        "page", "pages", "multi-page", "multipage", "multi page", "separate pages", "subpages", "sub-pages"
    ]
    if not any(k in p_lower for k in multi_page_indicators):
        return False, []

    patterns = [
        # "multi-page website with Home, Docs, Pricing, About and Contact"
        r"(?:multi-page|multipage|multi page)\s+(?:website|site|app)?\s*(?:with|featuring|including|having)?\s+([A-Za-z0-9\s,\/•&–-]+?)(?:\.|\n\n|\n[A-Z]|$)",
        # "Include Home, About, Features, Pricing and Contact pages" / "with ... pages"
        r"(?:with|include|includes|including|consisting of|having|contain|contains|feature|features)\s+([A-Za-z0-9\s,\/•&–-]+?)\s+(?:pages|subpages|screens)",
        # "Pages: Home, About, Features..." or "Site: Home, Features..."
        r"(?:pages|subpages|screens)\s*[:=]\s*([A-Za-z0-9\s,\/•&–-]+?)(?:\.|\n\n|\n[A-Z]|$)",
        # "3-page site: Home, Features, Contact" or "5 pages: ..."
        r"(?:\d+[-\s]pages?|\d+[-\s]page\s+site)\s*[:\s]+([A-Za-z0-9\s,\/•&–-]+?)(?:\.|\n\n|\n[A-Z]|$)",
        # "pages for Home, About..."
        r"(?:separate\s+)?pages?\s+(?:for|of|named|including|such as)\s+([A-Za-z0-9\s,\/•&–-]+?)(?:\.|\n\n|\n[A-Z]|$)",
    ]

    candidate_text = None
    for pat in patterns:
        m = re.search(pat, p, re.IGNORECASE)
        if m:
            candidate_text = m.group(1)
            break

    # Also handle bullet point lists if "pages" is mentioned
    if not candidate_text:
        lines = p.split("\n")
        bullet_pages = []
        for line in lines:
            line_clean = line.strip().strip("-*• ")
            if line_clean and any(k in line_clean.lower() for k in ["page", "home", "about", "features", "pricing", "contact", "services", "blog", "portfolio", "docs", "team"]):
                name = re.sub(r"\bpages?\b", "", line_clean, flags=re.IGNORECASE).strip().strip(":- ")
                if name and len(name) < 30:
                    bullet_pages.append(name)
        if len(bullet_pages) >= 2:
            candidate_text = ", ".join(bullet_pages)

    if not candidate_text:
        return False, []

    candidate_text = re.sub(r"\s+(?:and|&)\s+", ", ", candidate_text, flags=re.IGNORECASE)
    raw_parts = re.split(r"[,•\n\r\t]+", candidate_text)

    pages = []
    seen_slugs = set()

    stop_words = ["and", "or", "&", "the", "with", "a", "all", "our", "an", "use", "make", "placeholder"]

    for part in raw_parts:
        clean_name = re.sub(r"\bpages?\b", "", part, flags=re.IGNORECASE).strip().strip("'\"").strip(".:;-* \t\n\r")
        if not clean_name or len(clean_name) < 2 or clean_name.lower() in stop_words:
            continue
        
        display_name = " ".join(word.capitalize() for word in clean_name.split())
        slug = slugify(display_name)
        
        if slug not in seen_slugs and slug not in stop_words:
            seen_slugs.add(slug)
            pages.append({
                "name": display_name,
                "slug": slug,
                "path": "index.html" if slug in ["home", "index", "landing"] or len(pages) == 0 else f"{slug}.html"
            })

    if len(pages) >= 2:
        home_idx = next((i for i, pg in enumerate(pages) if pg["slug"] in ["home", "index"]), None)
        if home_idx is not None and home_idx != 0:
            home_page = pages.pop(home_idx)
            home_page["path"] = "index.html"
            pages.insert(0, home_page)
        elif home_idx is None:
            pages[0]["path"] = "index.html"

        for i in range(1, len(pages)):
            if pages[i]["path"] == "index.html":
                pages[i]["path"] = f"{pages[i]['slug']}.html"

        return True, pages

    return False, []

def build_shared_header(pages: list[dict], current_page_path: str, site_name: str = "NexusAI", accent: str = "indigo") -> str:
    """Builds shared header navigation with active page indicator and working relative links."""
    desktop_links = []
    mobile_links = []

    for pg in pages:
        is_active = (pg["path"] == current_page_path)
        active_class = f"text-{accent}-400 font-semibold" if is_active else "text-slate-400 hover:text-white"
        mob_active_class = f"text-{accent}-400 font-semibold" if is_active else "text-slate-300 hover:text-white"

        desktop_links.append(f'<a href="{pg["path"]}" class="{active_class} transition-colors">{pg["name"]}</a>')
        mobile_links.append(f'<a href="{pg["path"]}" class="block py-1.5 {mob_active_class}">{pg["name"]}</a>')

    desktop_links_str = "\n        ".join(desktop_links)
    mobile_links_str = "\n      ".join(mobile_links)

    # CTA target page
    cta_target = "pricing.html" if any(p["path"] == "pricing.html" for p in pages) else pages[-1]["path"]

    return f"""  <!-- Header / Navigation -->
  <header class="sticky top-0 z-50 backdrop-blur-md bg-slate-950/85 border-b border-slate-800/80">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
      <a href="index.html" class="flex items-center gap-3 group">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-{accent}-600 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-{accent}-500/25 group-hover:scale-105 transition">
          <i data-lucide="sparkles" class="w-5 h-5"></i>
        </div>
        <span class="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-{accent}-300">{site_name}</span>
      </a>

      <!-- Desktop Nav Links -->
      <nav class="hidden md:flex items-center gap-8 text-sm font-medium">
        {desktop_links_str}
      </nav>

      <div class="hidden md:flex items-center gap-4">
        <a href="{cta_target}" class="px-5 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-{accent}-600 to-violet-600 hover:from-{accent}-500 hover:to-violet-500 text-white shadow-md shadow-{accent}-500/20 transition-all flex items-center gap-2">
          <span>Get Started</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </a>
      </div>

      <!-- Mobile Hamburger Button -->
      <button id="mobile-menu-btn" class="md:hidden p-2 text-slate-400 hover:text-white rounded-lg border border-slate-800">
        <i data-lucide="menu" class="w-5 h-5"></i>
      </button>
    </div>

    <!-- Mobile Drawer -->
    <div id="mobile-menu" class="hidden md:hidden px-6 py-4 bg-slate-900 border-b border-slate-800 space-y-2 text-sm">
      {mobile_links_str}
      <div class="pt-2">
        <a href="{cta_target}" class="block text-center py-2 px-4 rounded-lg bg-{accent}-600 text-white font-semibold text-xs">Get Started</a>
      </div>
    </div>
  </header>"""

def build_shared_footer(pages: list[dict], site_name: str = "NexusAI", accent: str = "indigo") -> str:
    """Builds shared consistent footer with relative links across all pages."""
    footer_links = []
    for pg in pages:
        footer_links.append(f'<a href="{pg["path"]}" class="hover:text-white transition">{pg["name"]}</a>')
    footer_links_str = " • ".join(footer_links)

    return f"""  <!-- Footer -->
  <footer class="border-t border-slate-900 bg-slate-950 py-12 text-center text-xs text-slate-500">
    <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-6">
      <div class="flex items-center gap-3 font-semibold text-slate-300">
        <div class="w-7 h-7 rounded-lg bg-{accent}-600 flex items-center justify-center text-white">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
        </div>
        <span>{site_name} Platform</span>
      </div>
      <div class="flex flex-wrap items-center justify-center gap-4 text-slate-400">
        {footer_links_str}
      </div>
      <p>&copy; 2026 {site_name} Technologies Inc. All rights reserved.</p>
    </div>
  </footer>"""

def build_page_html(
    page_desc: dict,
    all_pages: list[dict],
    prompt: str,
    accent: str = "indigo",
    site_name: str = "NexusAI"
) -> str:
    """Generates complete standalone HTML document for a specific page."""
    slug = page_desc["slug"]
    name = page_desc["name"]
    path = page_desc["path"]

    header_html = build_shared_header(all_pages, path, site_name, accent)
    footer_html = build_shared_footer(all_pages, site_name, accent)

    # Generate dedicated page body content based on slug/name
    content_html = ""

    if slug in ["home", "index", "landing"]:
        content_html = f"""  <!-- Home Hero Section -->
  <section id="hero" class="relative pt-24 pb-20 overflow-hidden text-center">
    <div class="absolute inset-0 -z-10 flex items-center justify-center">
      <div class="w-[600px] h-[600px] bg-{accent}-600/15 rounded-full blur-[140px] pointer-events-none"></div>
    </div>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-{accent}-950/70 border border-{accent}-500/30 text-{accent}-400 text-xs font-semibold uppercase tracking-wider mb-8 shadow-inner">
        <i data-lucide="zap" class="w-3.5 h-3.5"></i>
        <span>AI Productivity Platform v3.0</span>
      </div>

      <h1 class="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white mb-6 leading-tight">
        Supercharge Your Team with <br>
        <span class="bg-clip-text text-transparent bg-gradient-to-r from-{accent}-400 via-violet-300 to-cyan-300">Intelligent AI Workflows</span>
      </h1>

      <p class="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
        {site_name} orchestrates autonomous agent swarms to execute research, synthesize deep documents, summarize communications, and manage complex cross-functional workflows in real time.
      </p>

      <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
        <a href="pricing.html" class="w-full sm:w-auto px-8 py-4 rounded-xl font-semibold bg-gradient-to-r from-{accent}-600 to-violet-600 hover:from-{accent}-500 hover:to-violet-500 text-white shadow-xl shadow-{accent}-600/25 flex items-center justify-center gap-2 transition">
          <span>Get Started Free</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </a>
        <a href="features.html" class="w-full sm:w-auto px-8 py-4 rounded-xl font-semibold bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800 flex items-center justify-center gap-2 transition">
          <i data-lucide="play-circle" class="w-4 h-4 text-{accent}-400"></i>
          <span>Explore Features</span>
        </a>
      </div>

      <!-- Metric Counters -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto pt-8 border-t border-slate-800/80">
        <div class="p-4 rounded-2xl bg-slate-900/40 border border-slate-800">
          <div class="text-2xl sm:text-3xl font-extrabold text-white">10x</div>
          <div class="text-xs text-slate-400 mt-1">Faster Task Delivery</div>
        </div>
        <div class="p-4 rounded-2xl bg-slate-900/40 border border-slate-800">
          <div class="text-2xl sm:text-3xl font-extrabold text-white">99.9%</div>
          <div class="text-xs text-slate-400 mt-1">Uptime SLA</div>
        </div>
        <div class="p-4 rounded-2xl bg-slate-900/40 border border-slate-800">
          <div class="text-2xl sm:text-3xl font-extrabold text-white">50M+</div>
          <div class="text-xs text-slate-400 mt-1">Actions Executed</div>
        </div>
        <div class="p-4 rounded-2xl bg-slate-900/40 border border-slate-800">
          <div class="text-2xl sm:text-3xl font-extrabold text-white">SOC 2</div>
          <div class="text-xs text-slate-400 mt-1">Type II Certified</div>
        </div>
      </div>
    </div>
  </section>"""

    elif slug in ["about", "story", "mission", "company"]:
        content_html = f"""  <!-- About Page -->
  <section class="py-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-3xl mx-auto mb-20">
        <h2 class="text-xs font-bold text-{accent}-400 uppercase tracking-widest mb-3">Our Mission</h2>
        <h1 class="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">Reimagining Productivity for the AI Native Era</h1>
        <p class="text-slate-400 text-lg mt-6 leading-relaxed">
          At {site_name}, we build autonomous software infrastructure that turns cognitive overhead into seamless execution. Our platform unifies context across your team's tools to deliver superhuman velocity.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="target" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Autonomous Precision</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Multi-agent swarms equipped with fine-tuned reasoning models execute complex multi-step workflows without hallucinations or drift.
          </p>
        </div>

        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="network" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Unified Knowledge Mesh</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Connects Notion, Slack, GitHub, Google Workspace, and Jira into a real-time semantic vector graph with sub-millisecond retrieval.
          </p>
        </div>

        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="shield-check" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Zero-Trust Privacy</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Your proprietary company data is never used for training. End-to-end encryption with tenant isolation and granular access scopes.
          </p>
        </div>
      </div>

      <!-- Leadership / Team values -->
      <div class="p-8 sm:p-12 rounded-3xl bg-slate-900/60 border border-slate-800 max-w-5xl mx-auto text-center">
        <h3 class="text-2xl font-bold text-white mb-4">Built by Engineers &amp; AI Researchers</h3>
        <p class="text-slate-400 text-sm max-w-2xl mx-auto mb-8 leading-relaxed">
          Our global distributed team previously built core infrastructure at top AI research labs and high-scale tech enterprises.
        </p>
        <div class="flex flex-wrap justify-center gap-4 text-xs font-mono text-{accent}-400">
          <span class="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">Distributed Swarms</span>
          <span class="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">Vector Embeddings</span>
          <span class="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">Real-Time Context</span>
          <span class="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">Enterprise Ready</span>
        </div>
      </div>
    </div>
  </section>"""

    elif slug in ["features", "capabilities", "services", "product"]:
        content_html = f"""  <!-- Features Page -->
  <section class="py-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-3xl mx-auto mb-20">
        <h2 class="text-xs font-bold text-{accent}-400 uppercase tracking-widest mb-3">Core Platform</h2>
        <h1 class="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">Engineered for Velocity &amp; Scale</h1>
        <p class="text-slate-400 text-lg mt-6 leading-relaxed">
          Explore the next-generation capabilities that empower modern teams to automate complex work seamlessly.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
        <!-- Feature 1 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-{accent}-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="bot" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Multi-Agent Swarms</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Distribute complex cross-functional research and coding workloads across specialized agents operating in parallel with shared memory.
          </p>
        </div>

        <!-- Feature 2 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-{accent}-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="file-text" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Smart Document Synthesis</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Instantly ingest hundreds of pages of documentation, pull key quantitative insights, and auto-generate executive briefings.
          </p>
        </div>

        <!-- Feature 3 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-{accent}-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="calendar" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Autonomous Action Scheduler</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            AI agents triage your incoming communications, prepare meeting briefs ahead of time, and draft follow-up actions automatically.
          </p>
        </div>

        <!-- Feature 4 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-{accent}-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="zap" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Sub-Second Hybrid Search</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Semantic vector embeddings combined with BM25 keyword matching retrieve exact references and data points instantly.
          </p>
        </div>

        <!-- Feature 5 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-{accent}-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="lock" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Enterprise Governance</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Audit every single tool action and token output with granular role-based access control and comprehensive change logs.
          </p>
        </div>

        <!-- Feature 6 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-{accent}-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="cpu" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Custom LLM Connectors</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Bring your own API keys or private self-hosted models seamlessly with automatic model routing and latency failover.
          </p>
        </div>
      </div>
    </div>
  </section>"""

    elif slug in ["pricing", "plans", "tiers"]:
        content_html = f"""  <!-- Pricing Page -->
  <section class="py-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <div class="max-w-2xl mx-auto mb-16">
        <h2 class="text-xs font-bold text-{accent}-400 uppercase tracking-widest mb-3">Transparent Plans</h2>
        <h1 class="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">Predictable Pricing for High-Growth Teams</h1>
        <p class="text-slate-400 text-lg mt-4 leading-relaxed">
          Start in our free sandbox and scale up seamlessly as your team's workflow requirements expand.
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-5xl mx-auto text-left mb-20">
        <!-- Starter Plan -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
          <div>
            <h4 class="text-lg font-bold text-white mb-2">Starter</h4>
            <p class="text-slate-400 text-sm mb-6">For individuals and prototyping.</p>
            <div class="text-4xl font-extrabold text-white mb-6">$0<span class="text-sm font-normal text-slate-500"> / month</span></div>
            <ul class="space-y-3 text-sm text-slate-300 mb-8">
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Up to 3 autonomous agents</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> 10,000 monthly execution tokens</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Standard integrations (Slack, Notion)</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Community support</li>
            </ul>
          </div>
          <button class="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold transition">Get Started Free</button>
        </div>

        <!-- Pro Plan -->
        <div class="p-8 rounded-2xl bg-slate-900 border-2 border-{accent}-500 shadow-2xl shadow-{accent}-500/15 flex flex-col justify-between relative">
          <div class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-{accent}-600 text-[10px] font-bold tracking-wider text-white uppercase">Most Popular</div>
          <div>
            <h4 class="text-lg font-bold text-white mb-2">Team Pro</h4>
            <p class="text-slate-400 text-sm mb-6">For fast-moving engineering &amp; product teams.</p>
            <div class="text-4xl font-extrabold text-white mb-6">$49<span class="text-sm font-normal text-slate-500"> / month</span></div>
            <ul class="space-y-3 text-sm text-slate-300 mb-8">
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Unlimited autonomous agent swarms</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> 1,000,000 monthly execution tokens</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Advanced integrations (GitHub, Jira, Linear)</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Real-time priority agent execution</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Priority 24/7 technical support</li>
            </ul>
          </div>
          <button class="w-full py-3 rounded-xl bg-gradient-to-r from-{accent}-600 to-violet-600 hover:from-{accent}-500 hover:to-violet-500 text-white font-semibold transition shadow-lg shadow-indigo-600/30">Start 14-Day Free Trial</button>
        </div>

        <!-- Enterprise Plan -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
          <div>
            <h4 class="text-lg font-bold text-white mb-2">Enterprise</h4>
            <p class="text-slate-400 text-sm mb-6">Dedicated deployment &amp; bespoke governance.</p>
            <div class="text-4xl font-extrabold text-white mb-6">Custom</div>
            <ul class="space-y-3 text-sm text-slate-300 mb-8">
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Dedicated isolated VPC deployment</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Custom fine-tuned domain models</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> SAML SSO, SCIM &amp; custom audit exports</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-{accent}-400"></i> Dedicated customer success manager &amp; SLA</li>
            </ul>
          </div>
          <button class="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold transition">Contact Enterprise Sales</button>
        </div>
      </div>

      <!-- FAQ Section -->
      <div id="pricing-faq" class="max-w-3xl mx-auto text-left pt-12 border-t border-slate-900">
        <h3 class="text-2xl font-bold text-white text-center mb-8">Frequently Asked Questions</h3>
        <div class="space-y-4">
          <div class="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h5 class="text-base font-bold text-white mb-2">Can I switch plans or cancel anytime?</h5>
            <p class="text-sm text-slate-400">Yes! You can upgrade, downgrade, or cancel your subscription at any time directly from the settings console with zero penalties.</p>
          </div>
          <div class="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h5 class="text-base font-bold text-white mb-2">How do execution tokens work?</h5>
            <p class="text-sm text-slate-400">Tokens correspond to the computational steps executed by your autonomous agent swarms. Starter includes 10k tokens/mo, while Pro includes 1M tokens.</p>
          </div>
        </div>
      </div>
    </div>
  </section>"""

    elif slug in ["contact", "get-in-touch", "reach-out", "support"]:
        content_html = f"""  <!-- Contact Page -->
  <section class="py-24">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <div class="w-12 h-12 rounded-2xl bg-{accent}-500/10 border border-{accent}-500/30 text-{accent}-400 flex items-center justify-center mx-auto mb-4">
        <i data-lucide="mail" class="w-6 h-6"></i>
      </div>
      <h1 class="text-4xl sm:text-5xl font-extrabold text-white mb-4">Get in Touch with Our Team</h1>
      <p class="text-base text-slate-400 max-w-md mx-auto mb-12 leading-relaxed">
        Have questions about custom agent swarms, security compliance, or enterprise rollout? Reach out anytime!
      </p>

      <div class="p-6 sm:p-8 rounded-2xl bg-slate-900 border border-slate-800 text-left shadow-xl mb-12">
        <form id="contact-form" class="space-y-4" onsubmit="event.preventDefault(); document.getElementById('contact-success').classList.remove('hidden');">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1.5">Your Name</label>
              <input type="text" required placeholder="Alex Morgan" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-{accent}-500 transition">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1.5">Work Email</label>
              <input type="email" required placeholder="alex@company.com" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-{accent}-500 transition">
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1.5">Team Size &amp; Use Case</label>
            <input type="text" placeholder="e.g. 25 engineers, automating code review & research" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-{accent}-500 transition">
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1.5">Message</label>
            <textarea rows="3" required placeholder="Tell us about the workflows you want to automate..." class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-{accent}-500 transition resize-none"></textarea>
          </div>
          <button type="submit" class="w-full py-3.5 rounded-xl font-semibold bg-gradient-to-r from-{accent}-600 to-violet-600 hover:from-{accent}-500 hover:to-violet-500 text-white transition flex items-center justify-center gap-2 shadow-lg shadow-{accent}-600/25">
            <i data-lucide="send" class="w-4 h-4"></i>
            <span>Send Message</span>
          </button>
          <div id="contact-success" class="hidden p-4 rounded-xl bg-{accent}-950/70 border border-{accent}-500/40 text-xs text-{accent}-300 text-center font-medium">
            ✓ Message sent successfully! Our solutions engineering team will reach out within 2 business hours.
          </div>
        </form>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
        <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <i data-lucide="clock" class="w-5 h-5 text-{accent}-400 mx-auto mb-2"></i>
          <span class="text-xs font-bold text-white block">Response Time</span>
          <span class="text-[11px] text-slate-400">&lt; 2 Business Hours</span>
        </div>
        <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <i data-lucide="map-pin" class="w-5 h-5 text-{accent}-400 mx-auto mb-2"></i>
          <span class="text-xs font-bold text-white block">Global Headquarters</span>
          <span class="text-[11px] text-slate-400">San Francisco, CA</span>
        </div>
        <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <i data-lucide="shield" class="w-5 h-5 text-{accent}-400 mx-auto mb-2"></i>
          <span class="text-xs font-bold text-white block">Security &amp; SLA</span>
          <span class="text-[11px] text-slate-400">SOC 2 Type II Verified</span>
        </div>
      </div>
    </div>
  </section>"""

    else:
        # Generic Page Builder for any arbitrary page name requested by user
        content_html = f"""  <!-- {name} Page -->
  <section class="py-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-3xl mx-auto mb-16">
        <h2 class="text-xs font-bold text-{accent}-400 uppercase tracking-widest font-mono mb-3">{site_name} Overview</h2>
        <h1 class="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">{name}</h1>
        <p class="text-slate-400 text-lg mt-4 leading-relaxed">
          Comprehensive details and resources for {name}.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="layers" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Structured Overview</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Essential specifications, structured metrics, and workflow integrations designed for {name}.
          </p>
        </div>

        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="zap" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Instant Execution</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Low-latency automated agent capabilities operating with continuous contextual memory.
          </p>
        </div>

        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="w-12 h-12 rounded-xl bg-{accent}-950 border border-{accent}-800/50 flex items-center justify-center text-{accent}-400 mb-6">
            <i data-lucide="shield" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Enterprise Grade</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Fully sandboxed environment compliant with strict governance and security benchmarks.
          </p>
        </div>
      </div>
    </div>
  </section>"""

    return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} | {site_name}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['Plus Jakarta Sans', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          }},
          colors: {{
            brand: {{
              50: '#eef2ff',
              500: '#6366f1',
              600: '#4f46e5',
              700: '#4338ca',
            }}
          }}
        }}
      }}
    }}
  </script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans antialiased selection:bg-{accent}-500 selection:text-white">

{header_html}

{content_html}

{footer_html}

  <script>
    lucide.createIcons();
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    if (btn && menu) {{
      btn.addEventListener('click', () => menu.classList.toggle('hidden'));
    }}
  </script>
</body>
</html>"""

def generate_multi_page_project(prompt: str, page_descriptors: list[dict]) -> list[dict]:
    """
    Generates all requested pages for a multi-page project.
    Returns: list of {"name": "...", "path": "...", "html": "..."}
    """
    accent = "indigo"
    p_lower = prompt.lower()
    if "emerald" in p_lower or "green" in p_lower:
        accent = "emerald"
    elif "cyan" in p_lower or "teal" in p_lower:
        accent = "cyan"
    elif "blue" in p_lower:
        accent = "blue"
    elif "violet" in p_lower or "purple" in p_lower:
        accent = "violet"

    site_name = "NexusAI"
    m_name = re.search(r"(?:for|named|called)\s+['\"]?([A-Za-z0-9\s]+?)(?:startup|platform|app|website|saas|['\"]|\.)", prompt, re.IGNORECASE)
    if m_name:
        extracted = m_name.group(1).strip()
        if extracted and len(extracted) < 20 and extracted.lower() not in ["an", "a", "our", "the", "my"]:
            site_name = extracted

    generated_pages = []
    for pg in page_descriptors:
        page_html = build_page_html(pg, page_descriptors, prompt, accent=accent, site_name=site_name)
        generated_pages.append({
            "name": pg["name"],
            "path": pg["path"],
            "html": page_html
        })

    return generated_pages

def refine_multi_page_project(
    pages: list[dict],
    instruction: str,
    active_page_path: str | None = None
) -> list[dict]:
    """
    Applies refinement to a multi-page project:
    - Page-specific edits: "on the Home page", "on the Pricing page", "in about.html", etc.
    - Global theme/style edits: "across the entire website", "change primary color to emerald", "change navbar", etc.
    """
    inst_lower = instruction.lower()
    updated_pages = []

    # Check for global theme / full website refinement
    is_global = any(k in inst_lower for k in [
        "across the entire website", "across all pages", "entire site", "all pages",
        "whole website", "every page", "globally", "primary color across", "theme across"
    ])

    # Check for page-specific target
    target_path = None
    if not is_global:
        for pg in pages:
            name_lower = pg["name"].lower()
            slug_lower = pg["path"].replace(".html", "").lower()
            if (
                f"{name_lower} page" in inst_lower
                or f"page {name_lower}" in inst_lower
                or f"in {name_lower}" in inst_lower
                or f"on {name_lower}" in inst_lower
                or f"on the {name_lower}" in inst_lower
                or f"to the {name_lower}" in inst_lower
                or f"in the {name_lower}" in inst_lower
                or f"{slug_lower}.html" in inst_lower
                or f"to {name_lower}" in inst_lower
            ):
                target_path = pg["path"]
                break

    # If no target specified and not explicitly global, check if instruction uniquely targets a page section
    if not is_global and not target_path:
        if any(k in inst_lower for k in ["hero", "headline", "hero heading"]):
            target_path = "index.html"
        elif any(k in inst_lower for k in ["pricing tier", "pricing plan", "faq section", "faq"]):
            target_path = "pricing.html" if any(p["path"] == "pricing.html" for p in pages) else "index.html"
        elif any(k in inst_lower for k in ["contact form", "office location"]):
            target_path = "contact.html" if any(p["path"] == "contact.html" for p in pages) else "index.html"
        elif active_page_path:
            target_path = active_page_path
        else:
            target_path = "index.html"

    # Color change detection
    new_color = None
    if "emerald" in inst_lower or "green" in inst_lower:
        new_color = "emerald"
    elif "cyan" in inst_lower or "teal" in inst_lower:
        new_color = "cyan"
    elif "blue" in inst_lower:
        new_color = "blue"
    elif "violet" in inst_lower or "purple" in inst_lower:
        new_color = "violet"
    elif "indigo" in inst_lower:
        new_color = "indigo"

    for pg in pages:
        current_html = pg["html"]
        if is_global or (new_color and ("primary color" in inst_lower or "theme" in inst_lower)):
            # Apply to all pages
            modified_html = apply_smart_refinement(current_html, instruction)
            updated_pages.append({
                "name": pg["name"],
                "path": pg["path"],
                "html": modified_html
            })
        elif pg["path"] == target_path:
            # Apply page-specific refinement
            modified_html = apply_smart_refinement(current_html, instruction)
            updated_pages.append({
                "name": pg["name"],
                "path": pg["path"],
                "html": modified_html
            })
        else:
            # Leave other pages untouched
            updated_pages.append(pg)

    return updated_pages
