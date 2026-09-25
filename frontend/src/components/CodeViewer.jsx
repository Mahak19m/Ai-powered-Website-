import React, { useState } from 'react';
import { Copy, Check, FileCode, Download, Layers } from 'lucide-react';
import { downloadHtml } from '../services/api';

export default function CodeViewer({
  htmlCode,
  projectName,
  pages = [],
  activePagePath = 'index.html',
  isMultiPage = false,
  onSelectPage
}) {
  const [copied, setCopied] = useState(false);

  const activePage = pages.find((p) => p.path === activePagePath);
  const currentCode = activePage ? activePage.html : htmlCode;
  const currentFilename = activePage ? activePage.path : `${projectName || 'index'}.html`;

  const handleCopy = async () => {
    if (!currentCode) return;
    try {
      await navigator.clipboard.writeText(currentCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy', err);
    }
  };

  const lineCount = currentCode ? currentCode.split('\n').length : 0;
  const byteCount = currentCode ? new Blob([currentCode]).size : 0;
  const kbFormatted = (byteCount / 1024).toFixed(1);

  return (
    <div className="flex flex-col h-full bg-dark-950 font-mono text-xs overflow-hidden">
      {/* Code Header Bar */}
      <div className="h-12 border-b border-slate-800 bg-dark-900/80 px-4 flex items-center justify-between z-10 select-none">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-indigo-400" />
          <span className="text-slate-300 font-medium">{currentFilename}</span>
          <span className="text-[10px] text-slate-500 font-sans">
            ({lineCount} lines • {kbFormatted} KB)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopy}
            disabled={!currentCode}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition disabled:opacity-40"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-sans">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span className="font-sans">Copy Code</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => downloadHtml(currentCode, currentFilename)}
            disabled={!currentCode}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-sans transition disabled:opacity-40"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download</span>
          </button>
        </div>
      </div>

      {/* Multi-Page File Switcher Bar (when multi-page) */}
      {isMultiPage && pages.length > 1 && (
        <div className="bg-dark-900/90 border-b border-slate-800/80 px-4 py-2 flex items-center gap-2 overflow-x-auto text-xs z-10">
          <div className="flex items-center gap-1 text-slate-400 font-medium mr-2 flex-shrink-0">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>Project Files:</span>
          </div>
          <div className="flex items-center gap-1.5">
            {pages.map((pg) => {
              const isActive = (pg.path === activePagePath);
              return (
                <button
                  key={pg.path}
                  type="button"
                  onClick={() => onSelectPage && onSelectPage(pg.path)}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-lg font-mono font-medium transition whitespace-nowrap ${
                    isActive
                      ? 'bg-indigo-600/90 text-white shadow-sm border border-indigo-500/50'
                      : 'bg-dark-950/80 text-slate-400 hover:text-slate-200 border border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <FileCode className="w-3 h-3 opacity-70" />
                  <span>{pg.path}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Code Content with Line Numbers */}
      <div className="flex-1 overflow-auto p-4 bg-dark-950 text-slate-300">
        {!currentCode ? (
          <div className="text-slate-500 italic p-4 text-center">
            No code generated yet. Send a prompt to see the code here.
          </div>
        ) : (
          <pre className="text-xs leading-relaxed font-mono whitespace-pre selection:bg-indigo-500/30">
            <code>{currentCode}</code>
          </pre>
        )}
      </div>
    </div>
  );
}
