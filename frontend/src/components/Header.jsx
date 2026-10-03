import React, { useState } from 'react';
import { Sparkles, Download, Archive, Settings, Plus, History, Code, Eye, ArrowLeft, Loader2 } from 'lucide-react';
import { downloadHtml, downloadZip } from '../services/api';

export default function Header({
  projectName,
  versionNumber,
  htmlCode,
  projectId,
  activeTab,
  setActiveTab,
  onNewProject,
  onBackToDashboard,
  onToggleHistory,
  onOpenSettings,
  isHistoryOpen,
  isGenerating
}) {
  const [isExportingZip, setIsExportingZip] = useState(false);

  const handleZipExport = () => {
    if (!projectId || isExportingZip) return;
    setIsExportingZip(true);
    try {
      downloadZip(projectId);
    } finally {
      setTimeout(() => setIsExportingZip(false), 1200);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-dark-950/90 backdrop-blur px-4 sm:px-5 flex items-center justify-between z-30 select-none">
      {/* Left: Brand & Dashboard Return & Project Name */}
      <div className="flex items-center gap-2.5 sm:gap-4">
        {/* Back to Dashboard Button */}
        <button
          type="button"
          onClick={onBackToDashboard}
          disabled={isGenerating}
          aria-label="Back to projects dashboard"
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-medium text-slate-300 hover:text-white border border-slate-800 hover:border-slate-700 transition shadow-sm disabled:opacity-40"
          title="Back to Projects Dashboard"
        >
          <ArrowLeft className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden sm:inline">Dashboard</span>
        </button>

        <div className="h-5 w-px bg-slate-800"></div>

        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/30">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <div className="hidden lg:flex flex-col">
            <span className="font-bold text-xs text-white tracking-tight leading-none">WebCraft AI</span>
            <span className="text-[9px] text-slate-400 leading-tight mt-0.5">Prompt to Live Site</span>
          </div>
        </div>

        <div className="h-5 w-px bg-slate-800 hidden md:block"></div>

        {/* Project Name & Version Pill */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-white max-w-[120px] sm:max-w-[200px] truncate" title={projectName}>
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
      <div className="flex items-center bg-dark-900 border border-slate-800 rounded-xl p-1 text-xs" role="tablist" aria-label="Editor view modes">
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === 'preview'}
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
          role="tab"
          aria-selected={activeTab === 'code'}
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
          disabled={isGenerating}
          aria-label="Create new website project"
          className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition disabled:opacity-40"
          title="Start fresh project"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Site</span>
        </button>

        <button
          type="button"
          onClick={onToggleHistory}
          aria-label="Toggle version history"
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
              disabled={isGenerating}
              aria-label="Download single-page HTML"
              className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition disabled:opacity-40"
              title="Download standalone single HTML file"
            >
              <Download className="w-3.5 h-3.5" />
              <span>HTML</span>
            </button>

            <button
              type="button"
              onClick={handleZipExport}
              disabled={isGenerating || isExportingZip || !projectId}
              aria-label="Export complete website ZIP archive"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-xs font-medium text-white shadow-sm shadow-indigo-600/30 transition"
              title="Export complete deployment ZIP package"
            >
              {isExportingZip ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span className="hidden sm:inline">Exporting...</span>
                </>
              ) : (
                <>
                  <Archive className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Export ZIP</span>
                </>
              )}
            </button>
          </>
        )}

        {/* Settings modal button */}
        <button
          type="button"
          onClick={onOpenSettings}
          aria-label="AI API settings"
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition ml-1"
          title="AI API Settings"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
