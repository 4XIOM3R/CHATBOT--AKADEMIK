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

async function siaLogin() {
    const status = document.getElementById("sia-login-status");
    status.style.display = "block";
    status.innerText = "⏳ Membuka browser... Silakan login di jendela yang muncul.";

    try {
        const res = await fetch("/auth/sia-login", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        const data = await res.json();
        if (res.ok) {
            status.innerText = "✅ Login & Sinkronisasi Berhasil!";
            localStorage.setItem("token", data.access_token);
            checkAuth();
        } else {
            throw new Error(data.detail || "Gagal login via SIA");
        }
    } catch (err) {
        status.innerText = "❌ Error: " + err.message;
        status.style.color = "#ef4444";
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

    try {
        // Load IPK
        const resIpk = await fetch("/academic/ipk", { headers });
        const dataIpk = await resIpk.json();
        document.getElementById("val-ipk").innerText = dataIpk.ipk || "0.00";

        // Load KHS
        const resKhs = await fetch("/academic/khs", { headers });
        const dataKhs = await resKhs.json();
        
        const tbodyKhs = document.querySelector("#khs-table tbody");
        tbodyKhs.innerHTML = "";
        let totalSks = 0;
        dataKhs.forEach(item => {
            totalSks += item.sks;
            tbodyKhs.innerHTML += `<tr>
                <td>${item.semester}</td>
                <td>${item.kode}</td>
                <td>${item.mata_kuliah}</td>
                <td>${item.sks}</td>
                <td>${item.nilai}</td>
            </tr>`;
        });
        document.getElementById("val-sks").innerText = totalSks;

        // Load Absen
        const resAbsen = await fetch("/academic/absen", { headers });
        const dataAbsen = await resAbsen.json();
        const tbodyAbsen = document.querySelector("#absen-table tbody");
        tbodyAbsen.innerHTML = "";
        dataAbsen.forEach(item => {
            tbodyAbsen.innerHTML += `<tr>
                <td>${item.mata_kuliah}</td>
                <td>${item.hadir}</td>
                <td>${item.izin}</td>
                <td>${item.alpha}</td>
            </tr>`;
        });

        // Load Pembayaran
        const resPay = await fetch("/academic/pembayaran", { headers });
        const dataPay = await resPay.json();
        const tbodyPay = document.querySelector("#pay-table tbody");
        tbodyPay.innerHTML = "";
        let totalTagihan = 0;
        dataPay.forEach(item => {
            totalTagihan += item.tagihan;
            tbodyPay.innerHTML += `<tr>
                <td>${item.jenis}</td>
                <td>${item.semester}</td>
                <td>Rp ${item.tagihan.toLocaleString('id-ID')}</td>
            </tr>`;
        });

        const payStatus = document.getElementById("val-pay");
        if (totalTagihan > 0) {
            payStatus.innerText = "TAGIHAN: Rp " + totalTagihan.toLocaleString('id-ID');
            payStatus.style.color = "#ef4444";
        } else {
            payStatus.innerText = "LANCAR";
            payStatus.style.color = "#10b981";
        }

    } catch (err) {
        console.error("Gagal memuat dashboard:", err);
    }
}

async function syncData() {
    const btn = document.getElementById("btn-sync");
    const status = document.getElementById("sync-status");
    
    btn.disabled = true;
    status.style.display = "block";
    status.innerText = "⏳ Sedang sinkronisasi... Silakan login di jendela browser yang terbuka.";

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
            status.style.background = "rgba(16, 185, 129, 0.1)";
            status.style.borderColor = "#10b981";
            status.style.color = "#10b981";
            status.innerText = "✅ Sinkronisasi berhasil! Memperbarui data...";
            await loadDashboard();
            setTimeout(() => { status.style.display = "none"; }, 3000);
        } else {
            throw new Error(data.detail || "Gagal sinkronisasi");
        }
    } catch (err) {
        status.style.background = "rgba(239, 68, 68, 0.1)";
        status.style.borderColor = "#ef4444";
        status.style.color = "#ef4444";
        status.innerText = "❌ Error: " + err.message;
    } finally {
        btn.disabled = false;
    }
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
