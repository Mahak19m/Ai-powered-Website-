/**
 * API service for communicating with the FastAPI backend and SSE streaming.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export const getStoredApiKey = () => localStorage.getItem('gemini_api_key') || '';
export const setStoredApiKey = (key) => localStorage.setItem('gemini_api_key', key);

export const getStoredModel = () => localStorage.getItem('gemini_model') || 'gemini-2.5-flash';
export const setStoredModel = (model) => localStorage.setItem('gemini_model', model);

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function streamGenerate({
  prompt,
  projectId = null,
  projectName = null,
  onStatus,
  onChunk,
  onComplete,
  onError
}) {
  const apiKey = getStoredApiKey();
  const model = getStoredModel();

  try {
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        project_id: projectId,
        project_name: projectName,
        api_key: apiKey || null,
        model: model || null
      })
    });

    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const block of lines) {
        if (!block.trim()) continue;
        
        let eventType = 'message';
        let dataStr = '';

        for (const line of block.split('\n')) {
          if (line.startsWith('event: ')) {
            eventType = line.replace('event: ', '').trim();
          } else if (line.startsWith('data: ')) {
            dataStr = line.replace('data: ', '').trim();
          }
        }

        if (!dataStr) continue;

        try {
          const parsed = JSON.parse(dataStr);
          if (eventType === 'status' && onStatus) {
            onStatus(parsed);
          } else if (eventType === 'chunk' && onChunk) {
            onChunk(parsed.chunk);
          } else if (eventType === 'complete' && onComplete) {
            onComplete(parsed);
          } else if (eventType === 'error' && onError) {
            onError(parsed.error);
          }
        } catch (e) {
          console.error('Failed to parse SSE payload:', dataStr, e);
        }
      }
    }
  } catch (error) {
    if (onError) onError(error.message);
  }
}

export async function streamRefine({
  projectId,
  currentHtml,
  instruction,
  activePagePath = 'index.html',
  pages = null,
  isMultiPage = false,
  onStatus,
  onChunk,
  onComplete,
  onError
}) {
  const apiKey = getStoredApiKey();
  const model = getStoredModel();

  try {
    const response = await fetch(`${API_BASE}/refine`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        project_id: projectId,
        current_html: currentHtml,
        instruction,
        active_page_path: activePagePath,
        pages,
        is_multi_page: isMultiPage,
        api_key: apiKey || null,
        model: model || null
      })
    });

    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const block of lines) {
        if (!block.trim()) continue;
        
        let eventType = 'message';
        let dataStr = '';

        for (const line of block.split('\n')) {
          if (line.startsWith('event: ')) {
            eventType = line.replace('event: ', '').trim();
          } else if (line.startsWith('data: ')) {
            dataStr = line.replace('data: ', '').trim();
          }
        }

        if (!dataStr) continue;

        try {
          const parsed = JSON.parse(dataStr);
          if (eventType === 'status' && onStatus) {
            onStatus(parsed);
          } else if (eventType === 'chunk' && onChunk) {
            onChunk(parsed.chunk);
          } else if (eventType === 'complete' && onComplete) {
            onComplete(parsed);
          } else if (eventType === 'error' && onError) {
            onError(parsed.error);
          }
        } catch (e) {
          console.error('Failed to parse SSE payload:', dataStr, e);
        }
      }
    }
  } catch (error) {
    if (onError) onError(error.message);
  }
}

export async function listProjects() {
  const res = await fetch(`${API_BASE}/projects`);
  if (!res.ok) {
    throw new Error(`Failed to load projects: ${res.statusText || res.status}`);
  }
  return await res.json();
}

export async function getProject(projectId) {
  const res = await fetch(`${API_BASE}/projects/${projectId}`);
  if (!res.ok) {
    throw new Error(`Failed to load project: ${res.statusText || res.status}`);
  }
  return await res.json();
}

export async function createProject({ name, initialPrompt = '', initialHtml = '', pages = null, isMultiPage = false }) {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name,
      initial_prompt: initialPrompt || 'Initial project creation',
      initial_html: initialHtml || '',
      pages: pages,
      is_multi_page: isMultiPage
    })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create project: ${res.statusText}`);
  }
  return await res.json();
}

export async function deleteProject(projectId) {
  const res = await fetch(`${API_BASE}/projects/${projectId}`, {
    method: 'DELETE'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to delete project: ${res.statusText}`);
  }
  return await res.json();
}

export async function revertToVersion(projectId, versionId) {
  const res = await fetch(`${API_BASE}/projects/${projectId}/revert/${versionId}`, {
    method: 'POST'
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to revert version: ${res.statusText}`);
  }
  return await res.json();
}

export function downloadHtml(html, filename = 'index.html') {
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function downloadZip(projectId) {
  window.open(`${API_BASE}/export/project/${projectId}/zip`, '_blank');
}
