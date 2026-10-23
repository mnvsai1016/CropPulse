// CropPulse Chatbot frontend integration

const SESSIONS_KEY = 'agri_chat_sessions';
const SESSION_STORAGE_KEY = 'agri_guide_chat_session_id';
const HISTORY_KEY = 'agri_chat_history';

let SESSION_ID = sessionStorage.getItem(SESSION_STORAGE_KEY);
if (!SESSION_ID) {
    SESSION_ID = 'session_' + Math.random().toString(36).substring(2, 11);
    sessionStorage.setItem(SESSION_STORAGE_KEY, SESSION_ID);
}

let chatHistory = [];
try {
    const rawHistory = sessionStorage.getItem(HISTORY_KEY);
    chatHistory = rawHistory ? JSON.parse(rawHistory) : [];
    if (!Array.isArray(chatHistory)) chatHistory = [];
} catch (_) {
    chatHistory = [];
}
let activeConversationId = null;
let isSendingMessage = false;

// Generate short topic name from first user message (max 5 words, no API)
function generateTopicName(message) {
    const stopWords = new Set(['what', 'how', 'do', 'i', 'a', 'an', 'the', 'for', 'to', 'is', 'should', 'can', 'does', 'with', 'my', 'this', 'that', 'it', 'please', 'tell', 'me', 'about', 'spray', 'fix', 'improve', 'help', 'get', 'use', 'and', 'or', 'in', 'on', 'at']);
    const words = String(message || '').toLowerCase().replace(/[^\w\s]/g, ' ').split(/\s+/).filter(w => w.length > 0 && !stopWords.has(w));
    const taken = words.slice(0, 5).map(w => w.charAt(0).toUpperCase() + w.slice(1));
    return taken.length ? taken.join(' ') : 'Chat';
}

// Format timestamp for display: "Today 2:30 PM", "Yesterday 4:15 PM"
function formatTimestamp(ms) {
    const d = new Date(ms);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today.getTime() - 86400000);
    const dDate = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    const timeStr = d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    if (dDate.getTime() === today.getTime()) return 'Today ' + timeStr;
    if (dDate.getTime() === yesterday.getTime()) return 'Yesterday ' + timeStr;
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ' ' + timeStr;
}

// Save current conversation to sessions (if >= 2 messages). Keep last 5.
function saveConversation() {
    const userCount = chatHistory.filter(m => m.role === 'user').length;
    const botCount = chatHistory.filter(m => m.role === 'bot').length;
    if (userCount < 1 || botCount < 1) return;

    let sessions = [];
    try {
        sessions = JSON.parse(sessionStorage.getItem(SESSIONS_KEY) || '[]');
    } catch (_) {}

    const firstUser = chatHistory.find(m => m.role === 'user');
    const title = firstUser ? generateTopicName(firstUser.content) : 'Chat';
    const ts = Date.now();

    const timeLabel = formatTimestamp(ts);
    const entry = {
        id: activeConversationId !== null ? activeConversationId : ts,
        title: title + ' · ' + timeLabel.split(' ').pop(),
        timestamp: timeLabel,
        createdAt: ts,
        messages: chatHistory.map(m => ({ role: m.role, content: m.content }))
    };

    sessions = sessions.filter(s => s.id !== activeConversationId && s.id !== entry.id);
    sessions.unshift(entry);
    if (sessions.length > 5) sessions = sessions.slice(0, 5);

    sessionStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
}

// Delete a saved conversation by id
function deleteConversation(sessionId, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    let sessions = [];
    try {
        sessions = JSON.parse(sessionStorage.getItem(SESSIONS_KEY) || '[]');
    } catch (_) {}
    const idStr = String(sessionId);
    sessions = sessions.filter(s => String(s.id) !== idStr);
    sessionStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
    if (activeConversationId !== null && String(activeConversationId) === idStr) {
        activeConversationId = null;
        chatHistory = [];
        sessionStorage.removeItem(HISTORY_KEY);
        const body = document.getElementById('chat-body');
        if (body) body.innerHTML = '';
        appendMessage('bot', 'Hello! I am your CropPulse assistant. Ask me anything about crops, yield, soil health, or fertilizers.');
    }
    renderHistorySidebar();
}

