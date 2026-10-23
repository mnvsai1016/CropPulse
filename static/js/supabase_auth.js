/**
 * CropPulse Supabase & Google Authentication Client
 * Manages Google OAuth Sign-in, user sessions, and cloud chat history persistence.
 */

// Default Supabase project credentials for CropPulse
const DEFAULT_SUPABASE_URL = 'https://pqntyibigddhpbyvtzrr.supabase.co';
const DEFAULT_SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxbnR5aWJpZ2RkaHBieXZ0enJyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI3NTM2NzAsImV4cCI6MjEwODMyOTY3MH0.OdpRU1E7T0Oj31bf6Z8xUxAmgdQDeTkyrZ4XcZwdilo';

let supabaseClient = null;
let currentAuthUser = null;
let isSyncing = false;

/**
 * Basic HTML escaping helper for safe UI injection
 */
function escapeHtmlAuth(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Initialize Supabase client and register session / auth change handlers
 */
function initSupabase() {
    const url = window.SUPABASE_URL || localStorage.getItem('croppulse_supabase_url') || DEFAULT_SUPABASE_URL;
    const anonKey = window.SUPABASE_ANON_KEY || localStorage.getItem('croppulse_supabase_anon_key') || DEFAULT_SUPABASE_ANON_KEY;

    if (!url || !anonKey || typeof supabase === 'undefined') {
        console.log('[CropPulse Supabase] Supabase SDK not available or credentials missing. Operating in local storage guest mode.');
        updateAuthUI(null);
        return null;
    }

    try {
        supabaseClient = supabase.createClient(url, anonKey);
        console.log('[CropPulse Supabase] Supabase client initialized.');
        
        // 1. Check current session on page load
        supabaseClient.auth.getSession().then(({ data: { session }, error }) => {
            if (error) {
                console.warn('[CropPulse Supabase] Error retrieving active session:', error.message);
            }
            currentAuthUser = session ? session.user : null;
            updateAuthUI(currentAuthUser);
            if (currentAuthUser && typeof window.syncFromSupabaseToLocal === 'function') {
                console.log('[CropPulse Supabase] Active session detected on page load for user:', currentAuthUser.id);
                window.syncFromSupabaseToLocal();
            }
        }).catch(err => {
            console.error('[CropPulse Supabase] getSession unexpected exception:', err);
        });

        // 2. Listen for auth state transitions (Sign-in, Sign-out, Token refresh)
        supabaseClient.auth.onAuthStateChange((event, session) => {
            console.log('[CropPulse Supabase] Auth state changed:', event);
            currentAuthUser = session ? session.user : null;
            updateAuthUI(currentAuthUser);

            if ((event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED' || event === 'USER_UPDATED') && currentAuthUser) {
                console.log('[CropPulse Supabase] User authenticated:', currentAuthUser.email || currentAuthUser.id);
                if (typeof window.syncFromSupabaseToLocal === 'function') {
                    window.syncFromSupabaseToLocal();
                }
            } else if (event === 'SIGNED_OUT') {
                console.log('[CropPulse Supabase] User signed out.');
                currentAuthUser = null;
                updateAuthUI(null);
            }
        });

        return supabaseClient;
    } catch (e) {
        console.error('[CropPulse Supabase] Failed to initialize Supabase client:', e);
        return null;
    }
}

/**
 * Trigger Google OAuth sign-in flow
 */
async function signInWithGoogle() {
    if (!supabaseClient) {
        initSupabase();
        if (!supabaseClient) {
            promptForSupabaseConfig();
            return;
        }
    }

    try {
        console.log('[CropPulse Supabase] Redirecting to Google OAuth...');
        const { data, error } = await supabaseClient.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin + window.location.pathname
            }
        });
        if (error) throw error;
    } catch (err) {
        console.error('[CropPulse Supabase] Google Sign-In Error:', err);
        alert('Google Sign-In Error: ' + err.message);
    }
}

/**
 * Sign out current user
 */
async function signOutUser() {
    if (!supabaseClient) return;
    try {
        console.log('[CropPulse Supabase] Signing out...');
        const { error } = await supabaseClient.auth.signOut();
        if (error) throw error;
        currentAuthUser = null;
        updateAuthUI(null);
    } catch (err) {
        console.error('[CropPulse Supabase] Sign out error:', err);
    }
}

/**
 * Configure Supabase credentials modal / prompt for user
 */
