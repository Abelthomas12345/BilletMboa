// controle.js — contrôle d'entrée via fetch POST /api/controle
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-controle");
    const zone = document.getElementById("resultat-controle");
    if (!form || !zone) return;

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const code = form.code.value.trim().toUpperCase();
        if (code.length < 4) {
            zone.innerHTML = `<div class="resultat resultat-inconnu">Code trop court.</div>`;
            return;
        }
        zone.innerHTML = "Vérification…";
        fetch("/api/controle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code }),
        })
            .then((r) => r.json())
            .then((data) => {
                let html = `<div class="resultat resultat-${data.statut}">${data.message}</div>`;
                if (data.billet) {
                    html += `<p><strong>${data.billet.nom_acheteur}</strong> — ${data.billet.categorie_nom} — ${data.billet.evenement_titre}</p>`;
                }
                zone.innerHTML = html;
                form.code.value = "";
                form.code.focus();
            })
            .catch(() => {
                zone.innerHTML = `<div class="resultat resultat-inconnu">Erreur réseau.</div>`;
            });
    });
});