import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export default function Toast({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => {
      onClose();
    }, 4000);
    return () => clearTimeout(timer);
  }, [toast, onClose]);

  if (!toast) return null;

  const isSuccess = toast.type === 'success';
  const isError = toast.type === 'error';
  const isWarning = toast.type === 'warning';

  const styleClass = isSuccess
    ? 'bg-emerald-950/90 border-emerald-500/40 text-emerald-200'
    : isError
    ? 'bg-rose-950/90 border-rose-500/40 text-rose-200'
    : isWarning
    ? 'bg-amber-950/90 border-amber-500/40 text-amber-200'
    : 'bg-slate-900/95 border-slate-700 text-slate-200';

  return (
    <div
      role="status"
      aria-live="polite"
      className={`fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-2xl shadow-2xl border backdrop-blur-md transition-all duration-300 animate-in fade-in slide-in-from-bottom-5 max-w-sm sm:max-w-md ${styleClass}`}
    >
      {isSuccess && <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />}
      {isError && <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />}
      {isWarning && <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0" />}
      {!isSuccess && !isError && !isWarning && <Info className="w-5 h-5 text-indigo-400 flex-shrink-0" />}

      <div className="text-xs font-medium leading-relaxed flex-1">
        {toast.message}
      </div>

      <button
        type="button"
        onClick={onClose}
        aria-label="Dismiss notification"
        className="text-slate-400 hover:text-white p-1 rounded-lg transition"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
