// ── fraud.js — Gestion des alertes fraude ────────────────────────────────────

const STATUT_LABEL = {
    "EN_COURS":     "En cours",
    "CONFIRME":     "Confirmée",
    "FAUX_POSITIF": "Faux positif",
    "RESOLU":       "Résolue"
};

/**
 * Normalise le score ML (défense contre anciennes données aberrantes).
 */
function formatScoreML(score) {
    score = parseFloat(score || 0);
    if (score > 1) score = score / 100;
    return `${(score * 100).toFixed(0)}%`;
}

/**
 * Retourne les boutons d'action selon le statut de l'alerte.
 */
function renderActions(f) {
    switch (f.statut_analyse) {

        case "EN_COURS":
            return `
                <button class="btn btn-sm btn-danger me-1 fw-bold"
                        onclick="actionFraud(${f.id},'valider')">
                    ✅ Confirmer
                </button>
                <button class="btn btn-sm btn-secondary me-1"
                        onclick="actionFraud(${f.id},'rejeter')">
                    ❌ Faux positif
                </button>
                <a href="fraud-detail.html?id=${f.id}" class="btn btn-sm btn-outline-secondary">
                    👁 Détails
                </a>
            `;

        case "CONFIRME":
            return `
                <button class="btn btn-sm btn-warning me-1"
                        onclick="actionFraud(${f.id},'bloquer')">
                    🔒 Bloquer compte
                </button>
                <a href="fraud-detail.html?id=${f.id}" class="btn btn-sm btn-outline-secondary">
                    👁 Détails
                </a>
            `;

        case "FAUX_POSITIF":
            return `
                <button class="btn btn-sm btn-outline-primary me-1"
                        onclick="actionFraud(${f.id},'reclassifier')">
                    🔄 Reclassifier
                </button>
                <a href="fraud-detail.html?id=${f.id}" class="btn btn-sm btn-outline-secondary">
                    👁 Détails
                </a>
            `;

        default:
            return `
                <a href="fraud-detail.html?id=${f.id}" class="btn btn-sm btn-outline-secondary">
                    👁 Détails
                </a>
            `;
    }
}

/**
 * Charge et affiche toutes les alertes.
 */
async function loadFrauds() {
    try {
        const frauds = await getFrauds();
        const tbody  = document.getElementById("fraudTableBody");
        if (!tbody) return;

        if (!frauds || frauds.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted py-4">
                        Aucune alerte de fraude enregistrée.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = frauds.map(f => `
            <tr>
                <td><span class="text-muted">#</span>${f.id}</td>
                <td><a href="fraud-detail.html?id=${f.id}" style="color:#e30613; font-weight:600;">#${f.transaction_id}</a></td>
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

    } catch (err) {
        console.error("Erreur fraudes:", err);
        showToast("Impossible de charger les alertes.", "danger");
    }
}

/**
 * Exécute une action sur une alerte fraude.
 */
async function actionFraud(id, action) {
    const commentaire = prompt("Commentaire (optionnel) :");

    try {
        switch (action) {

            case "valider":
                await validerFraud(id, { commentaire });
                showToast("Fraude confirmée — transaction rejetée ✅", "success");
                break;

            case "rejeter":
                await rejeterFraud(id, { commentaire });
                showToast("Marqué comme faux positif ✅", "success");
                break;

            case "bloquer":
                // L'action "bloquer" est gérée via la confirmation de fraude
                // (validerFraud met déjà la transaction en REJETEE)
                showToast("Le compte a été signalé. Contactez un superviseur pour le blocage définitif.", "warning");
                break;

            case "reclassifier":
                // Reclassifier un faux positif → retour EN_COURS via un appel personnalisé
                await authFetch(`/api/fraud/${id}/reclassifier`, {
                    method: "PUT",
                    body: JSON.stringify({ commentaire })
                }).catch(() => {
                    // Endpoint optionnel — si non implémenté, on avertit l'utilisateur
                    showToast("Reclassification : fonctionnalité en cours de déploiement.", "warning");
                    return;
                });
                showToast("Alerte reclassifiée 🔄", "info");
                break;

            default:
                showToast("Action non reconnue.", "danger");
                return;
        }
        await loadFrauds();

    } catch (err) {
        showToast("Erreur : " + err.message, "danger");
    }
}

/**
 * Vérification manuelle d'une transaction.
 */
async function checkFraud() {
    const amountInput = document.getElementById("amount");
    const amount      = parseFloat(amountInput?.value);

    if (!amount || isNaN(amount) || amount <= 0) {
        showToast("Veuillez saisir un montant valide.", "danger");
        return;
    }

    const btn = document.querySelector("[onclick='checkFraud()']");
    if (btn) { btn.disabled = true; btn.textContent = "Analyse en cours…"; }

    try {
        const result = await detectFraud({
            montant:          amount,
            pays_origine:     document.getElementById("paysOrigine")?.value     || "France",
            pays_destination: document.getElementById("paysDestination")?.value || "France",
            type_transaction: document.getElementById("typeTransaction")?.value || "VIREMENT"
        });

        const output       = document.getElementById("result");
        const scoreDisplay = (parseFloat(result.score) * 100).toFixed(0);

        output.innerHTML = result.is_fraud
            ? `<strong>🚨 Fraude probable détectée</strong><br>Niveau : <strong>${result.niveau}</strong> — Score ML : <strong>${scoreDisplay}%</strong>`
            : `<strong>✅ Transaction considérée sûre</strong><br>Score ML : <strong>${scoreDisplay}%</strong>`;

        output.className = `mt-3 alert alert-${result.is_fraud ? "danger" : "success"}`;

    } catch (err) {
        showToast("Erreur lors de l'analyse : " + err.message, "danger");
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = "Analyser"; }
    }
}

// ── Initialisation ────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
    requireAuth();
    await loadComponent("navbar",  "../components/navbar.html");
    await loadComponent("sidebar", "../components/sidebar.html");
    loadFrauds();
});
