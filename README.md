# 🌐 WebCraft AI - AI-Powered Website Builder

An AI-driven website builder inspired by v0, Bolt, and Lovable. Enter a prompt in natural language and watch the AI design, code, and render a responsive, modern website in real time with interactive preview, viewport switching, and one-click export.

---

## 🚀 Quick Start

### 1. Start the Backend (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
Backend runs at `http://127.0.0.1:8000`.

### 2. Start the Frontend (React + Vite + Tailwind)
```bash
cd frontend
npm.cmd run dev
```
Frontend runs at `http://localhost:5173`. Open this URL in your browser!

---

## 🌟 Key Features

- **Prompt to Live Site**: Generate production-ready HTML5 + Tailwind CSS + Lucide Icons websites from natural language.
- **Real-Time Token Streaming**: Watch the website being constructed live with Server-Sent Events (SSE).
- **Responsive Viewport Switcher**: Toggle seamlessly between **Desktop** (100%), **Tablet** (768px), and **Mobile** (375px) previews with phone/tablet shell frames.
- **Iterative Conversational Refinements**: Chat with the AI to refine and modify the site (e.g. *"Change color scheme to emerald"*, *"Add a 3-tier pricing table"*, *"Add an interactive FAQ accordion"*).
- **Version Timeline & Instant Rollback**: Every generation and refinement is snapshot. Restore any previous version with 1 click.
- **Code Inspector**: Switch between the live interactive preview and formatted code viewer with syntax highlighting and copy-to-clipboard.
- **Zero-Config Demo Mode**: Works out of the box with built-in modern website templates even without an API key.
- **Custom Gemini API Key**: Click the Settings gear in the top bar to plug in your Google Gemini API key (`gemini-2.5-flash` or `gemini-1.5-pro`).
- **Export Anywhere**: Download as a standalone `.html` file or export a complete deployment `.zip` archive ready for Netlify, Vercel, or GitHub Pages.

---

## 🛠️ Project Structure

```
ai-website-builder/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_generate.py   # Streaming generation (SSE) & prompt orchestration
│   │   │   ├── routes_projects.py   # Project versions, history, and CRUD
│   │   │   └── routes_export.py     # Standalone HTML and ZIP export
│   │   ├── core/
│   │   │   ├── config.py            # Environment variables & settings
│   │   │   ├── prompts.py           # System prompts for high-quality website design
│   │   │   ├── mock_templates.py    # Zero-config starter templates
│   │   │   └── llm_service.py       # Google Gemini SDK streaming client
│   │   └── main.py                  # FastAPI entry point & CORS
│   ├── requirements.txt             # FastAPI, Uvicorn, Google GenAI SDK
│   └── test_api.py                  # Automated smoke test suite
│
└── frontend/                        # React + Vite + Tailwind CSS
    ├── src/
    │   ├── components/
    │   │   ├── Header.jsx           # Top navbar, project actions, export buttons
    │   │   ├── ChatPanel.jsx        # Prompt studio, conversation thread, quick templates
    │   │   ├── PreviewFrame.jsx     # Sandboxed live iframe with viewport controls
    │   │   ├── CodeViewer.jsx       # Syntax viewer and copy button
    │   │   ├── VersionHistory.jsx   # Timeline of versions with instant rollback
    │   │   └── SettingsModal.jsx    # Gemini API key & model settings
    │   ├── services/
    │   │   └── api.js               # API service & SSE stream consumer
    │   ├── App.jsx                  # Split-pane workbench layout
    │   └── main.jsx
    └── package.json
```
