// main.js — initialisation commune à toutes les pages
document.addEventListener("DOMContentLoaded", () => {
    // Disparition automatique des messages flash
    document.querySelectorAll(".flash").forEach((el) => {
        setTimeout(() => el.remove(), 5000);
    });
});