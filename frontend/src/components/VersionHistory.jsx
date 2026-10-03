import React, { useEffect } from 'react';
import { X, History, Check, RotateCcw } from 'lucide-react';

export default function VersionHistory({
  isOpen,
  onClose,
  versions = [],
  currentVersionId,
  onRestoreVersion
}) {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const formatTimestamp = (isoString) => {
    if (!isoString) return 'Recent';
    try {
      const d = new Date(isoString);
      if (isNaN(d.getTime())) return isoString;
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoString;
    }
  };

  return (
    <>
      {/* Backdrop for mobile & tablet */}
      <div
        onClick={onClose}
        className="fixed inset-0 z-30 bg-black/50 backdrop-blur-xs lg:hidden animate-in fade-in"
      />

      {/* Slide-out Panel */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Version Timeline"
        className="fixed inset-y-0 right-0 z-40 w-80 sm:w-96 bg-dark-900 border-l border-slate-800 shadow-2xl flex flex-col animate-in slide-in-from-right duration-200 text-slate-200"
      >
        {/* Header */}
        <div className="h-16 px-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <History className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Version Timeline</h3>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-indigo-400 border border-slate-700">
              {versions.length}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close timeline"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {versions.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-xs">
              No versions recorded yet. Generate a website to start versioning.
            </div>
          ) : (
            versions
              .slice()
              .reverse()
              .map((v, index) => {
                const versionNum = versions.length - index;
                const isCurrent = v.id === currentVersionId;

                return (
                  <div
                    key={v.id}
                    className={`p-3.5 rounded-xl border transition ${
                      isCurrent
                        ? 'bg-indigo-950/40 border-indigo-500/50 shadow-md shadow-indigo-500/10'
                        : 'bg-dark-950/60 border-slate-800/80 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold font-mono text-indigo-400">
                          v{versionNum}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-medium">
                          {v.version_type || (index === versions.length - 1 ? 'initial' : 'refinement')}
                        </span>
                      </div>

                      {isCurrent ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/40">
                          <Check className="w-2.5 h-2.5" /> Active
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => onRestoreVersion(v.id)}
                          className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-indigo-600 px-2.5 py-1 rounded-lg border border-slate-700 transition"
                        >
                          <RotateCcw className="w-3 h-3" /> Restore
                        </button>
                      )}
                    </div>

                    <p className="text-xs text-slate-300 line-clamp-2 mb-2 font-normal leading-relaxed">
                      "{v.prompt}"
                    </p>

                    <div className="text-[10px] text-slate-500 flex items-center justify-between">
                      <span>{formatTimestamp(v.created_at)}</span>
                      <span className="font-mono text-[9px] text-slate-600">ID: {v.id.slice(0, 8)}</span>
                    </div>
                  </div>
                );
              })
          )}
        </div>
      </div>
    </>
  );
}
