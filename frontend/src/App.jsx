import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ChatPanel from './components/ChatPanel';
import PreviewFrame from './components/PreviewFrame';
import CodeViewer from './components/CodeViewer';
import VersionHistory from './components/VersionHistory';
import SettingsModal from './components/SettingsModal';
import { streamGenerate, streamRefine, revertToVersion } from './services/api';

export default function App() {
  const [projectId, setProjectId] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [htmlCode, setHtmlCode] = useState('');
  const [pages, setPages] = useState([]);
  const [isMultiPage, setIsMultiPage] = useState(false);
  const [activePagePath, setActivePagePath] = useState('index.html');

  const [versions, setVersions] = useState([]);
  const [currentVersionId, setCurrentVersionId] = useState(null);

  const [messages, setMessages] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const [activeTab, setActiveTab] = useState('preview'); // 'preview' | 'code'
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Switch active page in preview and code viewer
  const handleSelectPage = (path) => {
    setActivePagePath(path);
    const targetPage = pages.find((p) => p.path === path);
    if (targetPage) {
      setHtmlCode(targetPage.html);
    }
  };

  // Send a new prompt (either initial generation or iterative refinement)
  const handleSendMessage = async (promptText) => {
    if (isGenerating) return;

    // Add user message
    const userMsg = {
      role: 'user',
      content: promptText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsGenerating(true);
    setStatusMessage('Analyzing prompt and formulating design system...');

    let streamedAccumulator = '';

    if (!htmlCode || !projectId) {
      // First generation
      const autoProjectName = promptText.length > 30 ? `${promptText.slice(0, 30)}...` : promptText;
      setProjectName(autoProjectName);

      await streamGenerate({
        prompt: promptText,
        projectName: autoProjectName,
        onStatus: (data) => {
          setStatusMessage(data.message || 'Designing layout...');
        },
        onChunk: (chunk) => {
          streamedAccumulator += chunk;
          const clean = streamedAccumulator
            .replace(/^```(?:html)?\s*/i, '')
            .replace(/```\s*$/i, '');
          if (clean.includes('<body') || clean.includes('<!DOCTYPE')) {
            setHtmlCode(clean);
          }
        },
        onComplete: (data) => {
          setProjectId(data.project_id);
          setHtmlCode(data.html);
          setCurrentVersionId(data.version_id);

          const genPages = data.pages || [{ name: 'Home', path: 'index.html', html: data.html }];
          const multi = Boolean(data.is_multi_page);
          setPages(genPages);
          setIsMultiPage(multi);
          setActivePagePath(data.active_page_path || 'index.html');

          const newVer = {
            id: data.version_id,
            prompt: data.prompt,
            html_code: data.html,
            pages: genPages,
            is_multi_page: multi,
            created_at: new Date().toISOString(),
            version_type: 'generation'
          };
          setVersions([newVer]);

          const summaryMsg = multi
            ? `✨ Multi-page website generated (${genPages.length} pages: ${genPages.map((p) => p.name).join(', ')})! You can switch pages, test inter-page links, or refine specific pages.`
            : `✨ Website generated successfully! You can preview it, switch viewports, or prompt further refinements below.`;

          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: summaryMsg,
              version: 1,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }
          ]);

          setIsGenerating(false);
          setStatusMessage('');
        },
        onError: (err) => {
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: `Error during generation: ${err}`,
              isError: true,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }
          ]);
          setIsGenerating(false);
          setStatusMessage('');
        }
      });
    } else {
      // Iterative refinement
      await streamRefine({
        projectId,
        currentHtml: htmlCode,
        instruction: promptText,
        activePagePath,
        pages,
        isMultiPage,
        onStatus: (data) => {
          setStatusMessage(data.message || 'Applying requested edits...');
        },
        onChunk: (chunk) => {
          streamedAccumulator += chunk;
          const clean = streamedAccumulator
            .replace(/^```(?:html)?\s*/i, '')
            .replace(/```\s*$/i, '');
          if (clean.includes('<body') || clean.includes('<!DOCTYPE')) {
            setHtmlCode(clean);
          }
        },
        onComplete: (data) => {
          setHtmlCode(data.html);
          setCurrentVersionId(data.version_id);

          const updatedPages = data.pages || [{ name: 'Home', path: 'index.html', html: data.html }];
          const multi = Boolean(data.is_multi_page);
          setPages(updatedPages);
          setIsMultiPage(multi);
          setActivePagePath(data.active_page_path || activePagePath);

          const newVer = {
            id: data.version_id,
            prompt: data.prompt,
            html_code: data.html,
            pages: updatedPages,
            is_multi_page: multi,
            created_at: new Date().toISOString(),
            version_type: 'refinement'
          };
          setVersions((prev) => [...prev, newVer]);

          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: `Applied changes for: "${promptText}". Check out the updated preview!`,
              version: versions.length + 1,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }
          ]);

          setIsGenerating(false);
          setStatusMessage('');
        },
        onError: (err) => {
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: `Error during refinement: ${err}`,
              isError: true,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }
          ]);
          setIsGenerating(false);
          setStatusMessage('');
        }
      });
    }
  };

  // Restore previous snapshot version
  const handleRestoreVersion = async (versionId) => {
    const target = versions.find((v) => v.id === versionId);
    if (!target) return;

    try {
      if (projectId) {
        await revertToVersion(projectId, versionId);
      }
    } catch (e) {
      console.warn('Revert API sync note:', e);
    }

    if (target.pages && target.pages.length > 0) {
      setPages(target.pages);
      setIsMultiPage(Boolean(target.is_multi_page));
      const targetPage = target.pages.find((p) => p.path === activePagePath) || target.pages[0];
      setActivePagePath(targetPage.path);
      setHtmlCode(targetPage.html);
    } else {
      setHtmlCode(target.html_code);
      setPages([{ name: 'Home', path: 'index.html', html: target.html_code }]);
      setIsMultiPage(false);
      setActivePagePath('index.html');
    }

    setCurrentVersionId(target.id);

    const versionIndex = versions.findIndex((v) => v.id === versionId) + 1;
    setMessages((prev) => [
      ...prev,
      {
        role: 'assistant',
        content: `Restored version v${versionIndex} ("${target.prompt}")`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  // Reset to start a new project
  const handleNewProject = () => {
    if (htmlCode && !window.confirm('Start a new site? Any unsaved progress will be cleared.')) {
      return;
    }
    setProjectId(null);
    setProjectName('');
    setHtmlCode('');
    setPages([]);
    setIsMultiPage(false);
    setActivePagePath('index.html');
    setVersions([]);
    setCurrentVersionId(null);
    setMessages([]);
    setIsGenerating(false);
    setStatusMessage('');
  };

  const currentVersionNumber = versions.findIndex((v) => v.id === currentVersionId) + 1 || versions.length;

  return (
    <div className="h-screen w-screen flex flex-col bg-dark-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Navigation */}
      <Header
        projectName={projectName}
        versionNumber={currentVersionNumber}
        htmlCode={htmlCode}
        projectId={projectId}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNewProject={handleNewProject}
        onToggleHistory={() => setIsHistoryOpen(!isHistoryOpen)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        isHistoryOpen={isHistoryOpen}
      />

      {/* Main Studio Body: Split-Pane Workbench */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Side: AI Studio Chat Panel */}
        <div className="w-full sm:w-[380px] lg:w-[440px] xl:w-[480px] flex-shrink-0 h-full border-r border-slate-800">
          <ChatPanel
            messages={messages}
            isGenerating={isGenerating}
            statusMessage={statusMessage}
            onSendMessage={handleSendMessage}
            hasGeneratedCode={Boolean(htmlCode)}
          />
        </div>

        {/* Right Side: Live Sandbox Preview / Code Viewer */}
        <div className="flex-1 h-full overflow-hidden bg-dark-950">
          {activeTab === 'preview' ? (
            <PreviewFrame
              htmlCode={htmlCode}
              isGenerating={isGenerating}
              pages={pages}
              activePagePath={activePagePath}
              isMultiPage={isMultiPage}
              onSelectPage={handleSelectPage}
            />
          ) : (
            <CodeViewer
              htmlCode={htmlCode}
              projectName={projectName}
              pages={pages}
              activePagePath={activePagePath}
              isMultiPage={isMultiPage}
              onSelectPage={handleSelectPage}
            />
          )}
        </div>

        {/* Sliding Version History Timeline */}
        <VersionHistory
          isOpen={isHistoryOpen}
          onClose={() => setIsHistoryOpen(false)}
          versions={versions}
          currentVersionId={currentVersionId}
          onRestoreVersion={handleRestoreVersion}
        />
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}
