const API_URL = "http://127.0.0.1:5000";;

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
        const container = document.getElementById(id);
        container.innerHTML = html;

    
        container.querySelectorAll("script").forEach(oldScript => {
            const newScript = document.createElement("script");
            for (const attr of oldScript.attributes) newScript.setAttribute(attr.name, attr.value);
            newScript.textContent = oldScript.textContent;
            oldScript.replaceWith(newScript);
        });
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