/**
 * CORRECTION : score_risque est toujours reçu entre 0 et 1 depuis l'API.
 * On multiplie par 100 pour afficher en %.
 */
function formatRisk(score) {
    score = Number(score || 0);

    // Sécurité : si une vieille valeur aberrante passe quand même
    if (score > 1) score = score / 100;

    // Clamp final entre 0 et 100%
    score = Math.min(Math.max(score * 100, 0), 100);

    return `${score.toFixed(1)}%`;
}


async function loadTransactions() {
    try {
        const data  = await getTransactions();
        const tbody = document.getElementById("transactionsTable");

        if (!tbody) return;

        if (!data || data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted">
                        Aucune transaction.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.map(tx => `
            <tr>
                <td>#${tx.id}</td>

                <td>
                    ${tx.type ?? "—"}
                </td>

                <td>
                    ${Number(tx.montant).toLocaleString("fr-FR")} ${tx.devise}
                </td>

                <td>
                    ${tx.pays_origine ?? "—"} → ${tx.pays_destination ?? "—"}
                </td>

                <td>
                    ${new Date(tx.date_transaction).toLocaleString("fr-FR")}
                </td>

                <td>
                    ${formatRisk(tx.score_risque)}
                </td>

                <td>
                    <span class="badge-statut badge-${tx.statut}">
                        ${tx.statut}
                    </span>
                </td>
            </tr>
        `).join("");

    } catch(err) {
        console.error("Erreur transactions:", err);
    }
}


async function submitTransaction(e) {
    e.preventDefault();

    const btn = document.getElementById("submitTxBtn");
    btn.disabled = true;

    const data = {
        compte_id: parseInt(document.getElementById("compteId").value),

        type_transaction:
            document.getElementById("typeTx").value,

        montant:
            parseFloat(document.getElementById("montant").value),

        devise:
            document.getElementById("devise").value || "EUR",

        pays_origine:
            document.getElementById("paysO").value,

        pays_destination:
            document.getElementById("paysD").value
    };

    try {
        const res = await createTransaction(data);

        // CORRECTION : res.score_risque est en 0-1, formatRisk gère l'affichage
        showToast(
            res.fraud
                ? `⚠️ Fraude possible — score ${formatRisk(res.score_risque)}`
                : `✅ Transaction validée — score ${formatRisk(res.score_risque)}`,
            res.fraud ? "warning" : "success"
        );

        document.getElementById("txForm").reset();
        loadTransactions();

    } catch(err) {
        showToast("Erreur : " + err.message, "danger");

    } finally {
        btn.disabled = false;
    }
}


document.addEventListener("DOMContentLoaded", async () => {

    requireAuth();

    await loadComponent("navbar",   "../components/navbar.html");
    await loadComponent("sidebar",  "../components/sidebar.html");

    loadTransactions();

    const form = document.getElementById("txForm");
    if (form) {
        form.addEventListener("submit", submitTransaction);
    }
});