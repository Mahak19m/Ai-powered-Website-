import React, { useState } from 'react';
import { Copy, Check, FileCode, Download, Layers, Sparkles } from 'lucide-react';
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

  const lines = currentCode ? currentCode.split('\n') : [];
  const lineCount = lines.length;
  const byteCount = currentCode ? new Blob([currentCode]).size : 0;
  const kbFormatted = (byteCount / 1024).toFixed(1);

  return (
    <div className="flex flex-col h-full bg-dark-950 font-mono text-xs overflow-hidden">
      {/* Code Header Bar */}
      <div className="h-12 border-b border-slate-800 bg-dark-900/80 px-4 flex items-center justify-between z-10 select-none">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-indigo-400" />
          <span className="text-slate-300 font-medium truncate max-w-[200px]">{currentFilename}</span>
          <span className="text-[10px] text-slate-500 font-sans hidden sm:inline">
            ({lineCount} lines • {kbFormatted} KB)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopy}
            disabled={!currentCode}
            aria-label="Copy code to clipboard"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition disabled:opacity-40"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-sans text-xs">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span className="font-sans text-xs">Copy Code</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => downloadHtml(currentCode, currentFilename)}
            disabled={!currentCode}
            aria-label="Download HTML file"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-sans text-xs transition disabled:opacity-40"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Download</span>
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
      <div className="flex-1 overflow-auto bg-dark-950 text-slate-300">
        {!currentCode ? (
          <div className="h-full flex flex-col items-center justify-center p-8 text-center">
            <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mx-auto mb-3">
              <Sparkles className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-semibold text-slate-300 mb-1">No Code Generated Yet</h4>
            <p className="text-xs text-slate-500 max-w-xs mx-auto">
              Generate a website to inspect, copy, and export production-ready HTML and Tailwind code here.
            </p>
          </div>
        ) : (
          <div className="flex min-w-full font-mono text-xs leading-relaxed">
            {/* Line numbers column */}
            <div className="select-none py-4 px-3 text-right text-slate-600 bg-dark-950/80 border-r border-slate-800/80 sticky left-0 min-w-[3.5rem]">
              {lines.map((_, i) => (
                <div key={i}>{i + 1}</div>
              ))}
            </div>

            {/* Code content */}
            <pre className="p-4 flex-1 whitespace-pre overflow-x-auto selection:bg-indigo-500/30">
              <code>{currentCode}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
