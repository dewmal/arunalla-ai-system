// Admin Panel JavaScript

// State Management
const state = {
    adminApiKey: null,
    agents: [],
    currentAgent: null,
    isEditMode: false
};

// API Base URL
const API_BASE = window.location.origin;

// DOM Elements
const loginScreen = document.getElementById('loginScreen');
const adminPanel = document.getElementById('adminPanel');
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');
const agentsList = document.getElementById('agentsList');
const searchAgents = document.getElementById('searchAgents');
const welcomeScreen = document.getElementById('welcomeScreen');
const agentEditor = document.getElementById('agentEditor');
const agentForm = document.getElementById('agentForm');
const historyModal = document.getElementById('historyModal');
const historyContent = document.getElementById('historyContent');
const toastContainer = document.getElementById('toastContainer');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    const savedApiKey = localStorage.getItem('adminApiKey');
    if (savedApiKey) {
        state.adminApiKey = savedApiKey;
        showAdminPanel();
    }
    
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Login
    loginForm.addEventListener('submit', handleLogin);
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    
    // Create Agent
    document.getElementById('createAgentBtn').addEventListener('click', showCreateAgent);
    
    // Refresh Agents
    document.getElementById('refreshAgentsBtn').addEventListener('click', loadAgents);
    
    // Search Agents
    searchAgents.addEventListener('input', filterAgents);
    
    // Save Agent
    document.getElementById('saveAgentBtn').addEventListener('click', handleSaveAgent);
    
    // Delete Agent
    document.getElementById('deleteAgentBtn').addEventListener('click', handleDeleteAgent);
    
    // View History
    document.getElementById('viewHistoryBtn').addEventListener('click', showHistory);
    
    // Close Modal
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            historyModal.style.display = 'none';
        });
    });
    
    // Temperature Slider
    document.getElementById('agentTemperature').addEventListener('input', (e) => {
        document.getElementById('temperatureValue').textContent = e.target.value;
    });
    
    // Close modal on outside click
    historyModal.addEventListener('click', (e) => {
        if (e.target === historyModal) {
            historyModal.style.display = 'none';
        }
    });
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    const apiKey = document.getElementById('adminApiKey').value;
    
    try {
        // Test the API key by trying to list agents
        const response = await fetch(`${API_BASE}/admin/agents`, {
            headers: {
                'X-Admin-API-Key': apiKey
            }
        });
        
        if (response.ok) {
            state.adminApiKey = apiKey;
            localStorage.setItem('adminApiKey', apiKey);
            showAdminPanel();
        } else {
            const error = await response.json();
            showLoginError(error.detail || 'Invalid admin API key');
        }
    } catch (error) {
        showLoginError('Failed to connect to server');
    }
}

function handleLogout() {
    state.adminApiKey = null;
    localStorage.removeItem('adminApiKey');
    loginScreen.style.display = 'flex';
    adminPanel.style.display = 'none';
    document.getElementById('adminApiKey').value = '';
}

function showLoginError(message) {
    loginError.textContent = message;
    loginError.style.display = 'block';
    setTimeout(() => {
        loginError.style.display = 'none';
    }, 5000);
}

function showAdminPanel() {
    loginScreen.style.display = 'none';
    adminPanel.style.display = 'block';
    loadAgents();
}

