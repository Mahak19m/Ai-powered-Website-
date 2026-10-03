import React, { useState, useRef, useEffect } from 'react';
import { Monitor, Tablet, Smartphone, RotateCw, ExternalLink, Sparkles, ZoomIn, ZoomOut, Layers, FileText, Loader2 } from 'lucide-react';

const VIEWPORTS = {
  desktop: { name: 'Desktop', width: '100%', icon: Monitor },
  tablet: { name: 'Tablet (768px)', width: '768px', icon: Tablet },
  mobile: { name: 'Mobile (375px)', width: '375px', icon: Smartphone },
};

export default function PreviewFrame({
  htmlCode,
  isGenerating,
  pages = [],
  activePagePath = 'index.html',
  isMultiPage = false,
  onSelectPage
}) {
  const [viewport, setViewport] = useState('desktop');
  const [scale, setScale] = useState(1);
  const [refreshKey, setRefreshKey] = useState(0);
  const iframeRef = useRef(null);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const handleOpenNewWindow = () => {
    if (!htmlCode) return;
    const blob = new Blob([htmlCode], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  // Intercept all link clicks within iframe to ensure proper in-page anchor scrolling and multi-page switching
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const handleDocClick = (e) => {
      const anchor = e.target.closest('a');
      if (!anchor) return;

      const href = anchor.getAttribute('href');
      if (!href) return;

      const doc = iframe.contentDocument || iframe.contentWindow?.document;
      if (!doc) return;

      // 1. In-page anchor navigation (#about, #skills, #projects, etc.)
      if (href.startsWith('#')) {
        e.preventDefault();
        e.stopPropagation();

        if (href === '#' || href === '#top' || href === '#hero') {
          const heroEl = doc.getElementById('hero');
          if (heroEl) {
            heroEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
          } else {
            doc.documentElement.scrollTo({ top: 0, behavior: 'smooth' });
          }
        } else {
          const targetId = href.substring(1);
          const targetEl = doc.getElementById(targetId) || doc.querySelector(`[name="${targetId}"]`) || doc.querySelector(href);
          if (targetEl) {
            targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
        return;
      }

      // 2. External links
      if (href.startsWith('http://') || href.startsWith('https://')) {
        e.preventDefault();
        e.stopPropagation();
        window.open(href, '_blank', 'noopener,noreferrer');
        return;
      }

      // 3. Special protocols
      if (href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('javascript:')) {
        return;
      }

      // 4. Multi-page relative links (about.html, pricing.html, index.html, etc.)
      e.preventDefault();
      e.stopPropagation();

      const cleanHref = href.split('?')[0].split('#')[0].replace(/^\.?\//, '');
      const matchingPage = pages.find(
        (p) => p.path === cleanHref || p.path === `${cleanHref}.html` || p.path.endsWith(`/${cleanHref}`)
      );

      if (matchingPage && onSelectPage) {
        onSelectPage(matchingPage.path);
      } else if (cleanHref === '' || cleanHref === 'index.html') {
        if (onSelectPage && pages.some((p) => p.path === 'index.html')) {
          onSelectPage('index.html');
        } else {
          doc.documentElement.scrollTo({ top: 0, behavior: 'smooth' });
        }
      }
    };

    const attachListener = () => {
      try {
        const doc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!doc) return;
        doc.removeEventListener('click', handleDocClick, true);
        doc.addEventListener('click', handleDocClick, true);
      } catch (err) {
        console.warn('Iframe navigation listener attach warning:', err);
      }
    };

    attachListener();
    iframe.addEventListener('load', attachListener);

    return () => {
      iframe.removeEventListener('load', attachListener);
      try {
        const doc = iframe.contentDocument || iframe.contentWindow?.document;
        if (doc) doc.removeEventListener('click', handleDocClick, true);
      } catch (_) {}
    };
  }, [pages, onSelectPage, refreshKey, htmlCode]);

  return (
    <div className="flex flex-col h-full bg-dark-950 overflow-hidden relative">
      {/* Streaming Generation Progress Bar */}
      {isGenerating && (
        <div className="h-0.5 w-full bg-slate-800 overflow-hidden z-20">
          <div className="h-full bg-gradient-to-r from-indigo-500 via-violet-500 to-indigo-500 animate-pulse w-full"></div>
        </div>
      )}

      {/* Viewport Toolbar */}
      <div className="h-12 border-b border-slate-800/80 bg-dark-900/60 px-4 flex items-center justify-between z-10 select-none">
        
        {/* Device Switcher */}
        <div className="flex items-center bg-dark-950 border border-slate-800 rounded-lg p-0.5" role="group" aria-label="Viewport device selector">
          {Object.entries(VIEWPORTS).map(([key, item]) => {
            const Icon = item.icon;
            const isActive = viewport === key;
            return (
              <button
                key={key}
                type="button"
                onClick={() => setViewport(key)}
                aria-pressed={isActive}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs transition ${
                  isActive
                    ? 'bg-indigo-600 text-white font-medium shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title={item.name}
              >
                <Icon className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{item.name.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* Zoom buttons */}
          <div className="hidden md:flex items-center bg-dark-950 border border-slate-800 rounded-lg p-0.5 text-slate-400">
            <button
              onClick={() => setScale((s) => Math.max(0.5, s - 0.1))}
              aria-label="Zoom out preview"
              className="p-1 hover:text-white transition"
              title="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[11px] font-mono px-1.5 text-slate-300">
              {Math.round(scale * 100)}%
            </span>
            <button
              onClick={() => setScale((s) => Math.min(1.2, s + 0.1))}
              aria-label="Zoom in preview"
              className="p-1 hover:text-white transition"
              title="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="h-4 w-px bg-slate-800 hidden md:block"></div>

          <button
            type="button"
            onClick={handleRefresh}
            aria-label="Reload preview"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            title="Reload preview"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isGenerating ? 'animate-spin text-indigo-400' : ''}`} />
          </button>

          <button
            type="button"
            onClick={handleOpenNewWindow}
            disabled={!htmlCode}
            aria-label="Open preview in new browser tab"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-40 transition"
            title="Open preview in new tab"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Multi-Page Navigation Bar (when multi-page website) */}
      {isMultiPage && pages.length > 1 && (
        <div className="bg-dark-900/90 border-b border-slate-800/80 px-4 py-2 flex items-center gap-2 overflow-x-auto text-xs z-10">
          <div className="flex items-center gap-1 text-slate-400 font-medium mr-2 flex-shrink-0">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>Pages:</span>
          </div>
          <div className="flex items-center gap-1.5">
            {pages.map((pg) => {
              const isActive = (pg.path === activePagePath);
              return (
                <button
                  key={pg.path}
                  type="button"
                  onClick={() => onSelectPage && onSelectPage(pg.path)}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-lg font-medium transition whitespace-nowrap ${
                    isActive
                      ? 'bg-indigo-600/90 text-white shadow-sm border border-indigo-500/50'
                      : 'bg-dark-950/80 text-slate-400 hover:text-slate-200 border border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <FileText className="w-3 h-3 opacity-70" />
                  <span>{pg.name}</span>
                  <span className="text-[10px] font-mono opacity-60">({pg.path})</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Frame Container */}
      <div className="flex-1 bg-dark-950 p-3 sm:p-5 flex items-center justify-center overflow-auto">
        {!htmlCode ? (
          <div className="text-center max-w-sm p-8 rounded-2xl border border-dashed border-slate-800 bg-dark-900/30">
            <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mx-auto mb-3">
              <Sparkles className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-semibold text-slate-200 mb-1">Live Sandbox Ready</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Send a prompt from the studio panel on the left to start generating your website in real-time.
            </p>
          </div>
        ) : (
          <div
            className={`transition-all duration-300 h-full flex flex-col items-center justify-center ${
              viewport !== 'desktop'
                ? 'shadow-2xl rounded-2xl border-4 border-slate-800 overflow-hidden bg-slate-900'
                : 'w-full h-full'
            }`}
            style={{
              width: VIEWPORTS[viewport].width,
              transform: `scale(${scale})`,
              transformOrigin: 'top center',
            }}
          >
            {/* Device top notch indicator for mobile */}
            {viewport === 'mobile' && (
              <div className="w-full bg-slate-800 py-1 flex justify-center items-center">
                <div className="w-16 h-1 rounded-full bg-slate-700"></div>
              </div>
            )}

            <iframe
              key={refreshKey}
              ref={iframeRef}
              srcDoc={htmlCode}
              title="Live Website Sandbox"
              sandbox="allow-scripts allow-same-origin allow-forms allow-modals allow-popups"
              className="w-full h-full bg-white border-0 transition-opacity duration-300"
            />
          </div>
        )}
      </div>
    </div>
  );
}
