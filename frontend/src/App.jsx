import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import ChatPanel from './components/ChatPanel';
import PreviewFrame from './components/PreviewFrame';
import CodeViewer from './components/CodeViewer';
import VersionHistory from './components/VersionHistory';
import SettingsModal from './components/SettingsModal';
import Dashboard from './components/Dashboard';
import CreateProjectModal from './components/CreateProjectModal';
import DeleteConfirmModal from './components/DeleteConfirmModal';
import Toast from './components/Toast';
import {
  streamGenerate,
  streamRefine,
  revertToVersion,
  listProjects,
  getProject,
  createProject,
  deleteProject,
  checkBackendHealth
} from './services/api';

export default function App() {
  // Navigation View: 'dashboard' (entry screen) | 'editor'
  const [currentView, setCurrentView] = useState('dashboard');

  // Dashboard Projects State
  const [projects, setProjects] = useState([]);
  const [isProjectsLoading, setIsProjectsLoading] = useState(false);
  const [projectsError, setProjectsError] = useState('');
  const [backendStatus, setBackendStatus] = useState('healthy');

  // Modal & Notification States
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState(null);
  const [isDeletingProject, setIsDeletingProject] = useState(false);
  const [toast, setToast] = useState(null);

  // Active Editor Project State
  const [projectId, setProjectId] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [htmlCode, setHtmlCode] = useState('');
  const [pages, setPages] = useState([]);
  const [isMultiPage, setIsMultiPage] = useState(false);
  const [activePagePath, setActivePagePath] = useState('index.html');

  // Versioning & History
  const [versions, setVersions] = useState([]);
  const [currentVersionId, setCurrentVersionId] = useState(null);

  // Interactive Chat & Generation
  const [messages, setMessages] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  // Editor View Controls
  const [activeTab, setActiveTab] = useState('preview'); // 'preview' | 'code'
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Helper for displaying toast notifications
  const showToast = useCallback((message, type = 'info') => {
    setToast({ message, type });
  }, []);

  // Fetch all saved projects and check backend connectivity
  const fetchProjects = useCallback(async () => {
    setIsProjectsLoading(true);
    setProjectsError('');
    try {
      const [health, projectList] = await Promise.all([
        checkBackendHealth(),
        listProjects()
      ]);
      setBackendStatus(health.status === 'healthy' ? 'healthy' : 'degraded');
      setProjects(Array.isArray(projectList) ? projectList : []);
    } catch (err) {
      console.error('Error fetching dashboard projects:', err);
      setBackendStatus('offline');
      setProjectsError(err.message || 'Unable to communicate with the WebCraft AI backend.');
    } finally {
      setIsProjectsLoading(false);
    }
  }, []);

  // Load projects on initial app mount
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  // Global Escape key handler for open panels
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isHistoryOpen) {
        setIsHistoryOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isHistoryOpen]);

  // Open an existing project into the editor
  const handleOpenProject = async (targetId) => {
    try {
      setIsGenerating(false);
      setStatusMessage('');
      const proj = await getProject(targetId);
      if (!proj) {
        showToast('Project could not be loaded.', 'error');
        return;
      }

      setProjectId(proj.id);
      setProjectName(proj.name || 'Untitled Project');

      const projVersions = proj.versions || [];
      setVersions(projVersions);

      if (projVersions.length > 0) {
        const activeVer =
          projVersions.find((v) => v.id === proj.current_version_id) ||
          projVersions[projVersions.length - 1];

        setCurrentVersionId(activeVer.id);
        setHtmlCode(activeVer.html_code || '');

        const verPages =
          activeVer.pages && activeVer.pages.length > 0
            ? activeVer.pages
            : [{ name: 'Home', path: 'index.html', html: activeVer.html_code || '' }];
        setPages(verPages);
        setIsMultiPage(Boolean(activeVer.is_multi_page));
        setActivePagePath(verPages[0]?.path || 'index.html');

        // Reconstruct conversation timeline from version history
        const reconstructedMsgs = [];
        projVersions.forEach((ver, idx) => {
          if (ver.prompt && ver.prompt !== 'Initial project creation') {
            reconstructedMsgs.push({
              role: 'user',
              content: ver.prompt,
              timestamp: ver.created_at
                ? new Date(ver.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : 'Saved'
            });
            reconstructedMsgs.push({
              role: 'assistant',
              content:
                idx === 0 && ver.is_multi_page
                  ? `✨ Multi-page website generated (${verPages.length} pages: ${verPages.map((p) => p.name).join(', ')}).`
                  : idx === 0
                  ? '✨ Website generated successfully.'
                  : `Applied changes for: "${ver.prompt}".`,
              version: idx + 1,
              timestamp: ver.created_at
                ? new Date(ver.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : 'Saved'
            });
          }
        });
        setMessages(reconstructedMsgs);
      } else {
        setHtmlCode('');
        setPages([]);
        setIsMultiPage(false);
        setActivePagePath('index.html');
        setCurrentVersionId(null);
        setMessages([]);
      }

      setCurrentView('editor');
      showToast(`Opened project "${proj.name}"`, 'success');
    } catch (err) {
      console.error('Failed to open project:', err);
      showToast(`Error opening project: ${err.message}`, 'error');
    }
  };

  // Create a new project and open the editor
  const handleCreateProject = async (name) => {
    setIsCreatingProject(true);
    try {
      const newProj = await createProject({ name });
      setProjectId(newProj.id);
      setProjectName(newProj.name);
      setHtmlCode('');
      setPages([]);
      setIsMultiPage(false);
      setActivePagePath('index.html');
      setVersions(newProj.versions || []);
      setCurrentVersionId(newProj.current_version_id || null);
      setMessages([]);
      setIsGenerating(false);
      setStatusMessage('');

      setIsCreateModalOpen(false);
      setCurrentView('editor');
      showToast(`Created project "${newProj.name}". Ready to prompt!`, 'success');
      fetchProjects();
    } catch (err) {
      console.error('Failed to create project:', err);
      showToast(`Failed to create project: ${err.message}`, 'error');
    } finally {
      setIsCreatingProject(false);
    }
  };

  // Delete project with confirmation
  const handleConfirmDeleteProject = async (targetId) => {
    setIsDeletingProject(true);
    try {
      await deleteProject(targetId);
      setProjects((prev) => prev.filter((p) => p.id !== targetId));
      if (projectId === targetId) {
        setProjectId(null);
        setProjectName('');
        setHtmlCode('');
        setPages([]);
        setVersions([]);
        setMessages([]);
      }
      setProjectToDelete(null);
      showToast('Project deleted successfully.', 'success');
    } catch (err) {
      console.error('Failed to delete project:', err);
      showToast(`Failed to delete project: ${err.message}`, 'error');
    } finally {
      setIsDeletingProject(false);
    }
  };

  // Return from editor to dashboard
  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    fetchProjects();
  };

  // Switch active page in preview and code viewer
  const handleSelectPage = (path) => {
    setActivePagePath(path);
    const targetPage = pages.find((p) => p.path === path);
    if (targetPage) {
      setHtmlCode(targetPage.html);
    }
  };

  // Send prompt (initial generation or iterative refinement)
  const handleSendMessage = async (promptText) => {
    if (isGenerating) return;

    // Add user message to chat
    const userMsg = {
      role: 'user',
      content: promptText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsGenerating(true);
    setStatusMessage('Analyzing prompt and formulating design system...');

    let streamedAccumulator = '';

    if (!htmlCode) {
      // First generation for this project
      const finalProjectName =
        projectName || (promptText.length > 30 ? `${promptText.slice(0, 30)}...` : promptText);
      setProjectName(finalProjectName);

      await streamGenerate({
        prompt: promptText,
        projectId: projectId || null,
        projectName: finalProjectName,
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
          showToast('Website generated successfully!', 'success');
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
          showToast(`Generation error: ${err}`, 'error');
        }
      });
    } else {
      // Iterative refinement of existing code
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
          showToast('Refinement applied successfully!', 'success');
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
          showToast(`Refinement error: ${err}`, 'error');
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
    showToast(`Restored version v${versionIndex}`, 'info');
  };

  // New site trigger from Header
  const handleNewProjectTrigger = () => {
    setIsCreateModalOpen(true);
  };

  const currentVersionNumber =
    versions.findIndex((v) => v.id === currentVersionId) + 1 || versions.length;

  return (
    <div className="h-screen w-screen flex flex-col bg-dark-950 text-slate-100 overflow-hidden font-sans">
      {currentView === 'dashboard' ? (
        /* Project Dashboard Entry Screen */
        <Dashboard
          projects={projects}
          isLoading={isProjectsLoading}
          error={projectsError}
          backendStatus={backendStatus}
          onRefresh={fetchProjects}
          onOpenProject={handleOpenProject}
          onOpenCreateModal={() => setIsCreateModalOpen(true)}
          onRequestDeleteProject={(proj) => setProjectToDelete(proj)}
          onOpenSettings={() => setIsSettingsOpen(true)}
        />
      ) : (
        /* Full-Stack AI Studio Editor */
        <>
          {/* Top Navigation */}
          <Header
            projectName={projectName}
            versionNumber={currentVersionNumber}
            htmlCode={htmlCode}
            projectId={projectId}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            onNewProject={handleNewProjectTrigger}
            onBackToDashboard={handleBackToDashboard}
            onToggleHistory={() => setIsHistoryOpen(!isHistoryOpen)}
            onOpenSettings={() => setIsSettingsOpen(true)}
            isHistoryOpen={isHistoryOpen}
            isGenerating={isGenerating}
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
        </>
      )}

      {/* Global Modals & Notifications */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        isCreating={isCreatingProject}
        onSubmit={handleCreateProject}
        onClose={() => setIsCreateModalOpen(false)}
      />

      <DeleteConfirmModal
        isOpen={Boolean(projectToDelete)}
        project={projectToDelete}
        isDeleting={isDeletingProject}
        onConfirm={handleConfirmDeleteProject}
        onClose={() => setProjectToDelete(null)}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />

      <Toast
        toast={toast}
        onClose={() => setToast(null)}
      />
    </div>
  );
}
