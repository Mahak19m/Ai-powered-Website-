"""
Dynamic and intelligent website template generation & refinement engine for offline/demo mode.
Generates responsive, modern HTML5 + Tailwind CSS + Lucide Icons websites tailored to prompt requirements.
"""

import re

def generate_cs_ai_portfolio(prompt: str) -> str:
    """Generates a clean, modern CS Student & AI/ML / Software Developer portfolio."""
    return """<!DOCTYPE html>
<html lang="en" class="scroll-smooth dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Portfolio | Computer Science & AI/ML</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Plus Jakarta Sans', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          },
          colors: {
            brand: {
              50: '#f0fdf4',
              500: '#10b981',
              600: '#059669',
              700: '#047857',
            }
          }
        }
      }
    }
  </script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans antialiased selection:bg-emerald-500 selection:text-black">

  <!-- Header / Navigation -->
  <header class="sticky top-0 z-50 backdrop-blur-lg bg-slate-950/80 border-b border-slate-800/80">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
          <i data-lucide="terminal" class="w-4 h-4"></i>
        </div>
        <span class="font-mono font-bold text-sm text-white tracking-tight">&lt;dev.ai /&gt;</span>
      </div>

      <nav class="hidden md:flex items-center gap-6 text-xs font-medium text-slate-400">
        <a href="#about" class="hover:text-emerald-400 transition">About</a>
        <a href="#skills" class="hover:text-emerald-400 transition">Skills</a>
        <a href="#projects" class="hover:text-emerald-400 transition">Projects</a>
        <a href="#education" class="hover:text-emerald-400 transition">Education</a>
        <a href="#experience" class="hover:text-emerald-400 transition">Experience</a>
        <a href="#contact" class="px-3.5 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold transition">Contact</a>
      </nav>

      <!-- Mobile Button -->
      <button id="mobile-menu-btn" class="md:hidden p-2 text-slate-400 hover:text-white">
        <i data-lucide="menu" class="w-5 h-5"></i>
      </button>
    </div>

    <!-- Mobile Drawer -->
    <div id="mobile-menu" class="hidden md:hidden px-4 py-4 bg-slate-900 border-b border-slate-800 space-y-2 text-sm">
      <a href="#about" class="block py-1.5 text-slate-300 hover:text-emerald-400">About</a>
      <a href="#skills" class="block py-1.5 text-slate-300 hover:text-emerald-400">Skills</a>
      <a href="#projects" class="block py-1.5 text-slate-300 hover:text-emerald-400">Projects</a>
      <a href="#education" class="block py-1.5 text-slate-300 hover:text-emerald-400">Education</a>
      <a href="#experience" class="block py-1.5 text-slate-300 hover:text-emerald-400">Experience</a>
      <a href="#contact" class="block py-1.5 text-emerald-400 font-medium">Contact</a>
    </div>
  </header>

  <!-- Hero Section -->
  <section id="hero" class="relative pt-20 pb-16 overflow-hidden">
    <div class="absolute inset-0 -z-10 flex items-center justify-center">
      <div class="w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[128px] pointer-events-none"></div>
    </div>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-medium mb-6">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        Computer Science Student • AI/ML & Software Development
      </div>

      <h1 class="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
        Building Intelligent Systems &amp; Modern Software
      </h1>

      <p class="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto mb-8 leading-relaxed">
        Computer Science undergraduate focusing on Artificial Intelligence, Machine Learning algorithms, backend architectures, and high-performance software engineering.
      </p>

      <div class="flex flex-wrap items-center justify-center gap-4">
        <a href="#projects" class="px-6 py-3 rounded-xl font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition flex items-center gap-2 shadow-lg shadow-emerald-500/20">
          <i data-lucide="folder-git-2" class="w-4 h-4"></i>
          Explore Projects
        </a>
        <a href="#contact" class="px-6 py-3 rounded-xl font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition flex items-center gap-2">
          <i data-lucide="mail" class="w-4 h-4"></i>
          Get in Touch
        </a>
      </div>
    </div>
  </section>

  <!-- About Section -->
  <section id="about" class="py-16 bg-slate-900/40 border-t border-slate-900">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-2xl mx-auto mb-12">
        <h2 class="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono mb-2">About Me</h2>
        <h3 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Passionate about Code, Math &amp; Intelligence</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div class="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-800/40 flex items-center justify-center text-emerald-400 mb-4">
            <i data-lucide="cpu" class="w-5 h-5"></i>
          </div>
          <h4 class="text-lg font-bold text-white mb-2">AI / Machine Learning</h4>
          <p class="text-sm text-slate-400 leading-relaxed">Specialized in deep learning architectures, model training, computer vision pipelines, and natural language processing.</p>
        </div>

        <div class="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div class="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-800/40 flex items-center justify-center text-emerald-400 mb-4">
            <i data-lucide="server" class="w-5 h-5"></i>
          </div>
          <h4 class="text-lg font-bold text-white mb-2">Software &amp; Backend</h4>
          <p class="text-sm text-slate-400 leading-relaxed">Designing RESTful microservices, asynchronous workers, scalable database schemas, and clean, maintainable APIs.</p>
        </div>

        <div class="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div class="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-800/40 flex items-center justify-center text-emerald-400 mb-4">
            <i data-lucide="git-branch" class="w-5 h-5"></i>
          </div>
          <h4 class="text-lg font-bold text-white mb-2">Systems &amp; DevOps</h4>
          <p class="text-sm text-slate-400 leading-relaxed">Proficient with Linux environments, containerization via Docker, Git version control, and CI/CD automated deployment flows.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Skills Section -->
  <section id="skills" class="py-16 border-t border-slate-900">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-2xl mx-auto mb-12">
        <h2 class="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono mb-2">Technical Proficiency</h2>
        <h3 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Core Skills &amp; Technologies</h3>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- AI/ML -->
        <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div class="flex items-center gap-2 mb-3 text-emerald-400">
            <i data-lucide="brain" class="w-4 h-4"></i>
            <h4 class="font-bold text-sm text-white">AI / Data Science</h4>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">PyTorch</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">TensorFlow</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">Scikit-Learn</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">NumPy &amp; Pandas</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">OpenCV</span>
          </div>
        </div>

        <!-- Programming Languages -->
        <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div class="flex items-center gap-2 mb-3 text-emerald-400">
            <i data-lucide="code" class="w-4 h-4"></i>
            <h4 class="font-bold text-sm text-white">Languages</h4>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <span class="px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-500/40 text-xs text-emerald-300 font-semibold">Python</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">C / C++</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">Java</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">JavaScript / TS</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">SQL</span>
          </div>
        </div>

        <!-- Backend & Frameworks -->
        <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div class="flex items-center gap-2 mb-3 text-emerald-400">
            <i data-lucide="layers" class="w-4 h-4"></i>
            <h4 class="font-bold text-sm text-white">Backend &amp; Web</h4>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <span class="px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-500/40 text-xs text-emerald-300 font-semibold">FastAPI</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">Flask</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">Node.js</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">React</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">PostgreSQL</span>
          </div>
        </div>

        <!-- Tools & DevOps -->
        <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div class="flex items-center gap-2 mb-3 text-emerald-400">
            <i data-lucide="wrench" class="w-4 h-4"></i>
            <h4 class="font-bold text-sm text-white">Tools &amp; Infra</h4>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">Git &amp; GitHub</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">Docker</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">Linux / Bash</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">Postman</span>
            <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs text-slate-300">CI/CD</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Projects Section -->
  <section id="projects" class="py-16 bg-slate-900/40 border-t border-slate-900">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-2xl mx-auto mb-12">
        <h2 class="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono mb-2">Featured Work</h2>
        <h3 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Projects &amp; Implementations</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Project 1 -->
        <div class="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-emerald-500/40 transition group">
          <div class="flex items-center justify-between mb-4">
            <span class="text-xs font-mono text-emerald-400 font-semibold">Python • PyTorch • FastAPI</span>
            <div class="flex gap-2">
              <span class="p-1.5 rounded-lg bg-slate-800 text-slate-400 group-hover:text-emerald-400"><i data-lucide="github" class="w-4 h-4"></i></span>
              <span class="p-1.5 rounded-lg bg-slate-800 text-slate-400 group-hover:text-emerald-400"><i data-lucide="external-link" class="w-4 h-4"></i></span>
            </div>
          </div>
          <h4 class="text-xl font-bold text-white mb-2 group-hover:text-emerald-400 transition">Autonomous Multi-Agent Orchestrator</h4>
          <p class="text-sm text-slate-400 mb-4 leading-relaxed">Built an asynchronous framework for distributing analytical and coding tasks among specialized LLM agents with vector memory retrieval.</p>
          <div class="flex flex-wrap gap-2 text-[11px] font-mono text-slate-400">
            <span class="px-2 py-0.5 rounded bg-slate-800">FastAPI</span>
            <span class="px-2 py-0.5 rounded bg-slate-800">Python 3.12</span>
            <span class="px-2 py-0.5 rounded bg-slate-800">ChromaDB</span>
          </div>
        </div>

        <!-- Project 2 -->
        <div class="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-emerald-500/40 transition group">
          <div class="flex items-center justify-between mb-4">
            <span class="text-xs font-mono text-emerald-400 font-semibold">Deep Learning • Computer Vision</span>
            <div class="flex gap-2">
              <span class="p-1.5 rounded-lg bg-slate-800 text-slate-400 group-hover:text-emerald-400"><i data-lucide="github" class="w-4 h-4"></i></span>
              <span class="p-1.5 rounded-lg bg-slate-800 text-slate-400 group-hover:text-emerald-400"><i data-lucide="external-link" class="w-4 h-4"></i></span>
            </div>
          </div>
          <h4 class="text-xl font-bold text-white mb-2 group-hover:text-emerald-400 transition">Real-Time Object Detection &amp; Tracking</h4>
          <p class="text-sm text-slate-400 mb-4 leading-relaxed">Trained custom convolutional neural networks for multi-class edge detection achieving 94.2% mAP with low-latency inference.</p>
          <div class="flex flex-wrap gap-2 text-[11px] font-mono text-slate-400">
            <span class="px-2 py-0.5 rounded bg-slate-800">PyTorch</span>
            <span class="px-2 py-0.5 rounded bg-slate-800">OpenCV</span>
            <span class="px-2 py-0.5 rounded bg-slate-800">TensorRT</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Education Section -->
  <section id="education" class="py-16 border-t border-slate-900">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-2xl mx-auto mb-12">
        <h2 class="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono mb-2">Academic Background</h2>
        <h3 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Education &amp; Foundations</h3>
      </div>

      <div class="max-w-3xl mx-auto p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-4">
          <div>
            <h4 class="text-lg font-bold text-white">Bachelor of Science in Computer Science</h4>
            <p class="text-sm text-emerald-400 font-medium">Specialization: Artificial Intelligence &amp; Software Systems</p>
          </div>
          <span class="text-xs font-mono text-slate-500 mt-1 sm:mt-0">Expected Graduation: 2026</span>
        </div>
        <p class="text-sm text-slate-400 leading-relaxed mb-4">
          Core Focus: Algorithmic Complexity, Machine Learning Foundations, Deep Neural Networks, Operating Systems, Database Management Systems, and Software Architecture.
        </p>
        <div class="pt-3 border-t border-slate-800/80 flex flex-wrap gap-2 text-xs text-slate-400">
          <span class="text-slate-500 font-medium">Key Coursework:</span>
          <span>Data Structures &amp; Algorithms</span> •
          <span>Machine Learning</span> •
          <span>Computer Systems</span> •
          <span>Linear Algebra &amp; Probability</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Experience Section -->
  <section id="experience" class="py-16 bg-slate-900/40 border-t border-slate-900">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-2xl mx-auto mb-12">
        <h2 class="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono mb-2">Career Journey</h2>
        <h3 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Experience &amp; Contributions</h3>
      </div>

      <div class="max-w-3xl mx-auto space-y-6">
        <div class="p-6 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-2">
            <h4 class="text-base font-bold text-white">Software Engineering &amp; AI Intern</h4>
            <span class="text-xs font-mono text-emerald-400">Recent Internship</span>
          </div>
          <p class="text-xs text-slate-400 mb-3">AI Research &amp; Engineering Lab</p>
          <ul class="space-y-2 text-sm text-slate-300">
            <li class="flex items-start gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0"></i> Developed and optimized FastAPI endpoints for real-time model inference.</li>
            <li class="flex items-start gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0"></i> Automated data preprocessing pipelines using Python and Docker containerization.</li>
          </ul>
        </div>

        <div class="p-6 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-2">
            <h4 class="text-base font-bold text-white">Open Source Contributor &amp; Student Researcher</h4>
            <span class="text-xs font-mono text-slate-400">Ongoing</span>
          </div>
          <p class="text-xs text-slate-400 mb-3">Computer Science Research Group</p>
          <ul class="space-y-2 text-sm text-slate-300">
            <li class="flex items-start gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0"></i> Collaborated on open-source machine learning tooling and algorithmic benchmarks.</li>
            <li class="flex items-start gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0"></i> Authored technical documentation and reproducible benchmark environments.</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- Contact Section -->
  <section id="contact" class="py-20 border-t border-slate-900">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto mb-4">
        <i data-lucide="send" class="w-5 h-5"></i>
      </div>
      <h2 class="text-3xl font-bold text-white mb-3">Get in Touch</h2>
      <p class="text-sm text-slate-400 max-w-md mx-auto mb-8 leading-relaxed">
        Interested in collaborating, discussing AI/ML research, or exploring software engineering opportunities? Reach out anytime!
      </p>

      <div class="p-6 sm:p-8 rounded-2xl bg-slate-900 border border-slate-800 text-left">
        <form id="contact-form" class="space-y-4" onsubmit="event.preventDefault(); document.getElementById('form-success').classList.remove('hidden');">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1.5">Your Name</label>
              <input type="text" required placeholder="Jane Doe" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-emerald-500 transition">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1.5">Email Address</label>
              <input type="email" required placeholder="jane@example.com" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-emerald-500 transition">
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1.5">Message</label>
            <textarea rows="3" required placeholder="Let's connect about a project or opportunity..." class="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-emerald-500 transition resize-none"></textarea>
          </div>
          <button type="submit" class="w-full py-3 rounded-xl font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition flex items-center justify-center gap-2">
            <i data-lucide="send" class="w-4 h-4"></i>
            Send Message
          </button>
          <div id="form-success" class="hidden p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-xs text-emerald-300 text-center font-medium">
            ✓ Message sent successfully! I will get back to you shortly.
          </div>
        </form>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="border-t border-slate-900 bg-slate-950 py-8 text-center text-xs text-slate-500">
    <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2 font-mono text-slate-400">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span>Computer Science &amp; AI/ML Portfolio</span>
      </div>
      <p>&copy; 2026 Designed with modern web standards.</p>
    </div>
  </footer>

  <script>
    lucide.createIcons();
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    if (btn && menu) {
      btn.addEventListener('click', () => menu.classList.toggle('hidden'));
    }
  </script>
</body>
</html>"""

