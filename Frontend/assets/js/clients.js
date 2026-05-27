async function loadClients() {
    try {
        const data      = await getClients();
        const container = document.getElementById("clientsList");
        if (!container) return;
        if (!data || data.length === 0) {
            container.innerHTML = `<p class="text-muted">Aucun client trouvé.</p>`;
            return;
        }
        container.innerHTML = data.map(c => `
            <div class="card mb-2 p-3 d-flex flex-row align-items-center justify-content-between">
                <div>
                    <h6 class="mb-0">${c.prenom} ${c.nom}</h6>
                    <small class="text-muted">${c.email} · ${c.pays}</small>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <span class="badge-statut badge-${c.statut}">${c.statut}</span>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteClientUI(${c.id})">🗑</button>
                </div>
            </div>
        `).join("");
    } catch(err) { console.error("Erreur clients:", err); }
}

async function deleteClientUI(id) {
    if (!confirm("Supprimer ce client ?")) return;
    try {
        await deleteClient(id);
        showToast("Client supprimé");
        loadClients();
    } catch(err) { showToast("Erreur : " + err.message, "danger"); }
}

async function submitClient(e) {
    e.preventDefault();
    const data = {
        nom:            document.getElementById("nom").value,
        prenom:         document.getElementById("prenom").value,
        email:          document.getElementById("email").value,
        mot_de_passe:   document.getElementById("motDePasse").value,
        telephone:      document.getElementById("telephone").value,
        date_naissance: document.getElementById("dateNaissance").value,
        adresse:        document.getElementById("adresse").value,
        pays:           document.getElementById("pays").value || "France"
    };
    try {
        await createClient(data);
        showToast("Client créé ✅");
        document.getElementById("clientForm").reset();
        document.getElementById("addClientModal").style.display = "none";
        loadClients();
    } catch(err) { showToast("Erreur : " + err.message, "danger"); }
}

document.addEventListener("DOMContentLoaded", async () => {
    requireAuth();
    await loadComponent("navbar",  "../components/navbar.html");
    await loadComponent("sidebar", "../components/sidebar.html");
    loadClients();
    const form = document.getElementById("clientForm");
    if (form) form.addEventListener("submit", submitClient);
});