function promptForSupabaseConfig() {
    const currentUrl = localStorage.getItem('croppulse_supabase_url') || '';
    const currentKey = localStorage.getItem('croppulse_supabase_anon_key') || '';

    const url = prompt('Enter your Supabase Project URL (e.g. https://xyz.supabase.co):', currentUrl);
    if (!url) return;
    const anonKey = prompt('Enter your Supabase Anon / Public Key:', currentKey);
    if (!anonKey) return;

    localStorage.setItem('croppulse_supabase_url', url.trim());
    localStorage.setItem('croppulse_supabase_anon_key', anonKey.trim());
    initSupabase();
    alert('Supabase credentials configured successfully! You can now click Sign in with Google.');
}

/**
 * Render Avatar Image with fallback to Initials badge
 */
function renderAvatarHtml(avatar, initial, fullName, size = 28, borderWidth = 2) {
    const escapedName = escapeHtmlAuth(fullName);
    const escapedInitial = escapeHtmlAuth(initial);
    const fontSize = size >= 28 ? 13 : 11;
    if (avatar) {
        return `
            <div style="position:relative;width:${size}px;height:${size}px;flex-shrink:0;">
                <img src="${escapeHtmlAuth(avatar)}" alt="${escapedName}" 
                    style="width:${size}px;height:${size}px;border-radius:50%;object-fit:cover;border:${borderWidth}px solid #2e7d32;display:block;" 
                    onerror="this.onerror=null;this.style.display='none';if(this.nextElementSibling)this.nextElementSibling.style.display='flex';">
                <div style="display:none;width:${size}px;height:${size}px;border-radius:50%;background:#2e7d32;color:#ffffff;font-size:${fontSize}px;font-weight:700;align-items:center;justify-content:center;border:${borderWidth}px solid #1b5e20;">${escapedInitial}</div>
            </div>
        `.trim();
    }
    return `
        <div style="width:${size}px;height:${size}px;border-radius:50%;background:#2e7d32;color:#ffffff;font-size:${fontSize}px;font-weight:700;display:flex;align-items:center;justify-content:center;border:${borderWidth}px solid #1b5e20;flex-shrink:0;">${escapedInitial}</div>
    `.trim();
}

/**
 * Update UI across the application (Navbar & Chatbot Header)
 */
