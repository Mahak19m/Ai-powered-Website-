import React, { useState, useEffect } from 'react';
import { X, Key, ShieldCheck, ExternalLink, RotateCcw } from 'lucide-react';
import { getStoredApiKey, setStoredApiKey, getStoredModel, setStoredModel } from '../services/api';

export default function SettingsModal({ isOpen, onClose }) {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gemini-2.5-flash');
  const [savedStatus, setSavedStatus] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setApiKey(getStoredApiKey());
      setModel(getStoredModel());
      setSavedStatus(false);

      const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
          onClose();
        }
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSave = () => {
    setStoredApiKey(apiKey.trim());
    setStoredModel(model);
    setSavedStatus(true);
    setTimeout(() => {
      onClose();
    }, 600);
  };

  const handleClearKey = () => {
    setApiKey('');
    setStoredApiKey('');
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in duration-200"
    >
      <div className="w-full max-w-lg rounded-2xl bg-dark-900 border border-slate-800 p-6 shadow-2xl relative text-slate-200">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          aria-label="Close settings"
          className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
            <Key className="w-5 h-5" />
          </div>
          <div>
            <h2 id="settings-modal-title" className="text-lg font-bold text-white">AI Provider Settings</h2>
            <p className="text-xs text-slate-400">Configure your Google Gemini API key for live generation.</p>
          </div>
        </div>

        {/* Notice */}
        <div className="mb-5 p-3.5 rounded-xl bg-indigo-950/40 border border-indigo-500/20 text-xs text-indigo-300 flex items-start gap-2.5 leading-relaxed">
          <ShieldCheck className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
          <div>
            <span>Your API key is saved locally in your browser and used directly for generations. If left empty, the builder seamlessly uses the built-in demo engine!</span>
          </div>
        </div>

        {/* Form Fields */}
        <div className="space-y-4 mb-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label htmlFor="apiKeyInput" className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Gemini API Key
              </label>
              {apiKey && (
                <button
                  type="button"
                  onClick={handleClearKey}
                  className="text-[11px] text-slate-400 hover:text-rose-400 inline-flex items-center gap-1 transition"
                >
                  <RotateCcw className="w-3 h-3" /> Clear Key
                </button>
              )}
            </div>
            <div className="relative">
              <input
                id="apiKeyInput"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="AIzaSy..."
                className="w-full px-4 py-2.5 rounded-xl bg-dark-950 border border-slate-700 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition font-mono"
              />
            </div>
            <div className="mt-1.5 flex justify-between items-center text-[11px] text-slate-500">
              <span>Don't have a key yet?</span>
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 transition"
              >
                Get a free key on Google AI Studio <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Model Selection
            </label>
            <div className="grid grid-cols-2 gap-2.5">
              {[
                { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', badge: 'Fastest' },
                { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', badge: 'High Logic' },
              ].map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setModel(m.id)}
                  className={`p-3 rounded-xl border text-left flex flex-col justify-between transition ${
                    model === m.id
                      ? 'border-indigo-500 bg-indigo-600/15 text-white'
                      : 'border-slate-800 bg-dark-950/60 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <span className="text-sm font-semibold text-slate-200">{m.name}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-indigo-400 font-mono">
                      {m.badge}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500 font-mono">{m.id}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800 transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-5 py-2 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/25 transition flex items-center gap-2"
          >
            {savedStatus ? 'Saved!' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
}
