import React from 'react';
import { Sparkles, Download, Archive, Settings, Plus, History, Code, Eye } from 'lucide-react';
import { downloadHtml, downloadZip } from '../services/api';

export default function Header({
  projectName,
  versionNumber,
  htmlCode,
  projectId,
  activeTab,
  setActiveTab,
  onNewProject,
  onToggleHistory,
  onOpenSettings,
  isHistoryOpen
}) {
  return (
    <header className="h-16 border-b border-slate-800 bg-dark-950/90 backdrop-blur px-5 flex items-center justify-between z-30 select-none">
      {/* Left: Brand & Project Name */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/30">
            <Sparkles className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-sm text-white tracking-tight leading-none">WebCraft AI</span>
            <span className="text-[10px] text-slate-400 leading-tight mt-0.5">Prompt to Live Site</span>
          </div>
        </div>

        <div className="h-5 w-px bg-slate-800 hidden sm:block"></div>

        {/* Project Name & Version Pill */}
        <div className="hidden sm:flex items-center gap-2">
          <span className="text-xs font-medium text-slate-300 max-w-[200px] truncate">
            {projectName || 'Untitled Project'}
          </span>
          {versionNumber > 0 && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-indigo-400 border border-slate-700">
              v{versionNumber}
            </span>
          )}
        </div>
      </div>

      {/* Center: Preview vs Code View Mode Toggle */}
      <div className="flex items-center bg-dark-900 border border-slate-800 rounded-xl p-1 text-xs">
        <button
          type="button"
          onClick={() => setActiveTab('preview')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition ${
            activeTab === 'preview'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Eye className="w-3.5 h-3.5" />
          <span>Preview</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('code')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition ${
            activeTab === 'code'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Code className="w-3.5 h-3.5" />
          <span>Code</span>
        </button>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onNewProject}
          className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition"
          title="Start fresh project"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Site</span>
        </button>

        <button
          type="button"
          onClick={onToggleHistory}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
            isHistoryOpen
              ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40'
              : 'bg-slate-800/80 hover:bg-slate-700 text-slate-300 border-slate-700'
          }`}
          title="Version history"
        >
          <History className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Versions</span>
        </button>

        {/* Export Buttons */}
        {htmlCode && (
          <>
            <button
              type="button"
              onClick={() => downloadHtml(htmlCode, `${projectName || 'website'}.html`)}
              className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition"
              title="Download standalone single HTML file"
            >
              <Download className="w-3.5 h-3.5" />
              <span>HTML</span>
            </button>

            <button
              type="button"
              onClick={() => projectId && downloadZip(projectId)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white shadow-sm shadow-indigo-600/30 transition"
              title="Export complete deployment ZIP package"
            >
              <Archive className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Export ZIP</span>
            </button>
          </>
        )}

        {/* Settings modal button */}
        <button
          type="button"
          onClick={onOpenSettings}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition ml-1"
          title="AI API Settings"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
