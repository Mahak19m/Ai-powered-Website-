# WebCraft AI

> **Autonomous Full-Stack AI Website Builder** — Convert natural-language prompts into modern, responsive, multi-page websites in real time. Features iterative conversational refinement, version history snapshots, instant rollback, interactive sandboxed preview, code inspection, and one-click production export.

---

## 📑 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Running Locally](#running-locally)
- [API Overview](#api-overview)
- [Testing](#testing)
- [Deployment Considerations](#deployment-considerations)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Overview

**WebCraft AI** is an AI-powered website design and development platform inspired by modern generative tooling (v0, Bolt, Lovable). Users describe a website in plain English—whether a single-page SaaS landing page, portfolio, or a full multi-page portal. The system plans the layout, synthesizes semantic HTML5, utility-first Tailwind CSS, and Lucide icons, and streams the output directly into an interactive live preview.

Every prompt and iterative modification creates an immutable snapshot stored in a database, allowing users to inspect code, switch viewports, test inter-page navigation, roll back to any previous version, and export complete production-ready packages.

---

## Features

- **AI Prompt-to-Website Generation**: Synthesize production-ready responsive websites from high-level natural language descriptions.
- **Real-Time Token Streaming**: Watch the user interface materialize live through Server-Sent Events (SSE).
- **Natural-Language Refinement**: Iteratively modify specific sections or global styling (e.g., *"Change primary theme to dark emerald"*, *"Add a 24/7 hotline banner"*, *"Add a 3-tier pricing table"*).
- **Interactive Live Preview**: Sandboxed iframe preview with smooth scrolling, working relative anchor navigation, and zero script leaking.
- **Responsive Viewport Controls**: One-click switching between **Desktop** (100%), **Tablet** (768px), and **Mobile** (375px) device preview frames.
- **Code Viewer & Inspector**: Formatted HTML code viewer with synchronized line-number gutter, size metrics, and one-click clipboard copying.
- **Version History & Rollback**: Automatic snapshotting of every generation and refinement with one-click restore to any previous snapshot.
- **Multi-Page Website Generation**: Detects multi-page intent and generates coordinated pages (e.g., `index.html`, `pricing.html`, `contact.html`) with cohesive branding, shared headers, and footers.
- **Inter-Page Link Navigation**: Working relative links between generated pages inside the live preview.
- **HTML & ZIP Export**: Export as a standalone single-file HTML or download a complete deployment ZIP bundle with all pages and a generated `README.md`.
- **Project Dashboard**: Dedicated entry screen showing all projects, created/updated timestamps, version counts, and page types.
- **Search & Sorting**: Instant client-side search by project name or ID, and sorting by *Recently Updated*, *Newest First*, *Alphabetical*, or *Most Versions*.
- **Database Persistence**: Powered by SQLAlchemy with an isolated repository pattern; defaults to SQLite and switches to PostgreSQL via `DATABASE_URL`.
- **Responsive UI**: Fully responsive workbench and dashboard optimized for desktop, tablet, and mobile screens.
- **Error Handling & Retry**: In-place prompt retry actions, validation warnings on empty prompts, connection offline banners, and safe deletion modals.
- **Accessibility Support**: Keyboard focus management, Escape key drawer/modal dismissal, ARIA dialog roles, and screen-reader labels.

---

## Tech Stack

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Server**: Uvicorn
- **Validation**: Pydantic v2
- **ORM & Database Layer**: SQLAlchemy 2.0 (Repository Pattern)

### Artificial Intelligence
- **LLM SDK**: Google Gemini (`google-genai`)
- **Supported Models**: `gemini-2.5-flash` (default, fast), `gemini-1.5-pro` (high logic)
- **Zero-Config Fallback**: Built-in template generator allows running without an API key for demos.

### Database
- **Development**: SQLite (`sqlite:///./webcraft.db`)
- **Production Compatible**: PostgreSQL (via standard `DATABASE_URL`)

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                   React 18 Frontend                    │
│   (Dashboard, Studio Workbench, PreviewFrame, Code)   │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP REST / SSE Stream
                            ▼
┌────────────────────────────────────────────────────────┐
│                    FastAPI Backend                     │
│  ├── /api/projects  (CRUD, listing, rollback)          │
│  ├── /api/generate  (SSE stream prompt-to-site)        │
│  ├── /api/refine    (SSE stream smart refinement)      │
│  ├── /api/export    (HTML & multi-page ZIP)            │
│  └── /api/health    (Liveness check)                   │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
               ▼                           ▼
┌───────────────────────────────┐ ┌──────────────────────┐
│       Generation Engine       │ │  ProjectRepository   │
│  ├── Multi-Page Planner       │ │  ├── ProjectModel    │
│  ├── Refine / Smart Replace   │ │  └── VersionModel    │
│  └── Gemini LLM / Templates   │ └──────────┬───────────┘
└───────────────────────────────┘            │
                                             ▼
                                  ┌──────────────────────┐
                                  │   SQLite Database    │
                                  │  (or PostgreSQL DB)  │
                                  └──────────────────────┘
```

### Major Directories

- `backend/app/api/`: REST and Server-Sent Event route controllers (`routes_projects.py`, `routes_generate.py`, `routes_export.py`).
- `backend/app/core/`: Multi-page generation engine, AST-like refinement replacement engine, prompts, and LLM streaming service.
- `backend/app/db/`: SQLAlchemy engine session factory, ORM models (`ProjectModel`, `VersionModel`), and CRUD repository pattern.
- `frontend/src/components/`: Reusable modular components (`Dashboard`, `ChatPanel`, `PreviewFrame`, `CodeViewer`, `VersionHistory`, `Header`, modals).
- `frontend/src/services/api.js`: Unified client-side HTTP communication, SSE reader, and localStorage credential management.

---

## Project Structure

```
webcraft-ai-project/
├── .env.example                       # Environment configuration template
├── .gitignore                          # Git ignore rules for secrets, builds, DB
├── README.md                           # Project documentation
├── run.bat                             # Windows launch helper script
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_export.py        # Single HTML & ZIP export endpoints
│   │   │   ├── routes_generate.py      # SSE website generation & refinement
│   │   │   └── routes_projects.py      # Project listing, retrieval, rollback, delete
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic configuration & env loading
│   │   │   ├── llm_service.py          # Google Gemini SDK streaming client
│   │   │   ├── mock_templates.py       # Zero-config starter templates
│   │   │   ├── multi_page_engine.py    # Multi-page layout & navigation coordinator
│   │   │   ├── prompts.py              # LLM system prompts and rules
│   │   │   └── refine_engine.py        # Smart section replacement engine
│   │   ├── db/
│   │   │   ├── models.py               # SQLAlchemy ProjectModel & VersionModel
│   │   │   ├── repository.py           # ProjectRepository with CRUD & versioning
│   │   │   └── session.py              # Engine factory & DB session manager
│   │   ├── storage/
│   │   │   └── projects/               # Local JSON fallback mirrors (.gitkeep)
│   │   └── main.py                     # FastAPI application entry & CORS
│   ├── requirements.txt                # Python backend dependencies
│   ├── run_all_tests.py                # Master test runner (18 test suites)
│   ├── test_api.py                     # Backend connectivity & smoke tests
│   ├── test_database_layer.py          # Database models, CRUD, & rollback tests
│   ├── test_exact_refinement_suite.py  # Precision section refinement tests
│   ├── test_exact_skills.py            # Technical skills section replacement tests
│   ├── test_multi_page_suite.py        # Multi-page routing, export, & rollback tests
│   ├── test_phase3_dashboard_api.py    # Dashboard workflow integration tests
│   ├── test_phase4_e2e_integration.py  # 23-step E2E workflow & 7 edge cases
│   └── test_user_scenario.py           # Real-world student portfolio scenario
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatPanel.jsx           # Prompt studio with quick starters & retry
    │   │   ├── CodeViewer.jsx          # Code inspector with line numbers & copy
    │   │   ├── CreateProjectModal.jsx  # New project modal with starter chips
    │   │   ├── Dashboard.jsx           # Project dashboard with grid/list & search
    │   │   ├── DeleteConfirmModal.jsx  # Safe project deletion confirmation modal
    │   │   ├── Header.jsx              # Navbar, mode switcher, export buttons
    │   │   ├── PreviewFrame.jsx        # Sandbox preview iframe & viewport tools
    │   │   ├── SettingsModal.jsx       # Gemini API key & model selection modal
    │   │   ├── Toast.jsx               # Floating notifications (success, error, warning)
    │   │   └── VersionHistory.jsx      # Slide-out timeline with restore actions
    │   ├── services/
    │   │   └── api.js                  # Client API service & SSE stream parser
    │   ├── App.jsx                     # Top-level view routing & workbench state
    │   ├── index.css                   # Tailwind CSS directives
    │   └── main.jsx                    # React DOM entry point
    ├── package.json                    # Frontend dependencies & scripts
    ├── tailwind.config.js              # Tailwind custom theme & color tokens
    └── vite.config.js                  # Vite dev server & /api proxy configuration
```

---

## Prerequisites

- **Python**: 3.10, 3.11, 3.12, or 3.13
- **Node.js**: 18.x or higher (with npm)
- **Google Gemini API Key** *(Optional)*:
  - You can obtain a free key at [Google AI Studio](https://aistudio.google.com/app/apikey).
  - If no key is configured, WebCraft AI automatically falls back to its built-in zero-config generation engine.

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd webcraft-ai-project
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

---

## Environment Configuration

Copy the `.env.example` template to `.env` in the project root or backend directory:

```bash
cp .env.example .env
```

### Configuration Variables

| Variable | Default Value | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(Empty)* | Google Gemini API key. If omitted, built-in templates are used. |
| `DEFAULT_MODEL` | `gemini-2.5-flash` | Default Gemini model (`gemini-2.5-flash` or `gemini-1.5-pro`). |
| `DATABASE_URL` | `sqlite:///./webcraft.db` | SQLAlchemy database URL. Change to PostgreSQL for production. |
| `PORT` | `8000` | Port for the FastAPI backend server. |
| `VITE_API_BASE_URL` | `/api` | Base URL for frontend API requests (proxied locally by Vite). |

> **Security Note**: Never commit your `.env` file or real API keys to version control. The repository `.gitignore` automatically excludes all `.env` files.

---

## Running Locally

### Option A: Using Windows Helper Script

Double-click `run.bat` in the root folder, or run:

```cmd
run.bat
```

This launches both the backend and frontend dev servers concurrently in separate windows.

### Option B: Manual Startup

**Terminal 1 — Backend (FastAPI)**:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
Backend runs at: `http://127.0.0.1:8000`  
Health check: `http://127.0.0.1:8000/api/health`

**Terminal 2 — Frontend (React + Vite)**:
```bash
cd frontend
npm run dev
```
Frontend runs at: `http://localhost:5173`

---

## API Overview

The FastAPI backend exposes the following REST and SSE endpoints under `/api`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health and liveness check. Returns status and API key detection. |
| `GET` | `/api/projects` | List all saved projects with timestamps, page counts, and version numbers. |
| `POST` | `/api/projects` | Create a new project record in the database. |
| `GET` | `/api/projects/{id}` | Retrieve complete project details including all version snapshots. |
| `DELETE` | `/api/projects/{id}` | Delete a project and cascade delete all its version snapshots. |
| `POST` | `/api/projects/{id}/revert/{version_id}` | Revert active project version to an older snapshot. |
| `POST` | `/api/generate` | Server-Sent Events (SSE) stream for generating websites from natural language. |
| `POST` | `/api/refine` | Server-Sent Events (SSE) stream for smart section or multi-page refinements. |
| `POST` | `/api/export/html` | Export and download single-page HTML as an attachment. |
| `GET` | `/api/export/project/{id}/zip` | Bundle and download complete website project as a deployment ZIP archive. |

---

## Testing

The project includes an automated test suite verifying database operations, SSE generation, exact-list refinements, multi-page routing, export bundling, user workflows, and edge cases.

### Run Backend Test Suite

From the `backend/` directory:

```bash
python run_all_tests.py
```

**Expected Baseline**:
```
============================================================
RESULTS: Total=18, Passed=18, Failed=0
============================================================
ALL TESTS PASSED SUCCESSFULLY! 100% OK
```

### Run Frontend Production Build

From the `frontend/` directory:

```bash
npm run build
```

**Expected Result**: Clean build output in `frontend/dist/` with zero TypeScript/JavaScript compilation errors.

---

## Deployment Considerations

### Frontend
- Build production assets: `npm run build`.
- The output directory `frontend/dist/` can be deployed to any static host (Vercel, Netlify, Cloudflare Pages, AWS S3 + CloudFront).
- Configure `VITE_API_BASE_URL` to point to your live backend domain (e.g. `https://api.yourdomain.com/api`).

### Backend
- Deploy the FastAPI application using production ASGI servers such as Uvicorn or Gunicorn with Uvicorn workers.
- Example production startup command:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
  ```
- Compatible with platforms such as Render, Railway, Fly.io, AWS ECS, or Google Cloud Run.

### Database
- **Local / Single Instance**: SQLite (`sqlite:///./webcraft.db`) works out of the box with zero external setup.
- **Production / Scaled**: Set `DATABASE_URL` to a managed PostgreSQL connection string:
  ```bash
  DATABASE_URL=postgresql://user:password@db-host:5432/webcraft
  ```
  The SQLAlchemy repository automatically detects PostgreSQL and provisions the schema via `init_db()` on application boot.

---

## Known Limitations

1. **SQLite File Concurrency**: When running on SQLite, writes use a file lock. In horizontally scaled multi-container cloud deployments, configure `DATABASE_URL` to point to a managed PostgreSQL database.
2. **Client-Side Key Storage**: User-provided Gemini API keys configured via the in-app Settings modal are stored in the browser's `localStorage` for privacy and convenience. Multi-tenant team authentication is not yet implemented.
3. **External Asset Loading**: Generated sites reference Tailwind CSS via CDN and Lucide icons via SVG/script tags; an active internet connection is required to load these assets in the preview iframe.

---

## Future Improvements

- **User Authentication & Workspaces**: Multi-tenant team collaboration and access control.
- **Cloud Database Provisioning**: Automated migrations using Alembic.
- **S3 / Cloud Storage Integration**: Direct asset storage for user-uploaded images and media.
- **Custom Domain Publishing**: One-click DNS binding and automated SSL certificate issuance.
- **Component Library Extensibility**: Support for exporting React/Tailwind component JSX alongside HTML.

---

## License

This project is prepared for demonstration, portfolio, and educational evaluation. A software license (such as MIT or Apache 2.0) can be designated prior to commercial or public distribution.
