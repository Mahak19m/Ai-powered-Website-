import React, { useState, useEffect, useRef } from 'react';
import { Plus, Sparkles, Loader2, X, Laptop } from 'lucide-react';

const SUGGESTIONS = [
  'Modern AI Agent SaaS Platform',
  'Cloud Architect Portfolio & Resume',
  'Fintech Payment Gateway Landing Page',
  'Cybersecurity Startup with Pricing',
  'Artisan Coffee Roastery & Storefront'
];

export default function CreateProjectModal({
  isOpen,
  isCreating,
  onSubmit,
  onClose
}) {
  const [projectName, setProjectName] = useState('');
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setProjectName('');
      setError('');
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);

      const handleKeyDown = (e) => {
        if (e.key === 'Escape' && !isCreating) {
          onClose();
        }
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, isCreating, onClose]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = projectName.trim();
    if (!trimmed) {
      setError('Please provide a project name.');
      inputRef.current?.focus();
      return;
    }
    onSubmit(trimmed);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="create-project-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Top Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 id="create-project-title" className="text-base font-semibold text-white">
                Create New Project
              </h3>
              <p className="text-xs text-slate-400">Set up a website project and start designing in the Studio</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isCreating}
            aria-label="Close modal"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition disabled:opacity-50"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit}>
          <div className="p-6 space-y-5">
            <div>
              <label htmlFor="projectName" className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Project Name
              </label>
              <input
                ref={inputRef}
                id="projectName"
                type="text"
                value={projectName}
                onChange={(e) => {
                  setProjectName(e.target.value);
                  if (error) setError('');
                }}
                disabled={isCreating}
                placeholder="e.g. NextGen SaaS Landing Page"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
              />
              {error && (
                <p className="text-xs text-rose-400 mt-1.5 font-medium">{error}</p>
              )}
            </div>

            {/* Quick Inspiration Chips */}
            <div>
              <span className="block text-[11px] font-medium text-slate-400 mb-2">
                Or pick an idea to get started quickly:
              </span>
              <div className="flex flex-wrap gap-2">
                {SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => {
                      setProjectName(suggestion);
                      if (error) setError('');
                      inputRef.current?.focus();
                    }}
                    className="text-xs px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition active:scale-95 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>

            {/* Info highlight */}
            <div className="p-3.5 rounded-xl bg-indigo-500/5 border border-indigo-500/15 flex items-start gap-3">
              <Laptop className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
              <p className="text-[11px] text-slate-300 leading-relaxed">
                After creation, WebCraft AI Studio will launch where you can prompt single-page or multi-page websites, preview live code, and refine iteratively.
              </p>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-3 p-5 bg-slate-950/40 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              disabled={isCreating}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-700 transition focus:outline-none focus:ring-2 focus:ring-slate-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isCreating}
              className="flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-lg shadow-indigo-600/30 transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Creating Studio...</span>
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Create & Open Studio</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
