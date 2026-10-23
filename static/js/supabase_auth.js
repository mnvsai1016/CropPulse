/**
 * CropPulse Supabase & Google Authentication Client
 * Manages Google OAuth Sign-in, user sessions, and cloud chat history persistence.
 */

// Replace these placeholders with your Supabase project credentials,
// or configure them via window.SUPABASE_CONFIG = { url: '...', anonKey: '...' }
const DEFAULT_SUPABASE_URL = window.SUPABASE_URL || '';
const DEFAULT_SUPABASE_ANON_KEY = window.SUPABASE_ANON_KEY || '';

let supabaseClient = null;
let currentAuthUser = null;

function initSupabase() {
    const url = window.SUPABASE_URL || localStorage.getItem('croppulse_supabase_url') || DEFAULT_SUPABASE_URL;
    const anonKey = window.SUPABASE_ANON_KEY || localStorage.getItem('croppulse_supabase_anon_key') || DEFAULT_SUPABASE_ANON_KEY;

    if (!url || !anonKey || typeof supabase === 'undefined') {
        console.log('[CropPulse Auth] Supabase not yet configured. Operating in local storage guest mode.');
        updateAuthUI(null);
        return null;
    }

    try {
        supabaseClient = supabase.createClient(url, anonKey);
        
        // Check current session
        supabaseClient.auth.getSession().then(({ data: { session } }) => {
            currentAuthUser = session ? session.user : null;
            updateAuthUI(currentAuthUser);
            if (currentAuthUser && typeof window.syncFromSupabaseToLocal === 'function') {
                window.syncFromSupabaseToLocal();
            }
        });

        // Listen for auth state transitions (Sign-in, Sign-out, Token refresh)
        supabaseClient.auth.onAuthStateChange((event, session) => {
            currentAuthUser = session ? session.user : null;
            updateAuthUI(currentAuthUser);
            if (event === 'SIGNED_IN' && typeof window.syncFromSupabaseToLocal === 'function') {
                window.syncFromSupabaseToLocal();
            }
        });

        return supabaseClient;
    } catch (e) {
        console.error('[CropPulse Auth] Failed to initialize Supabase client:', e);
        return null;
    }
}

/**
 * Trigger Google OAuth sign-in flow
 */
async function signInWithGoogle() {
    if (!supabaseClient) {
        promptForSupabaseConfig();
        return;
    }

    try {
        const { data, error } = await supabaseClient.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin + window.location.pathname
            }
        });
        if (error) throw error;
    } catch (err) {
        alert('Google Sign-In Error: ' + err.message);
    }
}

/**
 * Sign out current user
 */
