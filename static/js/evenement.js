// evenement.js — compte à rebours + rafraîchissement des places via fetch
document.addEventListener("DOMContentLoaded", () => {
    // --- Compte à rebours ---
    const elDate = document.querySelector(".detail-evenement .date");
    const elCompte = document.getElementById("compte-a-rebours");
    if (elDate && elCompte) {
        const cible = new Date(elDate.dataset.compte.replace(" ", "T")).getTime();
        const maj = () => {
            const diff = cible - Date.now();
            if (diff <= 0) {
                elCompte.textContent = "Événement en cours ou passé";
                return;
            }
            const j = Math.floor(diff / 86400000);
            const h = Math.floor((diff % 86400000) / 3600000);
            const m = Math.floor((diff % 3600000) / 60000);
            const s = Math.floor((diff % 60000) / 1000);
            elCompte.textContent = `⏳ ${j} j ${h} h ${m} min ${s} s`;
        };
        maj();
        setInterval(maj, 1000);
    }

    // --- Rafraîchissement des places restantes via l'API toutes les 15 s ---
    const eventId = window.location.pathname.split("/").pop();
    const tbody = document.getElementById("places-body");
    if (tbody && /^\d+$/.test(eventId)) {
        const rafraichir = () => {
            fetch(`/api/evenements/${eventId}/places`)
                .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
                .then((data) => {
                    data.categories.forEach((c, i) => {
                        const ligne = tbody.rows[i];
                        if (ligne) ligne.querySelector(".restant").textContent = c.restants;
                    });
                })
                .catch((err) => console.warn("Erreur fetch places :", err));
        };
        rafraichir();
        setInterval(rafraichir, 15000);
    }
});