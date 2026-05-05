let token = null;
let currentMode = 'login'; // 'login', 'public', 'private'

// ============= INITIALIZATION =============
function init() {
    token = localStorage.getItem("token");
    if (token) {
        showPrivateChat();
    } else {
        showLoginPage();
    }
}

// ============= PAGE NAVIGATION =============
function showLoginPage() {
    currentMode = 'login';
    document.getElementById('login-page').style.display = 'flex';
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('app-container').style.display = 'none';
    document.getElementById('public-chat-container').style.display = 'none';
}

function showPrivateChat() {
    currentMode = 'private';
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('app-container').style.display = 'flex';
    document.getElementById('public-chat-container').style.display = 'none';
}

function startPublicChat() {
    currentMode = 'public';
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('app-container').style.display = 'none';
    document.getElementById('public-chat-container').style.display = 'flex';
}

function goToLogin() {
    document.getElementById('login-modal').style.display = 'flex';
}

function closeLoginModal() {
    document.getElementById('login-modal').style.display = 'none';
}

function closePublicChat() {
    showLoginPage();
}

// ============= AUTHENTICATION =============
async function siaLogin() {
    const status = document.getElementById("sia-login-status");
    status.style.display = "block";
    status.innerHTML = "Membuka browser... Silakan login di jendela yang muncul.";

    try {
        status.innerHTML = "Menunggu login via SIA UTY...";

        const res = await fetch("/auth/sia-login", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        const data = await res.json();
        if (res.ok) {
            token = data.access_token;
            localStorage.setItem("token", token);
            status.innerHTML = "✓ Login berhasil! Mengalihkan...";
            setTimeout(() => {
                closeLoginModal();
                showPrivateChat();
            }, 1500);
        } else {
            throw new Error(data.detail || "Gagal login via SIA");
        }
    } catch (err) {
        status.style.color = "#ef4444";
        status.innerHTML = "❌ Error: " + err.message;
    }
}

async function manualLogin() {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-pass").value;

    if (!email || !password) {
        alert("Email dan password harus diisi");
        return;
    }

    try {
        const res = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();
        if (res.ok) {
            token = data.access_token;
            localStorage.setItem("token", token);
            closeLoginModal();
            showPrivateChat();
        } else {
            alert(data.detail || "Login gagal");
        }
    } catch (err) {
        alert("Error: " + err.message);
    }
}

function logout() {
    token = null;
    localStorage.removeItem("token");
    showLoginPage();
}

// ============= PRIVATE CHAT (Authenticated) =============
async function sendMessage() {
    if (currentMode !== 'private') return;

    const input = document.getElementById("chat-input");
    const msg = input.value.trim();
    if (!msg) return;

    const chatMessages = document.getElementById("chat-messages");

    // Disable input
    input.disabled = true;
    const sendBtn = document.querySelector('.chat-area .btn-send');
    sendBtn.disabled = true;

    // Add user message
    chatMessages.innerHTML += `<div class="message user-msg">${escapeHtml(msg)}</div>`;
    input.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Typing indicator
    const typingId = "typing-" + Date.now();
    chatMessages.innerHTML += `
        <div class="message ai-msg" id="${typingId}">
            <div class="typing-container">
                <div class="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const res = await fetch("/ai/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ message: msg })
        });

        const data = await res.json();
        const typingEl = document.getElementById(typingId);

        if (res.ok) {
            typeWriterEffect(typingEl, data.answer, () => {
                input.disabled = false;
                sendBtn.disabled = false;
                input.focus();
            });
        } else {
            typingEl.innerHTML = "❌ Error: " + (data.detail || "Terjadi kesalahan");
            input.disabled = false;
            sendBtn.disabled = false;
        }
    } catch (err) {
        const typingEl = document.getElementById(typingId);
        typingEl.innerHTML = "❌ Koneksi error: " + err.message;
        input.disabled = false;
        sendBtn.disabled = false;
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ============= PUBLIC CHAT (No Authentication) =============
async function sendPublicMessage() {
    if (currentMode !== 'public') return;

    const input = document.getElementById("public-chat-input");
    const msg = input.value.trim();
    if (!msg) return;

    const chatMessages = document.getElementById("public-chat-messages");

    // Disable input
    input.disabled = true;
    const sendBtn = document.querySelector('.public-chat-container .btn-send');
    sendBtn.disabled = true;

    // Add user message
    chatMessages.innerHTML += `<div class="message user-msg">${escapeHtml(msg)}</div>`;
    input.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Typing indicator
    const typingId = "typing-pub-" + Date.now();
    chatMessages.innerHTML += `
        <div class="message ai-msg" id="${typingId}">
            <div class="typing-container">
                <div class="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const res = await fetch("/ai/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: msg })
        });

        const data = await res.json();
        const typingEl = document.getElementById(typingId);

        if (res.ok) {
            typeWriterEffect(typingEl, data.answer, () => {
                input.disabled = false;
                sendBtn.disabled = false;
                input.focus();
            });
        } else {
            typingEl.innerHTML = "❌ Error: " + (data.detail || "Terjadi kesalahan");
            input.disabled = false;
            sendBtn.disabled = false;
        }
    } catch (err) {
        const typingEl = document.getElementById(typingId);
        typingEl.innerHTML = "❌ Koneksi error: " + err.message;
        input.disabled = false;
        sendBtn.disabled = false;
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ============= UTILITY FUNCTIONS =============
function typeWriterEffect(element, text, callback) {
    element.innerHTML = "";
    let i = 0;
    const speed = 15;

    function type() {
        if (i < text.length) {
            const char = text.charAt(i);
            if (char === '\n') {
                element.innerHTML += '<br>';
            } else {
                element.innerHTML += char;
            }
            i++;
            document.getElementById(element.id).scrollTop = document.getElementById(element.id).scrollHeight;
            setTimeout(type, speed);
        } else {
            if (callback) callback();
        }
    }
    type();
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function syncData() {
    if (!token) return;

    const btn = document.querySelector('.btn-sync');
    btn.disabled = true;
    btn.textContent = "⏳ Syncing...";

    try {
        const res = await fetch("/sync/sync", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        const data = await res.json();
        if (res.ok) {
            alert("✓ Sinkronisasi berhasil!");
        } else {
            alert("Error: " + (data.detail || "Gagal sinkronisasi"));
        }
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = "📊 Sync Data";
    }
}

function clearChat() {
    if (currentMode === 'private') {
        document.getElementById('chat-messages').innerHTML = `
            <div class="message ai-msg">
                <strong>Chat cleared.</strong><br>
                Mulai pertanyaan baru Anda.
            </div>
        `;
    } else if (currentMode === 'public') {
        document.getElementById('public-chat-messages').innerHTML = `
            <div class="message ai-msg">
                <strong>Chat cleared.</strong><br>
                Silakan tanyakan sesuatu!
            </div>
        `;
    }
}

function newPrivateChat() {
    clearChat();
    document.getElementById('chat-input').focus();
}

// Initialize on load
window.addEventListener('load', init);
