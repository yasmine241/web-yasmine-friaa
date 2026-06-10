// ── Configuration globale SG SecureBank ──────────────────────────────────────
const API_URL = "http://127.0.0.1:5000";

// ── Auth ──────────────────────────────────────────────────────────────────────
function getToken()      { return localStorage.getItem("token"); }
function setToken(token) { localStorage.setItem("token", token); }
function getUser()       {
    try { return JSON.parse(localStorage.getItem("user") || "{}"); }
    catch { return {}; }
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    // Fonctionne depuis pages/ et depuis la racine
    const base = window.location.pathname.includes("/pages/") ? "../pages/" : "pages/";
    window.location.href = base + "login.html";
}

function requireAuth() {
    if (!getToken()) {
        const base = window.location.pathname.includes("/pages/") ? "" : "pages/";
        window.location.href = base + "login.html";
    }
}

// ── Chargement de composants HTML ─────────────────────────────────────────────
async function loadComponent(id, path) {
    try {
        const res  = await fetch(path);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const html = await res.text();
        const el   = document.getElementById(id);
        if (el) el.innerHTML = html;
    } catch (e) {
        console.warn("Composant introuvable :", path, e.message);
    }
}

// ── Toasts de notification ────────────────────────────────────────────────────
function showToast(message, type = "success") {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    const toast = document.createElement("div");
    toast.className = `alert alert-${type} shadow`;
    toast.style.cssText = "min-width:280px; padding:.7rem 1rem; cursor:pointer;";
    toast.textContent = message;
    toast.addEventListener("click", () => toast.remove());
    container.appendChild(toast);
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 4000);
}

// ── Confirmation modale légère ────────────────────────────────────────────────
function confirmAction(message) {
    return confirm(message);
}
