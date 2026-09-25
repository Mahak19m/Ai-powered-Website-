import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Wand2, Loader2, Bot, User, CheckCircle2, AlertCircle } from 'lucide-react';

const SUGGESTED_PROMPTS = [
  {
    title: 'Autonomous AI Agents',
    prompt: 'A dark modern landing page for an autonomous AI agent swarm platform with hero visual, interactive terminal demo, feature cards, and 3-tier pricing table.'
  },
  {
    title: 'Product Design Portfolio',
    prompt: 'A minimalist, high-end portfolio for a principal design technologist featuring featured case studies, awards, interactive dark theme, and contact CTA.'
  },
  {
    title: 'SaaS Analytics Dashboard',
    prompt: 'A clean marketing site for a real-time revenue analytics SaaS with metric counters, interactive feature tabs, client logos, and customer testimonials.'
  },
  {
    title: 'Artisan Coffee Roastery',
    prompt: 'A warm, editorial website for a specialty coffee roaster with bean catalog cards, roasting story, brew guide accordion, and newsletter subscription.'
  }
];

export default function ChatPanel({
  messages,
  isGenerating,
  statusMessage,
  onSendMessage,
  hasGeneratedCode
}) {
  const [inputPrompt, setInputPrompt] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, statusMessage]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!inputPrompt.trim() || isGenerating) return;
    onSendMessage(inputPrompt.trim());
    setInputPrompt('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSelectPrompt = (promptText) => {
    setInputPrompt(promptText);
    textareaRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-full bg-dark-900 border-r border-slate-800">
      {/* Top Panel Title */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Wand2 className="w-4 h-4 text-indigo-400" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            {hasGeneratedCode ? 'Iterative Refinement' : 'Website Studio'}
          </h2>
        </div>
        <span className="text-[11px] font-medium text-slate-500">
          {hasGeneratedCode ? 'Chat with AI to refine' : 'Start with a prompt'}
        </span>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col justify-center text-center px-4 py-8">
            <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-white mb-1">What kind of website do you want to build?</h3>
            <p className="text-xs text-slate-400 mb-6 leading-relaxed max-w-xs mx-auto">
              Describe your idea in plain English. WebCraft AI will design, structure, and code it in real time.
            </p>

            <div className="space-y-2 text-left">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
                Quick Starters
              </span>
              {SUGGESTED_PROMPTS.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectPrompt(item.prompt)}
                  className="w-full text-left p-2.5 rounded-xl bg-dark-950/70 hover:bg-indigo-950/40 border border-slate-800/80 hover:border-indigo-500/40 transition group flex items-start gap-2.5"
                >
                  <span className="text-indigo-400 text-xs mt-0.5">✦</span>
                  <div>
                    <span className="text-xs font-medium text-slate-200 group-hover:text-white block">
                      {item.title}
                    </span>
                    <span className="text-[11px] text-slate-500 line-clamp-1 group-hover:text-slate-400">
                      {item.prompt}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 text-xs leading-relaxed ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role !== 'user' && (
                <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 flex-shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-3.5 ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : msg.isError
                    ? 'bg-rose-950/50 border border-rose-800/50 text-rose-200'
                    : 'bg-dark-950 border border-slate-800 text-slate-300'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>
                {msg.version && (
                  <div className="mt-2 pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-indigo-400 font-mono">
                    <span className="flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      Version {msg.version} created
                    </span>
                    <span className="text-slate-500">{msg.timestamp || 'Just now'}</span>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 flex-shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          ))
        )}

        {/* Live Generation Indicator */}
        {isGenerating && (
          <div className="flex gap-3 text-xs">
            <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 flex-shrink-0 mt-0.5">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            </div>
            <div className="rounded-2xl p-3.5 bg-dark-950 border border-indigo-500/30 text-indigo-300 animate-pulse flex items-center gap-2 max-w-[85%]">
              <span>{statusMessage || 'Designing website architecture and generating code...'}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Prompt Input Area */}
      <div className="p-3 border-t border-slate-800 bg-dark-950/80">
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            ref={textareaRef}
            rows={3}
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isGenerating}
            placeholder={
              hasGeneratedCode
                ? "Describe changes (e.g. 'Make hero dark emerald', 'Add FAQ accordion', 'Add 3 testimonials')..."
                : "Describe the website you want to generate..."
            }
            className="w-full px-3.5 py-2.5 pb-10 rounded-xl bg-dark-900 border border-slate-700 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition resize-none disabled:opacity-50"
          />

          <div className="absolute bottom-2.5 right-2.5 flex items-center gap-2">
            <span className="text-[10px] text-slate-500 hidden sm:inline">
              ↵ Enter to send
            </span>
            <button
              type="submit"
              disabled={!inputPrompt.trim() || isGenerating}
              className="p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white shadow-sm transition"
            >
              {isGenerating ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Send className="w-3.5 h-3.5" />
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