function updateAuthUI(user) {
    // 1. Update Navbar Auth Container (Top Right Corner Icon + Dropdown)
    const navContainer = document.getElementById('navbar-auth-section');
    if (navContainer) {
        if (user) {
            const meta = user.user_metadata || {};
            const fullName = meta.full_name || meta.name || user.email?.split('@')[0] || 'User';
            const email = user.email || '';
            const avatar = meta.avatar_url || meta.picture || '';
            const initial = (fullName.trim().charAt(0) || 'U').toUpperCase();
            const escapedName = escapeHtmlAuth(fullName);
            const escapedEmail = escapeHtmlAuth(email);
            const avatarHtml = renderAvatarHtml(avatar, initial, fullName, 38, 2);

            navContainer.innerHTML = `
                <div class="nav-profile-wrapper" id="navProfileWrapper">
                    <button type="button" class="nav-profile-trigger" id="profileTriggerBtn" onclick="toggleProfileDropdown(event)" aria-label="User Account" title="${escapedName}">
                        ${avatarHtml}
                        <span class="nav-profile-status-dot" title="Online & Connected"></span>
                    </button>
                    <div class="nav-profile-dropdown" id="navProfileDropdown">
                        <div class="dropdown-user-header">
                            <div class="dropdown-avatar-wrap">
                                ${renderAvatarHtml(avatar, initial, fullName, 42, 2)}
                            </div>
                            <div class="dropdown-user-details">
                                <div class="dropdown-user-name">${escapedName}</div>
                                <div class="dropdown-user-email">${escapedEmail}</div>
                                <div class="dropdown-sync-pill"><i class="fas fa-check-circle"></i> Supabase Synced</div>
                            </div>
                        </div>
                        <div class="dropdown-menu-list">
                            <button type="button" class="dropdown-menu-item" onclick="openProfileModal(); closeProfileDropdown();">
                                <i class="fas fa-user-circle"></i>
                                <span>Profile</span>
                            </button>
                            <div class="dropdown-divider"></div>
                            <button type="button" class="dropdown-menu-item logout" onclick="signOutUser(); closeProfileDropdown();">
                                <i class="fas fa-sign-out-alt"></i>
                                <span>Logout</span>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        } else {
            navContainer.innerHTML = `
                <button onclick="signInWithGoogle()" class="nav-signin-compact-btn" title="Sign in with Google">
                    <i class="fab fa-google"></i>
                    <span>Sign In</span>
                </button>
            `;
        }
    }

    // 2. Update Chatbot Sidebar Auth Box
    const chatAuthBox = document.getElementById('chat-auth-box');
    if (chatAuthBox) {
        if (user) {
            const meta = user.user_metadata || {};
            const fullName = meta.full_name || meta.name || user.email?.split('@')[0] || 'User';
            const avatar = meta.avatar_url || meta.picture || '';
            const initial = (fullName.trim().charAt(0) || 'U').toUpperCase();
            const escapedName = escapeHtmlAuth(fullName);
            const avatarHtml = renderAvatarHtml(avatar, initial, fullName, 26, 1.5);

            chatAuthBox.innerHTML = `
                <div class="chat-auth-card" style="margin:0 10px 10px;padding:9px 10px;background:#ffffff;border-radius:10px;border:1px solid #c8e6c9;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px;">
                        <div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1;">
                            ${avatarHtml}
                            <div style="min-width:0;flex:1;">
                                <div class="chat-auth-name" style="font-size:12px;font-weight:600;color:#1e6b37;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.2;" title="${escapedName}">${escapedName}</div>
                            </div>
                        </div>
                        <button onclick="signOutUser()" class="chat-auth-signout-btn" style="background:transparent;border:none;color:#c62828;cursor:pointer;font-size:12px;padding:3px;border-radius:4px;display:flex;align-items:center;justify-content:center;transition:background 0.2s;" title="Sign out" aria-label="Sign out">
                            <i class="fas fa-sign-out-alt"></i>
                        </button>
                    </div>
                    <div style="display:inline-flex;align-items:center;gap:5px;background:#e8f5e9;color:#2e7d32;font-size:10px;font-weight:600;padding:2px 8px;border-radius:12px;border:1px solid #a5d6a7;">
                        <i class="fas fa-check-circle" style="font-size:9px;"></i> Cloud Synced
                    </div>
                </div>
            `;
        } else {
            chatAuthBox.innerHTML = `
                <div class="chat-auth-logged-out" style="margin:0 10px 10px;padding:10px;background:#ffffff;border:1px dashed #a5d6a7;border-radius:10px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                    <div style="display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:4px;color:#2e7d32;font-size:13px;">
                        <i class="fas fa-cloud" style="color:#4caf50;"></i>
                        <span style="font-weight:600;font-size:11.5px;color:#1e6b37;">Cloud Sync</span>
                    </div>
                    <p style="font-size:11px;color:#444;margin:0 0 8px 0;line-height:1.35;font-weight:500;">
                        Sign in with Google to sync history to cloud
                    </p>
                    <button onclick="signInWithGoogle()" class="chat-auth-signin-btn" style="width:100%;padding:6px 8px;background:#ffffff;border:1px solid #dcdcdc;border-radius:6px;font-size:11px;font-weight:600;color:#1e6b37;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;box-shadow:0 1px 3px rgba(0,0,0,0.05);transition:all 0.2s ease;">
                        <i class="fab fa-google" style="color:#ea4335;"></i> Sign in with Google
                    </button>
                </div>
            `;
        }
    }
}

/**
 * Cloud Synchronization: Push conversation to Supabase
 * @param {Object} conv - Conversation object { id, title, messages, ... }
 * @returns {Promise<boolean>}
 */
async function syncConversationToSupabase(conv) {
    if (!supabaseClient) {
        console.warn('[CropPulse Supabase] syncConversationToSupabase: Supabase client not initialized.');
        return false;
    }
    if (!currentAuthUser || !currentAuthUser.id) {
        // User not logged in; local storage persists chats
        return false;
    }
    if (!conv || typeof conv !== 'object') {
        console.warn('[CropPulse Supabase] syncConversationToSupabase skipped: invalid conversation object.', conv);
        return false;
    }

    // 1. Ensure id is a non-empty string
    let convId = '';
    if (typeof conv.id === 'string' && conv.id.trim().length > 0) {
        convId = conv.id.trim();
    } else if (typeof conv.id === 'number') {
        convId = String(conv.id);
    } else {
        convId = 'conv_' + Date.now();
        conv.id = convId;
    }

    // 2. Ensure user_id comes strictly from currentAuthUser.id
    const userId = String(currentAuthUser.id).trim();
    if (!userId) {
        console.error('[CropPulse Supabase] syncConversationToSupabase error: missing user_id on currentAuthUser.');
        return false;
    }

    // 3. Title sanitization
    const title = (typeof conv.title === 'string' && conv.title.trim().length > 0)
        ? conv.title.trim().slice(0, 100)
        : 'Chat';

    // 4. Message array sanitization (valid array of objects with role & content)
    const rawMessages = Array.isArray(conv.messages) ? conv.messages : [];
    const sanitizedMessages = rawMessages
        .filter(m => m && typeof m === 'object')
        .map(m => {
            const role = (m.role === 'user' || m.role === 'human') ? 'user' : 'bot';
            const content = typeof m.content === 'string' ? m.content : String(m.content || '');
            return { role, content };
        })
        .filter(m => m.content.trim().length > 0);

    const payload = {
        id: convId,
        user_id: userId,
        title: title,
        messages: sanitizedMessages,
        updated_at: new Date().toISOString()
    };

    try {
        console.log(`[CropPulse Supabase] Syncing conversation "${convId}" (${sanitizedMessages.length} msgs) for user ${userId}...`);
        const { error } = await supabaseClient
            .from('chat_conversations')
            .upsert(payload, { onConflict: 'id' });

        if (error) {
            console.error('[CropPulse Supabase] Error syncing conversation to Supabase:', error.message || error, { payload });
            return false;
        }

        console.log(`[CropPulse Supabase] Successfully synced conversation "${convId}" to Supabase.`);
        return true;
    } catch (err) {
        console.error('[CropPulse Supabase] Unexpected exception while syncing conversation:', err);
        return false;
    }
}

/**
 * Cloud Synchronization: Pull all user conversations from Supabase
 * @returns {Promise<Array|null>}
 */
async function loadConversationsFromSupabase() {
    if (!supabaseClient) {
        console.warn('[CropPulse Supabase] loadConversationsFromSupabase: Supabase client not initialized.');
        return null;
    }
    if (!currentAuthUser || !currentAuthUser.id) {
        console.log('[CropPulse Supabase] loadConversationsFromSupabase: No authenticated user.');
        return null;
    }

    try {
        const userId = String(currentAuthUser.id).trim();
        console.log(`[CropPulse Supabase] Querying chat_conversations for user_id "${userId}"...`);

        const { data, error } = await supabaseClient
            .from('chat_conversations')
            .select('id, user_id, title, messages, updated_at')
            .eq('user_id', userId)
            .order('updated_at', { ascending: false });

        if (error) {
            console.error('[CropPulse Supabase] Failed to fetch conversations from Supabase:', error.message || error);
            return null;
        }

        console.log(`[CropPulse Supabase] Loaded ${data ? data.length : 0} cloud conversations.`);
        return Array.isArray(data) ? data : [];
    } catch (err) {
        console.error('[CropPulse Supabase] Unexpected exception fetching conversations from Supabase:', err);
        return null;
    }
}

/**
 * Cloud Synchronization: Delete conversation from Supabase
 * @param {string} conversationId - The conversation ID to delete
 * @returns {Promise<boolean>}
 */
async function deleteConversationFromSupabase(conversationId) {
    if (!supabaseClient) {
        console.warn('[CropPulse Supabase] deleteConversation: Supabase client not initialized.');
        return false;
    }
    if (!currentAuthUser || !currentAuthUser.id) {
        // User not logged in, no cloud record to delete
        return false;
    }
    if (!conversationId) {
        console.warn('[CropPulse Supabase] deleteConversation: No conversation ID provided.');
        return false;
    }

    const idStr = String(conversationId).trim();
    const userId = String(currentAuthUser.id).trim();

    try {
        console.log(`[CropPulse Supabase] Deleting conversation "${idStr}" for user ${userId}...`);
        const { error } = await supabaseClient
            .from('chat_conversations')
            .delete()
            .eq('id', idStr)
            .eq('user_id', userId);

        if (error) {
            console.error(`[CropPulse Supabase] Error deleting conversation "${idStr}" from Supabase:`, error.message || error);
            return false;
        }

        console.log(`[CropPulse Supabase] Successfully deleted conversation "${idStr}" from Supabase.`);
        return true;
    } catch (err) {
        console.error(`[CropPulse Supabase] Unexpected exception deleting conversation "${idStr}":`, err);
        return false;
    }
}

/**
 * Global hook to pull cloud conversations, merge with local sessions, and refresh sidebar
 */
window.syncFromSupabaseToLocal = async function() {
    if (isSyncing) {
        console.log('[CropPulse Supabase] Sync already in progress, skipping duplicate call.');
        return;
    }
    if (!currentAuthUser || !currentAuthUser.id) {
        console.log('[CropPulse Supabase] Cannot sync to local: No authenticated user.');
        return;
    }

    isSyncing = true;
    try {
        console.log('[CropPulse Supabase] Pulling conversations from Supabase for merge...');
        const cloudChats = await loadConversationsFromSupabase();

        // 1. Read existing local sessions
        let localSessions = [];
        try {
            const raw = localStorage.getItem('croppulse_chat_sessions');
            localSessions = raw ? JSON.parse(raw) : [];
            if (!Array.isArray(localSessions)) localSessions = [];
        } catch (_) {
            localSessions = [];
        }

        // 2. Map existing local sessions by string ID
        const sessionMap = new Map();
        localSessions.forEach(s => {
            if (s && s.id !== undefined && s.id !== null) {
                sessionMap.set(String(s.id), s);
            }
        });

        // 3. Merge cloud chats into sessionMap
        if (cloudChats && Array.isArray(cloudChats) && cloudChats.length > 0) {
            cloudChats.forEach(c => {
                if (!c || c.id === undefined || c.id === null) return;
                const idStr = String(c.id);
                const cloudTime = c.updated_at ? new Date(c.updated_at).getTime() : Date.now();
                const existing = sessionMap.get(idStr);

                // Format timestamp helper
                const timeLabel = (typeof formatTimestamp === 'function')
                    ? formatTimestamp(cloudTime)
                    : new Date(cloudTime).toLocaleDateString([], { month: 'short', day: 'numeric' });

                const cloudMessages = Array.isArray(c.messages)
                    ? c.messages
                        .filter(m => m && typeof m === 'object')
                        .map(m => ({
                            role: (m.role === 'user' || m.role === 'human') ? 'user' : 'bot',
                            content: typeof m.content === 'string' ? m.content : String(m.content || '')
                        }))
                    : [];

                // If local exists and has more messages or newer timestamp, keep local and re-sync
                if (existing && (existing.createdAt || 0) > cloudTime && Array.isArray(existing.messages) && existing.messages.length > cloudMessages.length) {
                    syncConversationToSupabase(existing);
                } else {
                    sessionMap.set(idStr, {
                        id: c.id,
                        title: c.title || 'Chat',
                        timestamp: timeLabel,
                        createdAt: cloudTime,
                        messages: cloudMessages
                    });
                }
            });

            // 4. Back up any existing local-only conversations to cloud
            const cloudIds = new Set(cloudChats.map(c => String(c.id)));
            localSessions.forEach(s => {
                if (s && s.id && !cloudIds.has(String(s.id)) && Array.isArray(s.messages) && s.messages.length > 0) {
                    console.log(`[CropPulse Supabase] Backing up local-only session "${s.id}" to Supabase...`);
                    syncConversationToSupabase(s);
                }
            });
        } else if (localSessions.length > 0) {
            // User is signed in but has no cloud chats yet -> back up existing local chats!
            console.log('[CropPulse Supabase] Initial cloud sync: Backing up existing local sessions to Supabase...');
            localSessions.forEach(s => {
                if (s && s.id && Array.isArray(s.messages) && s.messages.length > 0) {
                    syncConversationToSupabase(s);
                }
            });
        }

        // 5. Sort merged list descending by createdAt, keep up to 20
        const merged = Array.from(sessionMap.values())
            .sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0))
            .slice(0, 20);

        localStorage.setItem('croppulse_chat_sessions', JSON.stringify(merged));
        console.log(`[CropPulse Supabase] Merged ${merged.length} conversations into localStorage.`);

        // 6. Trigger sidebar re-render so user immediately sees their previous conversations
        if (typeof window.renderHistorySidebar === 'function') {
            window.renderHistorySidebar();
        } else if (typeof renderHistorySidebar === 'function') {
            renderHistorySidebar();
        }
    } catch (err) {
        console.error('[CropPulse Supabase] Exception during syncFromSupabaseToLocal:', err);
    } finally {
        isSyncing = false;
    }
};

// Global hooks for chatbot to sync and delete
window.syncCurrentChatToCloud = syncConversationToSupabase;
window.syncConversationToSupabase = syncConversationToSupabase;
window.loadConversationsFromSupabase = loadConversationsFromSupabase;
window.deleteConversationFromCloud = deleteConversationFromSupabase;
window.deleteConversationFromSupabase = deleteConversationFromSupabase;

window.getCurrentAuthUser = function() {
    return currentAuthUser;
};

window.getSupabaseClient = function() {
    return supabaseClient;
};

// Dropdown menu toggle & close
window.toggleProfileDropdown = function(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const dropdown = document.getElementById('navProfileDropdown');
    if (!dropdown) return;
    dropdown.classList.toggle('show');
};

window.closeProfileDropdown = function() {
    const dropdown = document.getElementById('navProfileDropdown');
    if (dropdown) dropdown.classList.remove('show');
};

document.addEventListener('click', function(e) {
    const wrapper = document.getElementById('navProfileWrapper');
    if (wrapper && !wrapper.contains(e.target)) {
        window.closeProfileDropdown();
    }
});

// Profile Modal open & close
window.openProfileModal = function() {
    const modal = document.getElementById('userProfileModal');
    if (!modal) return;

    const user = currentAuthUser;
    const meta = user?.user_metadata || {};
    const fullName = meta.full_name || meta.name || user?.email?.split('@')[0] || 'User';
    const email = user?.email || 'Not available';
    const avatar = meta.avatar_url || meta.picture || '';
    const initial = (fullName.trim().charAt(0) || 'U').toUpperCase();

    let localSessions = [];
    try {
        localSessions = JSON.parse(localStorage.getItem('croppulse_chat_sessions') || '[]');
    } catch (_) {}

    const modalBody = document.getElementById('userProfileModalBody');
    if (modalBody) {
        modalBody.innerHTML = `
            <div style="display:flex;align-items:center;gap:14px;padding-bottom:16px;border-bottom:1px solid #eef2ee;margin-bottom:16px;">
                ${renderAvatarHtml(avatar, initial, fullName, 52, 2)}
                <div style="min-width:0;flex:1;">
                    <div style="font-size:16px;font-weight:700;color:#1e6b37;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtmlAuth(fullName)}</div>
                    <div style="font-size:13px;color:#666;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtmlAuth(email)}</div>
                    <div style="display:inline-flex;align-items:center;gap:5px;background:#e8f5e9;color:#2e7d32;font-size:11px;font-weight:600;padding:2px 8px;border-radius:12px;margin-top:6px;border:1px solid #c8e6c9;">
                        <i class="fab fa-google" style="color:#ea4335;"></i> Google Verified
                    </div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:13px;">
                <div style="background:#f8faf8;padding:12px;border-radius:10px;border:1px solid #e8f5e9;">
                    <div style="color:#888;font-size:11px;text-transform:uppercase;font-weight:600;">Cloud Database</div>
                    <div style="font-weight:600;color:#1e6b37;margin-top:3px;">Supabase PostgreSQL</div>
                </div>
                <div style="background:#f8faf8;padding:12px;border-radius:10px;border:1px solid #e8f5e9;">
                    <div style="color:#888;font-size:11px;text-transform:uppercase;font-weight:600;">Saved Chats</div>
                    <div style="font-weight:600;color:#1e6b37;margin-top:3px;">${localSessions.length} Synchronized</div>
                </div>
            </div>
            <div style="margin-top:14px;padding:10px 12px;background:#e8f5e9;border-radius:8px;font-size:12px;color:#2e7d32;display:flex;align-items:center;gap:8px;">
                <i class="fas fa-shield-alt" style="font-size:14px;"></i>
                <span>Your chat history and leaf diagnostics are backed up securely.</span>
            </div>
        `;
    }
    modal.style.display = 'flex';
};

window.closeProfileModal = function() {
    const modal = document.getElementById('userProfileModal');
    if (modal) modal.style.display = 'none';
};

document.addEventListener('DOMContentLoaded', () => {
    initSupabase();
});