// Agent Management
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE}/admin/agents`, {
            headers: {
                'X-Admin-API-Key': state.adminApiKey
            }
        });
        
        if (response.ok) {
            state.agents = await response.json();
            renderAgentsList();
        } else {
            showToast('Failed to load agents', 'error');
        }
    } catch (error) {
        showToast('Error loading agents', 'error');
    }
}

function renderAgentsList() {
    agentsList.innerHTML = '';
    
    const filteredAgents = filterAgentsBySearch();
    
    if (filteredAgents.length === 0) {
        agentsList.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted);">No agents found</div>';
        return;
    }
    
    filteredAgents.forEach(agent => {
        const item = document.createElement('div');
        item.className = 'agent-item';
        if (state.currentAgent && state.currentAgent.name === agent.name) {
            item.classList.add('active');
        }
        
        item.innerHTML = `
            <div class="agent-item-header">
                <div class="agent-item-name">${agent.name}</div>
                <div class="agent-item-status ${agent.enabled ? '' : 'disabled'}"></div>
            </div>
            <div class="agent-item-model">${agent.model}</div>
        `;
        
        item.addEventListener('click', () => loadAgent(agent.name));
        agentsList.appendChild(item);
    });
}

function filterAgentsBySearch() {
    const search = searchAgents.value.toLowerCase();
    if (!search) return state.agents;
    
    return state.agents.filter(agent =>
        agent.name.toLowerCase().includes(search) ||
        agent.model.toLowerCase().includes(search)
    );
}

function filterAgents() {
    renderAgentsList();
}

async function loadAgent(agentName) {
    try {
        const response = await fetch(`${API_BASE}/admin/agents/${agentName}`, {
            headers: {
                'X-Admin-API-Key': state.adminApiKey
            }
        });
        
        if (response.ok) {
            state.currentAgent = await response.json();
            state.isEditMode = true;
            showAgentEditor();
        } else {
            showToast('Failed to load agent', 'error');
        }
    } catch (error) {
        showToast('Error loading agent', 'error');
    }
}

function showCreateAgent() {
    state.currentAgent = null;
    state.isEditMode = false;
    showAgentEditor();
}

function showAgentEditor() {
    welcomeScreen.style.display = 'none';
    agentEditor.style.display = 'block';
    
    if (state.isEditMode && state.currentAgent) {
        // Edit mode
        document.getElementById('editorTitle').textContent = `Edit Agent: ${state.currentAgent.name}`;
        document.getElementById('editorSubtitle').textContent = 'Modify agent configuration and system prompt';
        document.getElementById('agentName').value = state.currentAgent.name;
        document.getElementById('agentName').disabled = true;
        document.getElementById('agentModel').value = state.currentAgent.model;
        document.getElementById('agentSystemPrompt').value = state.currentAgent.system_prompt;
        document.getElementById('agentTemperature').value = state.currentAgent.temperature || 0.7;
        document.getElementById('temperatureValue').textContent = state.currentAgent.temperature || 0.7;
        document.getElementById('agentMaxTokens').value = state.currentAgent.max_tokens || 2048;
        document.getElementById('agentEnabled').checked = state.currentAgent.enabled;
        document.getElementById('deleteAgentBtn').style.display = 'flex';
        document.getElementById('viewHistoryBtn').style.display = 'flex';
    } else {
        // Create mode
        document.getElementById('editorTitle').textContent = 'Create New Agent';
        document.getElementById('editorSubtitle').textContent = 'Configure a new AI agent';
        document.getElementById('agentName').value = '';
        document.getElementById('agentName').disabled = false;
        document.getElementById('agentModel').value = 'google::gemini-2.5-flash';
        document.getElementById('agentSystemPrompt').value = '';
        document.getElementById('agentTemperature').value = 0.7;
        document.getElementById('temperatureValue').textContent = '0.7';
        document.getElementById('agentMaxTokens').value = 2048;
        document.getElementById('agentEnabled').checked = true;
        document.getElementById('deleteAgentBtn').style.display = 'none';
        document.getElementById('viewHistoryBtn').style.display = 'none';
    }
    
    document.getElementById('changeReason').value = '';
    renderAgentsList(); // Update active state
}

async function handleSaveAgent(e) {
    e.preventDefault();
    
    const agentData = {
        model: document.getElementById('agentModel').value,
        system_prompt: document.getElementById('agentSystemPrompt').value,
        temperature: parseFloat(document.getElementById('agentTemperature').value),
        max_tokens: parseInt(document.getElementById('agentMaxTokens').value),
        enabled: document.getElementById('agentEnabled').checked,
        change_reason: document.getElementById('changeReason').value || undefined
    };
    
    const agentName = document.getElementById('agentName').value;
    
    if (!agentName) {
        showToast('Agent name is required', 'error');
        return;
    }
    
    try {
        const url = `${API_BASE}/admin/agents/${agentName}`;
        const method = state.isEditMode ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-API-Key': state.adminApiKey
            },
            body: JSON.stringify(agentData)
        });
        
        if (response.ok) {
            const savedAgent = await response.json();
            showToast(`Agent ${state.isEditMode ? 'updated' : 'created'} successfully`, 'success');
            await loadAgents();
            state.currentAgent = savedAgent;
            state.isEditMode = true;
            showAgentEditor();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to save agent', 'error');
        }
    } catch (error) {
        showToast('Error saving agent', 'error');
    }
}

async function handleDeleteAgent() {
    if (!state.currentAgent) return;
    
    if (!confirm(`Are you sure you want to delete agent "${state.currentAgent.name}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/admin/agents/${state.currentAgent.name}`, {
            method: 'DELETE',
            headers: {
                'X-Admin-API-Key': state.adminApiKey
            }
        });
        
        if (response.ok) {
            showToast('Agent deleted successfully', 'success');
            await loadAgents();
            welcomeScreen.style.display = 'flex';
            agentEditor.style.display = 'none';
            state.currentAgent = null;
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to delete agent', 'error');
        }
    } catch (error) {
        showToast('Error deleting agent', 'error');
    }
}

async function showHistory() {
    if (!state.currentAgent) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/agents/${state.currentAgent.name}/history`, {
            headers: {
                'X-Admin-API-Key': state.adminApiKey
            }
        });
        
        if (response.ok) {
            const history = await response.json();
            renderHistory(history);
            historyModal.style.display = 'flex';
        } else {
            showToast('Failed to load history', 'error');
        }
    } catch (error) {
        showToast('Error loading history', 'error');
    }
}

function renderHistory(history) {
    if (history.length === 0) {
        historyContent.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 40px;">No history available</div>';
        return;
    }
    
    historyContent.innerHTML = history.map(item => `
        <div class="history-item">
            <div class="history-item-header">
                <div class="history-item-time">${new Date(item.changed_at).toLocaleString()}</div>
                <div class="history-item-author">${item.changed_by || 'Unknown'}</div>
            </div>
            ${item.change_reason ? `<div class="history-item-reason">Reason: ${item.change_reason}</div>` : ''}
            <div class="history-item-prompt">${item.new_prompt}</div>
        </div>
    `).join('');
}

// Toast Notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-message">${message}</div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}
