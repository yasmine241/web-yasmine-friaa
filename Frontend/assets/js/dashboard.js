let fraudPieChart;

async function loadDashboard() {
    try {
        const data = await getDashboardStats();
        document.getElementById("totalTransactions").innerText = data.total_transactions ?? "—";
        document.getElementById("fraudCount").innerText        = data.fraud_count ?? "—";
        document.getElementById("safeCount").innerText         = data.safe_count ?? "—";
        document.getElementById("rejectedCount").innerText     = data.rejected_transactions ?? "—";
        document.getElementById("pendingAlerts").innerText     = data.pending_alerts ?? "—";
        document.getElementById("fraudRate").innerText         = (data.fraud_rate ?? 0) + "%";
        document.getElementById("fraudAmount").innerText       = Number(data.fraud_amount ?? 0).toLocaleString("fr-FR") + " €";
        document.getElementById("totalAmount").innerText       = Number(data.total_amount ?? 0).toLocaleString("fr-FR") + " €";
        document.getElementById("fraudAlert").style.display   = data.fraud_count > 0 ? "block" : "none";
        renderPieChart(data);
    } catch(err) { console.error("Erreur dashboard:", err); }
}

function renderPieChart(data) {
    const ctx = document.getElementById("fraudPieChart");
    if (!ctx) return;
    if (fraudPieChart) fraudPieChart.destroy();
    fraudPieChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Sûres", "En analyse", "Rejetées"],
            datasets: [{
                data: [data.safe_count, data.fraud_count, data.rejected_transactions],
                backgroundColor: ["#198754","#fd7e14","#dc3545"],
                borderWidth: 2
            }]
        },
        options: { responsive:true, maintainAspectRatio:false, plugins:{ legend:{ position:"bottom" } } }
    });
}

async function loadRecentFrauds() {
    try {
        const frauds = await getPendingFrauds();
        const tbody  = document.getElementById("recentFraudsBody");
        if (!tbody) return;
        if (!frauds || frauds.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">Aucune alerte en attente</td></tr>`;
            return;
        }
        tbody.innerHTML = frauds.slice(0, 8).map(f => `
            <tr>
                <td>#${f.transaction_id}</td>
                <td>${f.type_fraude ?? "—"}</td>
                <td><span class="badge-statut badge-${f.niveau_risque}">${f.niveau_risque}</span></td>
                <td>${(f.score_ml * 100).toFixed(0)}%</td>
                <td>${new Date(f.date_detection).toLocaleString("fr-FR")}</td>
            </tr>
        `).join("");
    } catch(err) { console.error("Erreur fraudes récentes:", err); }
}

document.addEventListener("DOMContentLoaded", async () => {
    requireAuth();
    await loadComponent("navbar",  "../components/navbar.html");
    await loadComponent("sidebar", "../components/sidebar.html");
    await loadComponent("footer",  "../components/footer.html");
    await loadComponent("cookieBanner", "../components/cookie-banner.html");
    loadDashboard();
    loadRecentFrauds();
    setInterval(() => { loadDashboard(); loadRecentFrauds(); }, 10000);
});