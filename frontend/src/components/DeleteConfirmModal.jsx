import React, { useEffect, useRef } from 'react';
import { Trash2, AlertTriangle, Loader2, X } from 'lucide-react';

export default function DeleteConfirmModal({
  isOpen,
  project,
  isDeleting,
  onConfirm,
  onClose
}) {
  const cancelButtonRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;

    // Focus cancel button by default for safety
    cancelButtonRef.current?.focus();

    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && !isDeleting) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isDeleting, onClose]);

  if (!isOpen || !project) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Top Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 id="delete-modal-title" className="text-base font-semibold text-white">
                Delete Project
              </h3>
              <p className="text-xs text-slate-400">This action is permanent and cannot be undone</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            aria-label="Close modal"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition disabled:opacity-50"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <p className="text-sm text-slate-300 leading-relaxed">
            Are you sure you want to delete <span className="font-semibold text-white bg-slate-800 px-2 py-0.5 rounded border border-slate-700">{project.name}</span>?
          </p>
          <div className="p-3.5 rounded-xl bg-rose-500/5 border border-rose-500/15 text-xs text-rose-300 space-y-1.5">
            <p className="font-semibold flex items-center gap-1.5 text-rose-300">
              <Trash2 className="w-3.5 h-3.5" />
              All associated data will be removed:
            </p>
            <ul className="list-disc list-inside text-rose-300/80 text-[11px] pl-1 space-y-0.5">
              <li>{project.versions_count || 1} saved version snapshot(s)</li>
              <li>Generated HTML code and multi-page assets</li>
              <li>Database and local project storage</li>
            </ul>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 p-5 bg-slate-950/40 border-t border-slate-800">
          <button
            ref={cancelButtonRef}
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            className="px-4 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-700 transition focus:outline-none focus:ring-2 focus:ring-slate-500"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => onConfirm(project.id)}
            disabled={isDeleting}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-600/30 transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-rose-500"
          >
            {isDeleting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Deleting...</span>
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4" />
                <span>Delete Project</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