def generate_saas_template(prompt: str) -> str:
    """Generates a modern AI Platform / SaaS landing page with Home, About, Features, Pricing, and Contact."""
    return """<!DOCTYPE html>
<html lang="en" class="scroll-smooth dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NexusAI - Next-Gen AI Productivity Suite</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Plus Jakarta Sans', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          },
          colors: {
            brand: {
              50: '#eef2ff',
              500: '#6366f1',
              600: '#4f46e5',
              700: '#4338ca',
            }
          }
        }
      }
    }
  </script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans antialiased selection:bg-indigo-500 selection:text-white">

  <!-- Navigation -->
  <header class="sticky top-0 z-50 backdrop-blur-md bg-slate-950/85 border-b border-slate-800/80">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
      <a href="#home" class="flex items-center gap-3 group">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition">
          <i data-lucide="sparkles" class="w-5 h-5"></i>
        </div>
        <span class="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-300">NexusAI</span>
      </a>

      <!-- Desktop Nav Links -->
      <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
        <a href="#home" class="hover:text-indigo-400 transition-colors">Home</a>
        <a href="#about" class="hover:text-indigo-400 transition-colors">About</a>
        <a href="#features" class="hover:text-indigo-400 transition-colors">Features</a>
        <a href="#pricing" class="hover:text-indigo-400 transition-colors">Pricing</a>
        <a href="#contact" class="hover:text-indigo-400 transition-colors">Contact</a>
      </nav>

      <div class="hidden md:flex items-center gap-4">
        <a href="#pricing" class="px-5 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-md shadow-indigo-500/20 transition-all flex items-center gap-2">
          <span>Start Free Trial</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </a>
      </div>

      <!-- Mobile Hamburger Button -->
      <button id="mobile-menu-btn" class="md:hidden p-2 text-slate-400 hover:text-white rounded-lg border border-slate-800">
        <i data-lucide="menu" class="w-5 h-5"></i>
      </button>
    </div>

    <!-- Mobile Drawer -->
    <div id="mobile-menu" class="hidden md:hidden px-6 py-4 bg-slate-900 border-b border-slate-800 space-y-3 text-sm">
      <a href="#home" class="block py-1 text-slate-300 hover:text-indigo-400">Home</a>
      <a href="#about" class="block py-1 text-slate-300 hover:text-indigo-400">About</a>
      <a href="#features" class="block py-1 text-slate-300 hover:text-indigo-400">Features</a>
      <a href="#pricing" class="block py-1 text-slate-300 hover:text-indigo-400">Pricing</a>
      <a href="#contact" class="block py-1 text-indigo-400 font-semibold">Contact</a>
    </div>
  </header>

  <!-- Home / Hero Section -->
  <section id="home" class="relative pt-24 pb-20 overflow-hidden text-center">
    <div class="absolute inset-0 -z-10 flex items-center justify-center">
      <div class="w-[600px] h-[600px] bg-indigo-600/15 rounded-full blur-[140px] pointer-events-none"></div>
    </div>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-950/70 border border-indigo-500/30 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-8 shadow-inner">
        <i data-lucide="zap" class="w-3.5 h-3.5"></i>
        <span>Autonomous AI Productivity Suite v3.0</span>
      </div>

      <h1 class="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white mb-6 leading-tight">
        Supercharge Your Team with <br>
        <span class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-violet-300 to-cyan-300">AI-Powered Workflows</span>
      </h1>

      <p class="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
        NexusAI orchestrates intelligent agent swarms to automate deep research, synthesize documents, summarize communications, and manage complex cross-functional workflows in real time.
      </p>

      <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
        <a href="#pricing" class="w-full sm:w-auto px-8 py-4 rounded-xl font-semibold bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-xl shadow-indigo-600/25 flex items-center justify-center gap-2 transition">
          <span>Get Started Free</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </a>
        <a href="#features" class="w-full sm:w-auto px-8 py-4 rounded-xl font-semibold bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800 flex items-center justify-center gap-2 transition">
          <i data-lucide="play-circle" class="w-4 h-4 text-indigo-400"></i>
          <span>Explore Capabilities</span>
        </a>
      </div>

      <!-- Hero Metric Counters -->
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
  </section>

  <!-- About Section -->
  <section id="about" class="py-24 bg-slate-900/40 border-t border-slate-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-3xl mx-auto mb-16">
        <h2 class="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-3">Our Mission</h2>
        <h3 class="text-3xl sm:text-4xl font-bold text-white tracking-tight">Reimagining Productivity for the AI Native Era</h3>
        <p class="text-slate-400 text-base mt-4 leading-relaxed">
          We build autonomous software infrastructure that turns cognitive overhead into seamless automated execution. Our platform unifies context across your team's tools to deliver superhuman velocity.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-6">
            <i data-lucide="target" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Precision Autonomous Agents</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Multi-agent swarms equipped with fine-tuned reasoning models that execute multi-step workflows without hallucinations or drift.
          </p>
        </div>

        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-6">
            <i data-lucide="network" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Unified Knowledge Mesh</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Connects Notion, Slack, GitHub, Google Workspace, and Jira into a real-time semantic vector graph with sub-millisecond retrieval.
          </p>
        </div>

        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800">
          <div class="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-6">
            <i data-lucide="shield-check" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Zero-Trust Enterprise Privacy</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Your proprietary company data is never used for training. End-to-end encryption with tenant isolation and granular access scopes.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- Features Section -->
  <section id="features" class="py-24 border-t border-slate-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-3xl mx-auto mb-16">
        <h2 class="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-3">Engineered for Velocity</h2>
        <h3 class="text-3xl sm:text-4xl font-bold text-white tracking-tight">Powerful Capabilities for High-Growth Teams</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Feature 1 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-6">
            <i data-lucide="bot" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Multi-Agent Swarms</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Distribute complex cross-functional research and coding workloads across specialized agents operating in parallel with shared memory.
          </p>
        </div>

        <!-- Feature 2 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-6">
            <i data-lucide="file-text" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Smart Document Synthesis</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Instantly ingest hundreds of pages of documentation, pull key quantitative insights, and auto-generate executive briefings.
          </p>
        </div>

        <!-- Feature 3 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-6">
            <i data-lucide="calendar" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Autonomous Action Scheduler</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            AI agents triage your incoming communications, prepare meeting briefs ahead of time, and draft follow-up actions automatically.
          </p>
        </div>

        <!-- Feature 4 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-6">
            <i data-lucide="zap" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Sub-Second Hybrid Search</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Semantic vector embeddings combined with BM25 keyword matching retrieve exact references and data points instantly.
          </p>
        </div>

        <!-- Feature 5 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-6">
            <i data-lucide="lock" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Enterprise Governance</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Audit every single tool action and token output with granular role-based access control and comprehensive change logs.
          </p>
        </div>

        <!-- Feature 6 -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/40 transition">
          <div class="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/50 flex items-center justify-center text-indigo-400 mb-6">
            <i data-lucide="cpu" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-bold text-white mb-3">Custom LLM Connectors</h4>
          <p class="text-slate-400 text-sm leading-relaxed">
            Bring your own API keys or private self-hosted models seamlessly with automatic model routing and latency failover.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- Pricing Section -->
  <section id="pricing" class="py-24 bg-slate-900/40 border-t border-slate-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <div class="max-w-2xl mx-auto mb-16">
        <h2 class="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-3">Transparent Pricing</h2>
        <h3 class="text-3xl sm:text-4xl font-bold text-white tracking-tight">Simple, Scalable Plans for Every Stage</h3>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-5xl mx-auto text-left">
        <!-- Starter Plan -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
          <div>
            <h4 class="text-lg font-bold text-white mb-2">Starter</h4>
            <p class="text-slate-400 text-sm mb-6">For individuals and prototyping.</p>
            <div class="text-4xl font-extrabold text-white mb-6">$0<span class="text-sm font-normal text-slate-500"> / month</span></div>
            <ul class="space-y-3 text-sm text-slate-300 mb-8">
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Up to 3 autonomous agents</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> 10,000 monthly execution tokens</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Standard integrations (Slack, Notion)</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Community support</li>
            </ul>
          </div>
          <button class="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold transition">Get Started Free</button>
        </div>

        <!-- Pro Plan (Featured) -->
        <div class="p-8 rounded-2xl bg-slate-900 border-2 border-indigo-500 shadow-2xl shadow-indigo-500/15 flex flex-col justify-between relative">
          <div class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-indigo-600 text-[10px] font-bold tracking-wider text-white uppercase">Most Popular</div>
          <div>
            <h4 class="text-lg font-bold text-white mb-2">Team Pro</h4>
            <p class="text-slate-400 text-sm mb-6">For fast-moving engineering &amp; product teams.</p>
            <div class="text-4xl font-extrabold text-white mb-6">$49<span class="text-sm font-normal text-slate-500"> / month</span></div>
            <ul class="space-y-3 text-sm text-slate-300 mb-8">
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Unlimited autonomous agent swarms</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> 1,000,000 monthly execution tokens</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Advanced integrations (GitHub, Jira, Linear)</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Real-time priority agent execution</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Priority 24/7 technical support</li>
            </ul>
          </div>
          <button class="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold transition shadow-lg shadow-indigo-600/30">Start 14-Day Free Trial</button>
        </div>

        <!-- Enterprise Plan -->
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
          <div>
            <h4 class="text-lg font-bold text-white mb-2">Enterprise</h4>
            <p class="text-slate-400 text-sm mb-6">Dedicated deployment &amp; bespoke governance.</p>
            <div class="text-4xl font-extrabold text-white mb-6">Custom</div>
            <ul class="space-y-3 text-sm text-slate-300 mb-8">
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Dedicated isolated VPC deployment</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Custom fine-tuned domain models</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> SAML SSO, SCIM &amp; custom audit exports</li>
              <li class="flex items-center gap-2"><i data-lucide="check" class="w-4 h-4 text-indigo-400"></i> Dedicated customer success manager &amp; SLA</li>
            </ul>
          </div>
          <button class="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold transition">Contact Enterprise Sales</button>
        </div>
      </div>
    </div>
  </section>

  <!-- Contact Section -->
  <section id="contact" class="py-24 border-t border-slate-900">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <div class="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 flex items-center justify-center mx-auto mb-4">
        <i data-lucide="mail" class="w-6 h-6"></i>
      </div>
      <h2 class="text-3xl sm:text-4xl font-bold text-white mb-3">Get in Touch with Our Team</h2>
      <p class="text-sm sm:text-base text-slate-400 max-w-md mx-auto mb-10 leading-relaxed">
        Have questions about custom agent swarms, security compliance, or enterprise rollout? Reach out anytime!
      </p>

      <div class="p-6 sm:p-8 rounded-2xl bg-slate-900 border border-slate-800 text-left shadow-xl">
        <form id="contact-form" class="space-y-4" onsubmit="event.preventDefault(); document.getElementById('contact-success').classList.remove('hidden');">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1.5">Your Name</label>
              <input type="text" required placeholder="Alex Morgan" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500 transition">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1.5">Work Email</label>
              <input type="email" required placeholder="alex@company.com" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500 transition">
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1.5">Team Size &amp; Use Case</label>
            <input type="text" placeholder="e.g. 25 engineers, automating code review & research" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500 transition">
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1.5">Message</label>
            <textarea rows="3" required placeholder="Tell us about the workflows you want to automate..." class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500 transition resize-none"></textarea>
          </div>
          <button type="submit" class="w-full py-3.5 rounded-xl font-semibold bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white transition flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/25">
            <i data-lucide="send" class="w-4 h-4"></i>
            <span>Send Message</span>
          </button>
          <div id="contact-success" class="hidden p-4 rounded-xl bg-indigo-950/70 border border-indigo-500/40 text-xs text-indigo-300 text-center font-medium">
            ✓ Message sent successfully! Our solutions engineering team will reach out within 2 business hours.
          </div>
        </form>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="border-t border-slate-900 bg-slate-950 py-12 text-center text-xs text-slate-500">
    <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-3 font-semibold text-slate-300">
        <div class="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
        </div>
        <span>NexusAI Productivity Platform</span>
      </div>
      <p>&copy; 2026 NexusAI Technologies Inc. All rights reserved. Built with modern web standards.</p>
    </div>
  </footer>

  <script>
    lucide.createIcons();
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    if (btn && menu) {
      btn.addEventListener('click', () => menu.classList.toggle('hidden'));
    }
  </script>
</body>
</html>"""

def get_matching_mock_template(prompt: str) -> str:
    """Matches prompt context to an appropriate starter structure."""
    p = prompt.lower()
    if any(k in p for k in ["computer science", "cs student", "ai/ml student", "portfolio", "resume", "student", "cv"]):
        return generate_cs_ai_portfolio(prompt)
    return generate_saas_template(prompt)

def refine_mock_website(current_html: str, instruction: str) -> str:
    """
    Applies real, intelligent refinements to existing HTML in offline/mock mode.
    Delegates to the generalized refine_engine.
    """
    from app.core.refine_engine import apply_smart_refinement
    return apply_smart_refinement(current_html, instruction)
