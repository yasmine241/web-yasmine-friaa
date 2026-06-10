// ── api.js — Couche d'accès à l'API SG SecureBank ────────────────────────────

/**
 * Fetch authentifié. Ajoute le token JWT, gère les erreurs 401/403.
 */
async function authFetch(url, options = {}) {
    const token = getToken();
    const response = await fetch(API_URL + url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "Authorization": token ? `Bearer ${token}` : "",
            ...(options.headers || {})
        }
    });

    if (response.status === 401) {
        showToast("Session expirée. Reconnexion…", "warning");
        setTimeout(logout, 1200);
        return null;
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.message || `Erreur HTTP ${response.status}`);
    }

    // 204 No Content — pas de corps JSON
    if (response.status === 204) return null;

    return response.json();
}

// ── Dashboard ────────────────────────────────────────────────────────────────
async function getDashboardStats()      { return authFetch("/api/dashboard"); }

// ── Transactions ─────────────────────────────────────────────────────────────
async function getTransactions()        { return authFetch("/api/transactions"); }
async function createTransaction(data)  { return authFetch("/api/transactions", { method: "POST", body: JSON.stringify(data) }); }

// ── Clients ──────────────────────────────────────────────────────────────────
async function getClients(params = "")  { return authFetch("/api/clients" + (params ? "?" + params : "")); }
async function getClient(id)            { return authFetch(`/api/clients/${id}`); }
async function createClient(data)       { return authFetch("/api/clients",       { method: "POST",   body: JSON.stringify(data) }); }
async function updateClient(id, data)   { return authFetch(`/api/clients/${id}`, { method: "PUT",    body: JSON.stringify(data) }); }
async function deleteClient(id)         { return authFetch(`/api/clients/${id}`, { method: "DELETE" }); }

// ── Comptes ──────────────────────────────────────────────────────────────────
async function getComptes()             { return authFetch("/api/comptes"); }
async function getComptesByClient(cid)  { return authFetch(`/api/comptes/client/${cid}`); }
async function createCompte(data)       { return authFetch("/api/comptes",       { method: "POST",   body: JSON.stringify(data) }); }
async function updateCompte(id, data)   { return authFetch(`/api/comptes/${id}`, { method: "PUT",    body: JSON.stringify(data) }); }
async function deleteCompte(id)         { return authFetch(`/api/comptes/${id}`, { method: "DELETE" }); }

// ── Fraudes ──────────────────────────────────────────────────────────────────
async function getFrauds()              { return authFetch("/api/fraud"); }
async function getFraud(id)             { return authFetch(`/api/fraud/${id}`); }
async function getPendingFrauds()       { return authFetch("/api/fraud/pending"); }
async function validerFraud(id, data)   { return authFetch(`/api/fraud/${id}/valider`, { method: "PUT", body: JSON.stringify(data) }); }
async function rejeterFraud(id, data)   { return authFetch(`/api/fraud/${id}/rejeter`, { method: "PUT", body: JSON.stringify(data) }); }
async function detectFraud(transaction) { return authFetch("/api/fraud/detect", { method: "POST", body: JSON.stringify(transaction) }); }