// Load a saved conversation by id
function loadConversation(sessionId) {
    let sessions = [];
    try {
        sessions = JSON.parse(sessionStorage.getItem(SESSIONS_KEY) || '[]');
    } catch (_) {}
    const conv = sessions.find(s => String(s.id) === String(sessionId));
    if (!conv) return;

    activeConversationId = conv.id;
    chatHistory = (conv.messages || []).map(m => ({ role: m.role, content: m.content }));
    sessionStorage.setItem(HISTORY_KEY, JSON.stringify(chatHistory));

    renderHistorySidebar();
    restoreChatHistory();
}

// Render sidebar with saved conversations
function renderHistorySidebar() {
    const list = document.getElementById('chat-history-list');
    if (!list) return;

    let sessions = [];
    try {
        sessions = JSON.parse(sessionStorage.getItem(SESSIONS_KEY) || '[]');
    } catch (_) {}

    list.innerHTML = '';
    sessions.forEach(s => {
        const card = document.createElement('div');
        const isActive = activeConversationId !== null && String(s.id) === String(activeConversationId);
        const tsDisplay = s.timestamp || formatTimestamp(s.createdAt || (typeof s.id === 'number' ? s.id : Date.now()));
        card.style.cssText = `padding:10px 12px;background:${isActive ? '#e8f5e9' : '#fff'};border-radius:8px;cursor:pointer;border:1px solid ${isActive ? '#2d7a2d' : '#eee'};font-size:12px;display:flex;align-items:flex-start;justify-content:space-between;gap:8px;`;
        card.setAttribute('data-session-id', String(s.id));
        card.innerHTML = `<div style="flex:1;min-width:0;"><div style="font-weight:500;color:#333;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(s.title || 'Chat')}</div><div style="font-size:10px;color:#888;">${escapeHtml(tsDisplay)}</div></div><button type="button" class="chat-delete-btn" style="flex-shrink:0;background:transparent;border:none;color:#999;cursor:pointer;padding:2px;font-size:12px;" title="Delete"><i class="fas fa-trash-alt"></i></button>`;
        card.onclick = (e) => { if (!e.target.closest('button')) loadConversation(s.id); };
        const deleteBtn = card.querySelector('.chat-delete-btn');
        if (deleteBtn) {
            deleteBtn.onclick = function (e) {
                e.preventDefault();
                e.stopPropagation();
                deleteConversation(card.getAttribute('data-session-id'), e);
            };
        }
        list.appendChild(card);
    });
}

