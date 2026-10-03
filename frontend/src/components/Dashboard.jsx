import React, { useState, useMemo } from 'react';
import {
  Sparkles,
  Plus,
  Trash2,
  Search,
  Layers,
  Clock,
  RefreshCw,
  AlertCircle,
  FolderOpen,
  ArrowRight,
  Settings,
  Globe,
  SlidersHorizontal,
  LayoutGrid,
  List
} from 'lucide-react';

export default function Dashboard({
  projects,
  isLoading,
  error,
  backendStatus,
  onRefresh,
  onOpenProject,
  onOpenCreateModal,
  onRequestDeleteProject,
  onOpenSettings
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('updated_desc'); // 'updated_desc' | 'created_desc' | 'name_asc' | 'versions_desc'
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'list'

  // Format date helper
  const formatDate = (isoString) => {
    if (!isoString) return 'Just now';
    try {
      const d = new Date(isoString);
      if (isNaN(d.getTime())) return isoString;
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoString;
    }
  };

  // Filter and sort projects
  const filteredProjects = useMemo(() => {
    let result = [...(projects || [])];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(
        (p) =>
          p.name?.toLowerCase().includes(q) ||
          p.id?.toLowerCase().includes(q)
      );
    }

    result.sort((a, b) => {
      if (sortBy === 'updated_desc') {
        return new Date(b.updated_at || b.created_at || 0) - new Date(a.updated_at || a.created_at || 0);
      }
      if (sortBy === 'created_desc') {
        return new Date(b.created_at || 0) - new Date(a.created_at || 0);
      }
      if (sortBy === 'name_asc') {
        return (a.name || '').localeCompare(b.name || '');
      }
      if (sortBy === 'versions_desc') {
        return (b.versions_count || 1) - (a.versions_count || 1);
      }
      return 0;
    });

    return result;
  }, [projects, searchQuery, sortBy]);

  const totalProjects = projects?.length || 0;
  const multiPageCount = projects?.filter((p) => p.is_multi_page)?.length || 0;
  const totalVersions = projects?.reduce((sum, p) => sum + (p.versions_count || 1), 0) || 0;

  return (
    <div className="min-h-screen w-screen bg-dark-950 text-slate-100 flex flex-col font-sans overflow-x-hidden">
      {/* Top Navigation Bar */}
      <header className="h-16 border-b border-slate-800 bg-dark-950/80 backdrop-blur sticky top-0 z-30 px-4 sm:px-6 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/25">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base text-white tracking-tight leading-none">WebCraft AI</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Dashboard
              </span>
            </div>
            <span className="text-xs text-slate-400 leading-tight hidden sm:block">Autonomous Full-Stack Website Builder</span>
          </div>
        </div>

        {/* Header Right Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Backend Status indicator */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === 'healthy'
                  ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50'
                  : 'bg-rose-400 shadow-sm shadow-rose-400/50'
              }`}
            />
            <span className="text-slate-300 capitalize text-[11px]">
              {backendStatus === 'healthy' ? 'API Online' : 'API Offline'}
            </span>
          </div>

          {/* Refresh Button */}
          <button
            type="button"
            onClick={onRefresh}
            disabled={isLoading}
            aria-label="Refresh project list"
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800 transition focus:outline-none focus:ring-2 focus:ring-slate-700"
            title="Refresh Projects"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-indigo-400' : ''}`} />
          </button>

          {/* Settings Button */}
          <button
            type="button"
            onClick={onOpenSettings}
            aria-label="Open AI settings"
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800 transition focus:outline-none focus:ring-2 focus:ring-slate-700"
            title="AI Model & API Key Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          {/* Create New Project Primary Action */}
          <button
            type="button"
            onClick={onOpenCreateModal}
            className="flex items-center gap-2 px-3.5 sm:px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/25 transition active:scale-95 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Create New Project</span>
            <span className="sm:hidden">New</span>
          </button>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
        {/* Connection Error Banner */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/25 text-rose-300 flex items-center justify-between gap-4 animate-in fade-in">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-rose-200">Backend Communication Issue</p>
                <p className="text-xs text-rose-300/80">{error}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={onRefresh}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-600/30 hover:bg-rose-600/50 text-xs font-medium text-rose-100 border border-rose-500/40 transition focus:outline-none focus:ring-2 focus:ring-rose-500"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* Dashboard Top Stats & Welcome Card */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2 p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 shadow-xl relative overflow-hidden flex flex-col justify-between">
            <div className="space-y-1.5 relative z-10">
              <h2 className="text-xl font-bold text-white tracking-tight">Your Website Projects</h2>
              <p className="text-xs text-slate-400 max-w-md">
                Manage, preview, and iteratively refine all your AI-generated single-page and multi-page websites.
              </p>
            </div>
            <div className="mt-4 flex items-center gap-3 relative z-10">
              <button
                type="button"
                onClick={onOpenCreateModal}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-md shadow-indigo-600/25 transition focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Project</span>
              </button>
            </div>
            {/* Background Glow */}
            <div className="absolute right-0 bottom-0 w-48 h-48 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
          </div>

          {/* Stat Card 1: Total Projects */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-md flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400">Total Projects</p>
              <h3 className="text-2xl font-bold text-white mt-1">{totalProjects}</h3>
              <p className="text-[11px] text-slate-500 mt-0.5">Persisted in database</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <FolderOpen className="w-6 h-6" />
            </div>
          </div>

          {/* Stat Card 2: Multi-Page Websites */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-md flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400">Multi-Page Sites</p>
              <h3 className="text-2xl font-bold text-white mt-1">{multiPageCount}</h3>
              <p className="text-[11px] text-slate-500 mt-0.5">{totalVersions} total versions</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
              <Layers className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Filter, Search, and View Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          {/* Search Box */}
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search projects..."
              aria-label="Search projects by name or ID"
              className="w-full pl-10 pr-12 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                aria-label="Clear search query"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-white px-1"
              >
                Clear
              </button>
            )}
          </div>

          {/* Sort & View Options */}
          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            {/* Sort Dropdown */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
              <SlidersHorizontal className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                aria-label="Sort projects"
                className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value="updated_desc" className="bg-slate-900 text-white">Recently Updated</option>
                <option value="created_desc" className="bg-slate-900 text-white">Newest First</option>
                <option value="name_asc" className="bg-slate-900 text-white">Alphabetical (A-Z)</option>
                <option value="versions_desc" className="bg-slate-900 text-white">Most Versions</option>
              </select>
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center bg-slate-900 border border-slate-800 rounded-xl p-0.5" role="group" aria-label="View layout switcher">
              <button
                type="button"
                onClick={() => setViewMode('grid')}
                aria-label="Grid view"
                aria-pressed={viewMode === 'grid'}
                className={`p-1.5 rounded-lg transition ${
                  viewMode === 'grid' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Grid View"
              >
                <LayoutGrid className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setViewMode('list')}
                aria-label="List view"
                aria-pressed={viewMode === 'list'}
                className={`p-1.5 rounded-lg transition ${
                  viewMode === 'list' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="List View"
              >
                <List className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Project List / Cards Section */}
        {isLoading ? (
          /* Loading Skeletons */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((idx) => (
              <div
                key={idx}
                className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/60 animate-pulse space-y-4 min-h-[190px] flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="h-4 w-32 bg-slate-800 rounded" />
                    <div className="h-4 w-12 bg-slate-800 rounded-full" />
                  </div>
                  <div className="space-y-1.5">
                    <div className="h-4 w-44 bg-slate-800/80 rounded" />
                    <div className="h-3 w-28 bg-slate-800/50 rounded" />
                  </div>
                </div>
                <div className="pt-3 flex items-center justify-between border-t border-slate-800/60">
                  <div className="h-8 w-28 bg-slate-800 rounded-xl" />
                  <div className="h-8 w-8 bg-slate-800 rounded-lg" />
                </div>
              </div>
            ))}
          </div>
        ) : filteredProjects.length === 0 ? (
          /* Empty State */
          <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800/60 space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
              <FolderOpen className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-semibold text-white">
                {searchQuery ? 'No matching projects found' : 'No projects yet'}
              </h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                {searchQuery
                  ? `We couldn't find any projects matching "${searchQuery}". Try a different keyword or clear your filter.`
                  : 'Get started by creating your first website project with natural language prompts.'}
              </p>
            </div>
            {searchQuery ? (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition"
              >
                Clear Search
              </button>
            ) : (
              <button
                type="button"
                onClick={onOpenCreateModal}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition"
              >
                <Plus className="w-4 h-4" />
                <span>Create Your First Project</span>
              </button>
            )}
          </div>
        ) : viewMode === 'grid' ? (
          /* Grid View */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProjects.map((project) => (
              <div
                key={project.id}
                className="group p-5 rounded-2xl bg-slate-900/90 hover:bg-slate-900 border border-slate-800 hover:border-indigo-500/40 shadow-md hover:shadow-xl hover:shadow-indigo-500/5 hover:-translate-y-0.5 transition-all duration-200 flex flex-col justify-between min-h-[195px]"
              >
                {/* Card Top: Badges & Name */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold">
                      v{project.versions_count || 1}
                    </span>
                    {project.is_multi_page ? (
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-violet-500/10 text-violet-300 border border-violet-500/20 flex items-center gap-1">
                        <Layers className="w-3 h-3" />
                        <span>Multi-Page ({project.pages_count || 'Multi'})</span>
                      </span>
                    ) : (
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1">
                        <Globe className="w-3 h-3" />
                        <span>Single Page</span>
                      </span>
                    )}
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-white group-hover:text-indigo-300 transition line-clamp-1" title={project.name}>
                      {project.name}
                    </h4>
                    <p className="text-[11px] font-mono text-slate-500 mt-0.5">ID: {project.id}</p>
                  </div>

                  {/* Date details */}
                  <div className="space-y-1 text-[11px] text-slate-400 pt-1">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3 h-3 text-slate-500 flex-shrink-0" />
                      <span className="truncate">Updated: {formatDate(project.updated_at || project.created_at)}</span>
                    </div>
                  </div>
                </div>

                {/* Card Bottom: Actions */}
                <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                  <button
                    type="button"
                    onClick={() => onOpenProject(project.id)}
                    aria-label={`Open project ${project.name}`}
                    className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-indigo-600/15 hover:bg-indigo-600 text-indigo-300 hover:text-white text-xs font-semibold border border-indigo-500/30 hover:border-indigo-600 shadow-sm transition"
                  >
                    <span>Open Project</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>

                  <button
                    type="button"
                    onClick={() => onRequestDeleteProject(project)}
                    aria-label={`Delete project ${project.name}`}
                    className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 transition"
                    title={`Delete ${project.name}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* List View */
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden divide-y divide-slate-800/60">
            {filteredProjects.map((project) => (
              <div
                key={project.id}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-850/50 transition"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-300 flex-shrink-0">
                    {project.is_multi_page ? <Layers className="w-5 h-5 text-violet-400" /> : <Globe className="w-5 h-5 text-indigo-400" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-semibold text-white">{project.name}</h4>
                      <span className="text-[10px] font-mono px-2 py-0.2 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold">
                        v{project.versions_count || 1}
                      </span>
                      {project.is_multi_page && (
                        <span className="text-[10px] px-2 py-0.2 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20">
                          Multi-Page
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Last edited: {formatDate(project.updated_at || project.created_at)} • ID: {project.id}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center">
                  <button
                    type="button"
                    onClick={() => onOpenProject(project.id)}
                    aria-label={`Open project ${project.name}`}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition"
                  >
                    <span>Open</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => onRequestDeleteProject(project)}
                    aria-label={`Delete project ${project.name}`}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
                    title={`Delete ${project.name}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
