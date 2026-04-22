let isLoginMode = true;

async function login() {
    const email = document.getElementById("login-email").value;
    const pass = document.getElementById("login-pass").value;
    const endpoint = isLoginMode ? "/auth/login" : "/auth/register";

    const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password: pass })
    });

    const data = await res.json();
    if (res.ok) {
        if (isLoginMode) {
            localStorage.setItem("token", data.access_token);
            checkAuth();
        } else {
            alert("Pendaftaran berhasil! Silakan login.");
            toggleAuth();
        }
    } else {
        alert(data.detail || "Terjadi kesalahan");
    }
}

function toggleAuth() {
    isLoginMode = !isLoginMode;
    const title = document.querySelector("#auth-section h1");
    const btn = document.querySelector("#auth-section button");
    const toggleLink = document.querySelector("#auth-section p a");

    if (isLoginMode) {
        title.innerText = "SIA Assistant AI";
        btn.innerText = "Masuk";
        toggleLink.innerText = "Daftar";
    } else {
        title.innerText = "Daftar Akun Baru";
        btn.innerText = "Daftar";
        toggleLink.innerText = "Masuk ke akun";
    }
}


function logout() {
    localStorage.removeItem("token");
    location.reload();
}

function checkAuth() {
    token = localStorage.getItem("token");
    if (token) {
        document.getElementById("auth-section").style.display = "none";
        document.getElementById("dashboard").style.display = "block";
        document.getElementById("chat-toggle").style.display = "flex";
        loadDashboard();
    }
}

async function loadDashboard() {
    const headers = { "Authorization": `Bearer ${token}` };

    // Load IPK
    const resIpk = await fetch("/academic/ipk", { headers });
    const dataIpk = await resIpk.json();
    document.getElementById("val-ipk").innerText = dataIpk.ipk || "0.00";

    // Load KHS
    const resKhs = await fetch("/academic/khs", { headers });
    const dataKhs = await resKhs.json();
    
    const tbody = document.querySelector("#khs-table tbody");
    tbody.innerHTML = "";
    
    let totalSks = 0;
    dataKhs.forEach(item => {
        totalSks += item.sks;
        const tr = `<tr>
            <td>${item.semester}</td>
            <td>${item.kode}</td>
            <td>${item.mata_kuliah}</td>
            <td>${item.sks}</td>
            <td>${item.nilai}</td>
        </tr>`;
        tbody.innerHTML += tr;
    });
    
    document.getElementById("val-sks").innerText = totalSks;
}

function toggleChat() {
    const widget = document.getElementById("chat-widget");
    widget.style.display = widget.style.display === "flex" ? "none" : "flex";
}

async function sendMessage() {
    const input = document.getElementById("chat-msg");
    const msg = input.value.trim();
    if (!msg) return;

    const chatBody = document.getElementById("chat-body");
    
    // Add user message
    chatBody.innerHTML += `<div class="message user-msg">${msg}</div>`;
    input.value = "";
    chatBody.scrollTop = chatBody.scrollHeight;

    // AI thinking state
    const thinkingId = "thinking-" + Date.now();
    chatBody.innerHTML += `<div class="message ai-msg" id="${thinkingId}">...</div>`;
    chatBody.scrollTop = chatBody.scrollHeight;

    const res = await fetch("/ai/chat", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ message: msg })
    });

    const data = await res.json();
    const thinkingEl = document.getElementById(thinkingId);
    if (res.ok) {
        thinkingEl.innerText = data.answer;
    } else {
        thinkingEl.innerText = "Maaf, terjadi kesalahan.";
    }
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Init
checkAuth();
