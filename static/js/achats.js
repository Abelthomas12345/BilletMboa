// achat.js — validation côté client du formulaire d'achat
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-achat");
    if (!form) return;

    form.addEventListener("submit", (e) => {
        const nom = form.nom.value.trim();
        const tel = form.telephone.value.trim();
        const qte = parseInt(form.quantite.value, 10);
        const option = form.categorie_id.options[form.categorie_id.selectedIndex];
        const restants = parseInt(option.dataset.restants, 10);

        const erreurs = [];
        if (nom.length < 2) erreurs.push("Le nom doit contenir au moins 2 caractères.");
        if (tel.length < 8) erreurs.push("Le téléphone doit contenir au moins 8 caractères.");
        if (isNaN(qte) || qte < 1 || qte > 5) erreurs.push("Quantité entre 1 et 5.");
        if (!isNaN(restants) && qte > restants)
            erreurs.push(`Il ne reste que ${restants} billet(s) dans cette catégorie.`);

        if (erreurs.length) {
            e.preventDefault();
            alert(erreurs.join("\n"));
        }
    });
});