async function signOutUser() {
    if (!supabaseClient) return;
    try {
        await supabaseClient.auth.signOut();
        currentAuthUser = null;
        updateAuthUI(null);
    } catch (err) {
        console.error('Sign out error:', err);
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
 * Update UI across the application (Navbar & Chatbot Header)
 */
function updateAuthUI(user) {
    // 1. Update Navbar Auth Container
    const navContainer = document.getElementById('navbar-auth-section');
    if (navContainer) {
        if (user) {
            const avatar = user.user_metadata?.avatar_url || 'https://www.gravatar.com/avatar/?d=mp';
            const name = user.user_metadata?.full_name || user.email?.split('@')[0] || 'User';
            navContainer.innerHTML = `
                <div style="display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.15);padding:4px 10px;border-radius:20px;border:1px solid rgba(255,255,255,0.25);">
                    <img src="${avatar}" style="width:24px;height:24px;border-radius:50%;object-fit:cover;" alt="Avatar">
                    <span style="font-size:13px;color:white;font-weight:500;max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${name}</span>
                    <button onclick="signOutUser()" style="background:transparent;border:none;color:#ffcdd2;cursor:pointer;font-size:12px;margin-left:4px;" title="Sign out"><i class="fas fa-sign-out-alt"></i></button>
                </div>
            `;
        } else {
            navContainer.innerHTML = `
                <button onclick="signInWithGoogle()" style="background:#ffffff;color:#1e6b37;border:none;border-radius:18px;padding:6px 14px;font-size:13px;font-weight:600;display:flex;align-items:center;gap:6px;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.12);transition:all 0.15s ease;">
                    <i class="fab fa-google" style="color:#ea4335;"></i> Sign In
                </button>
            `;
        }
    }

    // 2. Update Chatbot Sidebar Auth Box
    const chatAuthBox = document.getElementById('chat-auth-box');
    if (chatAuthBox) {
        if (user) {
            const name = user.user_metadata?.full_name || user.email?.split('@')[0] || 'User';
            chatAuthBox.innerHTML = `
                <div style="padding:8px 10px;background:#ffffff;border-radius:8px;border:1px solid #c8e6c9;font-size:11px;color:#2e7d32;display:flex;align-items:center;justify-content:space-between;margin:0 10px 10px;">
                    <span style="display:flex;align-items:center;gap:5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                        <i class="fas fa-cloud-check" style="color:#2e7d32;"></i> ${name}
                    </span>
                    <button onclick="signOutUser()" style="background:transparent;border:none;color:#888;cursor:pointer;font-size:11px;" title="Sign Out"><i class="fas fa-sign-out-alt"></i></button>
                </div>
            `;
        } else {
            chatAuthBox.innerHTML = `
                <div style="margin:0 10px 10px;padding:8px;background:#f1f8e9;border:1px dashed #a5d6a7;border-radius:8px;text-align:center;">
                    <div style="font-size:10.5px;color:#33691e;margin-bottom:6px;line-height:1.3;">Sign in to sync your chat history to the cloud:</div>
                    <button onclick="signInWithGoogle()" style="width:100%;padding:5px 8px;background:#ffffff;border:1px solid #c8e6c9;border-radius:6px;font-size:11px;font-weight:600;color:#2e7d32;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;">
                        <i class="fab fa-google" style="color:#ea4335;"></i> Google Sign In
                    </button>
                </div>
            `;
        }
    }
}

/**
 * Cloud Synchronization: Push conversation to Supabase
 */
async function syncConversationToSupabase(conv) {
    if (!supabaseClient || !currentAuthUser || !conv) return;

    try {
        const { error } = await supabaseClient
            .from('chat_conversations')
            .upsert({
                id: conv.id,
                user_id: currentAuthUser.id,
                title: conv.title || 'Chat',
                messages: conv.messages || [],
                updated_at: new Date().toISOString()
            });

        if (error) {
            console.warn('[CropPulse Auth] Error syncing conversation to Supabase:', error.message);
        }
    } catch (err) {
        console.warn('[CropPulse Auth] Supabase sync exception:', err);
    }
}

/**
 * Cloud Synchronization: Pull all user conversations from Supabase
 */
async function loadConversationsFromSupabase() {
    if (!supabaseClient || !currentAuthUser) return null;

    try {
        const { data, error } = await supabaseClient
            .from('chat_conversations')
            .select('*')
            .eq('user_id', currentAuthUser.id)
            .order('updated_at', { ascending: false });

        if (error) throw error;
        return data || [];
    } catch (err) {
        console.warn('[CropPulse Auth] Failed to fetch conversations from Supabase:', err);
        return null;
    }
}

// Global hook for chatbot to sync
window.syncFromSupabaseToLocal = async function() {
    const cloudChats = await loadConversationsFromSupabase();
    if (cloudChats && cloudChats.length > 0) {
        const localSessions = JSON.parse(localStorage.getItem('croppulse_chat_sessions') || '[]');
        const localMap = new Map(localSessions.map(s => [String(s.id), s]));

        cloudChats.forEach(c => {
            localMap.set(String(c.id), {
                id: c.id,
                title: c.title,
                timestamp: new Date(c.updated_at).toLocaleDateString([], { month: 'short', day: 'numeric' }),
                createdAt: new Date(c.updated_at).getTime(),
                messages: c.messages || []
            });
        });

        const merged = Array.from(localMap.values()).sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0)).slice(0, 20);
        localStorage.setItem('croppulse_chat_sessions', JSON.stringify(merged));
        if (typeof renderHistorySidebar === 'function') {
            renderHistorySidebar();
        }
    }
};

window.syncCurrentChatToCloud = function(conv) {
    syncConversationToSupabase(conv);
};

document.addEventListener('DOMContentLoaded', () => {
    initSupabase();
});
