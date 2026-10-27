// evenement_form.js — validation client du formulaire de création d'événement
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-evenement");
    if (!form) return;
    form.addEventListener("submit", (e) => {
        const erreurs = [];
        if (form.titre.value.trim().length < 2) erreurs.push("Titre trop court.");
        if (form.artiste.value.trim().length < 2) erreurs.push("Artiste trop court.");
        if (!form.date.value) erreurs.push("Date obligatoire.");
        if (!form.heure.value) erreurs.push("Heure obligatoire.");
        if (erreurs.length) {
            e.preventDefault();
            alert(erreurs.join("\n"));
        }
    });
});