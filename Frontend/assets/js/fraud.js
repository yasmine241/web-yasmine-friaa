const STATUT_LABEL = {
    "EN_COURS":     "En cours",
    "CONFIRME":     "Confirmé",
    "FAUX_POSITIF": "Faux positif",
    "RESOLU":       "Résolu"
};

/**
 * CORRECTION : actions disponibles selon le statut de chaque fraude
 */
function renderActions(f) {
    switch (f.statut_analyse) {

        case "EN_COURS":
            return `
                <button class="btn btn-sm btn-danger me-1"
                        onclick="actionFraud(${f.id},'valider')">
                    ✅ Confirmer
                </button>
                <button class="btn btn-sm btn-secondary"
                        onclick="actionFraud(${f.id},'rejeter')">
                    ❌ Faux positif
                </button>
            `;

        case "CONFIRME":
            return `
                <button class="btn btn-sm btn-warning me-1"
                        onclick="actionFraud(${f.id},'bloquer')">
                    🔒 Bloquer compte
                </button>
                <button class="btn btn-sm btn-outline-secondary"
                        onclick="voirDetail(${f.id})">
                    👁 Détails
                </button>
            `;

        case "FAUX_POSITIF":
            return `
                <button class="btn btn-sm btn-outline-primary"
                        onclick="actionFraud(${f.id},'reclassifier')">
                    🔄 Reclassifier
                </button>
            `;

        case "RESOLU":
            return `
                <button class="btn btn-sm btn-outline-secondary"
                        onclick="voirDetail(${f.id})">
                    👁 Détails
                </button>
            `;

        default:
            return "—";
    }
}

/**
 * CORRECTION : normalisation défensive du score_ml
 * Au cas où de vieilles données aberrantes passent encore
 */
function formatScoreML(score) {
    score = parseFloat(score || 0);
    if (score > 1) score = score / 100;   // sécurité données anciennes
    return `${(score * 100).toFixed(0)}%`;
}


async function loadFrauds() {
    try {
        const frauds = await getFrauds();
        const tbody  = document.getElementById("fraudTableBody");
        if (!tbody) return;

        if (!frauds || frauds.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted">Aucune alerte</td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = frauds.map(f => `
            <tr>
                <td>#${f.id}</td>
                <td>#${f.transaction_id}</td>
                <td>${f.type_fraude ?? "—"}</td>
                <td>
                    <span class="badge-statut badge-${f.niveau_risque}">
                        ${f.niveau_risque}
                    </span>
                </td>
                <td>${formatScoreML(f.score_ml)}</td>
                <td>
                    <span class="badge-statut badge-${f.statut_analyse}">
                        ${STATUT_LABEL[f.statut_analyse] ?? f.statut_analyse}
                    </span>
                </td>
                <td>${renderActions(f)}</td>
            </tr>
        `).join("");

    } catch(err) {
        console.error("Erreur fraudes:", err);
    }
}


async function actionFraud(id, action) {
    const commentaire = prompt("Commentaire (optionnel) :");

    try {
        switch (action) {
            case "valider":
                await validerFraud(id, { commentaire });
                showToast("Fraude confirmée ✅", "success");
                break;
            case "rejeter":
                await rejeterFraud(id, { commentaire });
                showToast("Marqué comme faux positif ✅", "success");
                break;
            case "bloquer":
                await bloquerCompte(id, { commentaire });
                showToast("Compte bloqué 🔒", "warning");
                break;
            case "reclassifier":
                await reclassifierFraud(id, { commentaire });
                showToast("Fraude reclassifiée 🔄", "info");
                break;
            default:
                showToast("Action inconnue", "danger");
                return;
        }
        loadFrauds();
    } catch(err) {
        showToast("Erreur : " + err.message, "danger");
    }
}

function voirDetail(id) {
    showToast("Page de détail non implémentée", "info");
}


async function checkFraud() {
    const amount = parseFloat(document.getElementById("amount").value);
    if (!amount || isNaN(amount)) {
        alert("Montant invalide");
        return;
    }

    try {
        const result = await detectFraud({
            montant:          amount,
            pays_origine:     document.getElementById("paysOrigine")?.value     || "France",
            pays_destination: document.getElementById("paysDestination")?.value || "France",
            type_transaction: document.getElementById("typeTransaction")?.value || "VIREMENT"
        });

        const output = document.getElementById("result");

        // CORRECTION : result.score est en 0-1 (cohérent avec le backend corrigé)
        const scoreDisplay = (result.score * 100).toFixed(0);

        output.innerHTML = result.is_fraud
            ? `🚨 FRAUDE DÉTECTÉE — Niveau : ${result.niveau} — Score : ${scoreDisplay}%`
            : `✅ Transaction SÛRE — Score : ${scoreDisplay}%`;

        output.className = `mt-3 alert alert-${result.is_fraud ? "danger" : "success"}`;

    } catch(err) {
        showToast("Erreur serveur", "danger");
    }
}


document.addEventListener("DOMContentLoaded", async () => {
    requireAuth();
    await loadComponent("navbar",  "../components/navbar.html");
    await loadComponent("sidebar", "../components/sidebar.html");
    loadFrauds();
});