// Start new chat: save current if has messages, clear, new SESSION_ID, welcome
function startNewChat() {
    saveConversation();

    SESSION_ID = 'session_' + Math.random().toString(36).substr(2, 9);
    sessionStorage.setItem(SESSION_STORAGE_KEY, SESSION_ID);
    activeConversationId = null;

    chatHistory = [];
    sessionStorage.removeItem(HISTORY_KEY);

    renderHistorySidebar();
    const body = document.getElementById('chat-body');
    if (body) body.innerHTML = '';
    appendMessage('bot', 'Hello! I am your CropPulse assistant. Ask me anything about crops, yield, soil health, or fertilizers.');
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatBotMessage(raw) {
    const text = escapeHtml(raw || '');
    const lines = text.split(/\r?\n/);
    const htmlParts = [];
    let i = 0;

    function applyInlineFormatting(s) {
        return s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    }

    while (i < lines.length) {
        if (lines[i].trim() === '') { i++; continue; }
        if (/^(\*|-)\s+/.test(lines[i])) {
            const items = [];
            while (i < lines.length && /^(\*|-)\s+/.test(lines[i])) {
                items.push(`<li>${applyInlineFormatting(lines[i].replace(/^(\*|-)\s+/, '').trim())}</li>`);
                i++;
            }
            htmlParts.push(`<ul style="margin:6px 0 8px 18px;padding:0;">${items.join('')}</ul>`);
            continue;
        }
        const paraLines = [];
        while (i < lines.length && lines[i].trim() !== '' && !/^(\*|-)\s+/.test(lines[i])) {
            paraLines.push(lines[i].trim());
            i++;
        }
        htmlParts.push(`<p style="margin:0 0 8px 0;">${applyInlineFormatting(paraLines.join(' '))}</p>`);
    }
    return htmlParts.join('');
}

function toggleChat() {
    const win = document.getElementById('chat-window');
    if (!win) return;
    const isOpen = win.style.display === 'flex';
    if (isOpen) {
        saveConversation();
        win.style.display = 'none';
    } else {
        win.style.display = 'flex';
        restoreChatHistory();
        renderHistorySidebar();
        const input = document.getElementById('chat-input');
        if (input) input.focus();
    }
}

function restoreChatHistory() {
    const body = document.getElementById('chat-body');
    if (!body) return;
    body.innerHTML = '';
    if (chatHistory.length === 0) {
        appendMessage('bot', 'Hello! I am your CropPulse assistant. Ask me anything about crops, yield, soil health, or fertilizers.');
    } else {
        chatHistory.forEach(msg => appendMessage(msg.role, msg.content, false));
    }
}

function appendMessage(role, content, save = true) {
    const body = document.getElementById('chat-body');
    if (!body) return;
    const wrapper = document.createElement('div');
    wrapper.style.cssText = `display:flex;justify-content:${role === 'user' ? 'flex-end' : 'flex-start'};margin-bottom:8px;`;
    const bubble = document.createElement('div');
    bubble.style.cssText = `max-width:80%;padding:10px 14px;border-radius:${role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px'};background:${role === 'user' ? '#2d7a2d' : '#f0f0f0'};color:${role === 'user' ? '#fff' : '#222'};font-size:14px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word;`;
    if (role === 'user') {
        bubble.textContent = content;
    } else {
        bubble.style.whiteSpace = 'normal';
        bubble.innerHTML = formatBotMessage(content);
    }
    wrapper.appendChild(bubble);
    body.appendChild(wrapper);
    body.scrollTop = body.scrollHeight;
    if (save) {
        chatHistory.push({ role, content });
        sessionStorage.setItem(HISTORY_KEY, JSON.stringify(chatHistory));
    }
}

function appendSources(sources) {
    if (!sources || sources.length === 0) return;
    const body = document.getElementById('chat-body');
    if (!body) return;
    const el = document.createElement('div');
    el.style.cssText = 'font-size:11px;color:#888;margin-bottom:8px;padding-left:4px;';
    el.textContent = 'Sources: ' + sources.join(', ');
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
}

function showTyping() {
    const body = document.getElementById('chat-body');
    if (!body) return;
    const el = document.createElement('div');
    el.id = 'typing-indicator';
    el.style.cssText = 'display:flex;justify-content:flex-start;margin-bottom:8px;';
    el.innerHTML = '<div style="background:#f0f0f0;padding:10px 14px;border-radius:18px 18px 18px 4px;color:#888;font-size:13px;">Thinking...</div>';
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

async function sendMessage() {
    if (isSendingMessage) return;
    const input = document.getElementById('chat-input');
    if (!input) return;
    const message = input.value.trim();
    if (!message) return;

    isSendingMessage = true;
    input.value = '';
    appendMessage('user', message);
    showTyping();
    const sendBtn = document.getElementById('chat-send-btn');
    if (sendBtn) sendBtn.disabled = true;
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: SESSION_ID,
                context: window.chatContext || null
            })
        });
        const data = await response.json();
        hideTyping();
        if (data.reply) {
            appendMessage('bot', data.reply);
            appendSources(data.sources);
        } else if (data.error) {
            appendMessage('bot', data.error);
        } else {
            appendMessage('bot', 'Sorry, something went wrong. Please try again.');
        }
    } catch (error) {
        hideTyping();
        appendMessage('bot', 'Connection error. Please try again.');
    } finally {
        isSendingMessage = false;
        if (sendBtn) sendBtn.disabled = false;
        if (input) input.focus();
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function clearChat() {
    startNewChat();
}

function toggleHistorySidebar() {
    const sidebar = document.getElementById('chat-sidebar');
    if (!sidebar) return;
    const isVisible = sidebar.style.display === 'flex';
    sidebar.style.display = isVisible ? 'none' : 'flex';
}

function dismissChatIntro() {
    const toast = document.getElementById('chat-intro-toast');
    if (toast) toast.style.display = 'none';
    sessionStorage.setItem('agri_chat_intro_shown', '1');
}

function maybeShowChatIntro() {
    const path = window.location.pathname || '/';
    const isHome = path === '/' || path === '';
    if (!isHome) return;
    if (sessionStorage.getItem('agri_chat_intro_shown')) return;
    const toast = document.getElementById('chat-intro-toast');
    if (toast) toast.style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function () {
    restoreChatHistory();
    renderHistorySidebar();
    maybeShowChatIntro();
});
