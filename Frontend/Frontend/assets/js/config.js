const API_URL = "http://127.0.0.1:5000";

function getToken()      { return localStorage.getItem("token"); }
function setToken(token) { localStorage.setItem("token", token); }
function getUser()       { try { return JSON.parse(localStorage.getItem("user") || "{}"); } catch { return {}; } }

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "../pages/login.html";
}

function requireAuth() {
    if (!getToken()) window.location.href = "../pages/login.html";
}

async function loadComponent(id, path) {
    try {
        const res  = await fetch(path);
        const html = await res.text();
        document.getElementById(id).innerHTML = html;
    } catch(e) { console.warn("Composant introuvable :", path); }
}

function showToast(message, type = "success") {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    const toast = document.createElement("div");
    toast.className = `alert alert-${type} shadow`;
    toast.style.minWidth = "260px";
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}