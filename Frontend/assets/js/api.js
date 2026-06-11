async function authFetch(url, options = {}) {
    const token = getToken();
    const response = await fetch(API_URL + url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "Authorization": token ? `Bearer ${token}` : "",
            ...options.headers
        }
    });
    if (response.status === 401) { logout(); return; }
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.message || "Erreur API");
    }
    return response.json();
}

async function getDashboardStats()      { return authFetch("/api/dashboard"); }
async function getTransactions()        { return authFetch("/api/transactions"); }
async function getClients()             { return authFetch("/api/clients"); }
async function getClient(id)            { return authFetch(`/api/clients/${id}`); }
async function createClient(data)       { return authFetch("/api/clients",    { method:"POST", body:JSON.stringify(data) }); }
async function updateClient(id, data)   { return authFetch(`/api/clients/${id}`, { method:"PUT",  body:JSON.stringify(data) }); }
async function deleteClient(id)         { return authFetch(`/api/clients/${id}`, { method:"DELETE" }); }
async function getComptes()             { return authFetch("/api/comptes"); }
async function getComptesByClient(cid)  { return authFetch(`/api/comptes/client/${cid}`); }
async function createCompte(data)       { return authFetch("/api/comptes",    { method:"POST", body:JSON.stringify(data) }); }
async function getFrauds()              { return authFetch("/api/fraud"); }
async function getPendingFrauds()       { return authFetch("/api/fraud/pending"); }
async function validerFraud(id, data)   { return authFetch(`/api/fraud/${id}/valider`, { method:"PUT", body:JSON.stringify(data) }); }
async function rejeterFraud(id, data)   { return authFetch(`/api/fraud/${id}/rejeter`, { method:"PUT", body:JSON.stringify(data) }); }
async function bloquerCompte(id, data)      { return authFetch(`/api/fraud/${id}/bloquer`,      { method:"PUT", body:JSON.stringify(data) }); }
async function reclassifierFraud(id, data)  { return authFetch(`/api/fraud/${id}/reclassifier`, { method:"PUT", body:JSON.stringify(data) }); }
async function detectFraud(transaction) { return authFetch("/api/fraud/detect", { method:"POST", body:JSON.stringify(transaction) }); }
async function createTransaction(data)  { return authFetch("/api/transactions", { method:"POST", body:JSON.stringify(data) }); }