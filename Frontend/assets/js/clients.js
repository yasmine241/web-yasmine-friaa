async function loadClients() {
    try {
        const response  = await getClients();
        const data      = response?.items ?? response; // backend paginé : {items:[...]}
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
                    <span class="text-muted small">#${c.id}</span>
                </div>
            </div>
        `).join("");
    } catch (err) {
        console.error("Erreur clients:", err);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    requireAuth();
    await loadComponent("navbar",  "../components/navbar.html");
    await loadComponent("sidebar", "../components/sidebar.html");
    await loadComponent("footer",  "../components/footer.html");
    await loadComponent("cookieBanner", "../components/cookie-banner.html");
    loadClients();
});