// Constants and initial setup
const apiUrl = "http://127.0.0.1:5000";

// Get fresh token from localStorage
function getToken() {
    return localStorage.getItem("token");
}

// Authentication check
function checkAuth() {
    const token = getToken();
    const allowedPaths = ['/', '/login', '/register'];
    const currentPath = window.location.pathname;
    
    if (!token && !allowedPaths.some(path => currentPath === path || currentPath.startsWith(path + '/'))) {
        localStorage.clear();
        window.location.href = '/';
        return false;
    }
    return true;
}

// Enhanced authenticated fetch function
async function authenticatedFetch(url, options = {}) {
    const token = getToken();
    if (!token) {
        localStorage.clear();
        window.location.href = '/';
        throw new Error("Authentication token is missing");
    }

    const fullUrl = url.startsWith('http') ? url : `${apiUrl}${url.startsWith('/') ? '' : '/'}${url}`;
    
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
    };

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const response = await fetch(fullUrl, { 
            ...options, 
            headers,
            credentials: 'include'  // Important for cookies if using them
        });

        clearTimeout(timeoutId);

        if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
            throw new Error("Session expired. Please login again.");
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.msg || `Request failed with status ${response.status}`);
        }

        return response;
    } catch (error) {
        console.error("Fetch error:", error);
        if (error.name === 'AbortError') {
            throw new Error("Request timed out. Please try again.");
        } else if (error.name === 'TypeError') {
            throw new Error("Network error. Please check your connection.");
        }
        throw error;
    }
}

// DOM elements cache
const elements = {
    userEmail: document.getElementById("userEmail"),
    btnLogout: document.getElementById("btnLogout"),
    btnCompose: document.getElementById("btnCompose"),
    btnInbox: document.getElementById("btnInbox"),
    btnSent: document.getElementById("btnSent"),
    messageList: document.getElementById("messageList"),
    sentList: document.getElementById("sentList"),
    sendBtn: document.getElementById("sendBtn"),
    emailInput: document.getElementById("to"),
    subjectInput: document.getElementById("subject"),
    bodyInput: document.getElementById("body"),
    refreshInbox: document.getElementById("refreshInbox"),
    refreshSent: document.getElementById("refreshSent"),
    notification: document.getElementById("notification")
};

// Helper functions
function validateEmailFormat(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showNotification(message, isError = false) {
    if (!elements.notification) return;
    
    elements.notification.textContent = message;
    elements.notification.className = `notification ${isError ? "error" : ""} show`;
    setTimeout(() => {
        elements.notification?.classList.remove("show");
    }, 3000);
}

// API functions
async function loadInbox() {
    try {
        if (!elements.messageList) return;
        
        elements.messageList.innerHTML = `<div class="loading-msg"><i class="fas fa-spinner fa-spin"></i> Loading inbox...</div>`;

        const response = await authenticatedFetch("/api/inbox");
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.msg || "Failed to load inbox");
        }

        const messages = data.messages || [];
        
        elements.messageList.innerHTML = messages.length ? 
            messages.map(msg => `
                <div class="message-item" data-id="${msg.id}">
                    <div class="message-header">
                        <span class="from">
                            <i class="fas fa-user"></i> 
                            ${msg.sender_email || 'Unknown sender'}
                        </span>
                        <span class="date">${new Date(msg.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="subject">${msg.subject}</div>
                    <div class="preview">${msg.body.substring(0, 100)}${msg.body.length > 100 ? '...' : ''}</div>
                </div>
            `).join('') :
            `<div class="no-messages">No messages in inbox</div>`;
            
    } catch (error) {
        console.error("Inbox loading error:", error);
        if (elements.messageList) {
            elements.messageList.innerHTML = `
                <div class="error-msg">
                    <i class="fas fa-exclamation-triangle"></i> 
                    ${error.message || 'Failed to load inbox'}
                </div>
            `;
        }
        showNotification(error.message || "Error loading inbox", true);
    }
}

// Event handlers
function setupEventListeners() {
    // Navigation
    elements.btnLogout?.addEventListener("click", () => {
        localStorage.clear();
        window.location.href = "/";
    });

    elements.btnInbox?.addEventListener("click", () => {
        window.location.href = "/api/inbox";
    });

    // Refresh button
    elements.refreshInbox?.addEventListener("click", () => {
        showNotification("Refreshing inbox...");
        loadInbox();
    });
}

// Initialize the application
function init() {
    if (!checkAuth()) return;

    // Show user email if available
    const userEmail = localStorage.getItem("email");
    if (elements.userEmail && userEmail) {
        elements.userEmail.textContent = userEmail;
    }

    // Setup all event listeners
    setupEventListeners();

    // Load inbox if on inbox page
    if (window.location.pathname === "/api/inbox") {
        loadInbox();
    }
}

// Debugging - log token status
console.log("Current token:", getToken());
console.log("User email:", localStorage.getItem("email"));

// Start the application when DOM is loaded
document.addEventListener("DOMContentLoaded", init);