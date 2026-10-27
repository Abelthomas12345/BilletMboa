# app.py — Application Flask de billetterie de concerts et d'événements
import os
import sqlite3
import secrets
from datetime import datetime
from functools import wraps

from flask import (Flask, g, render_template, request, redirect,
                   url_for, flash, session, jsonify, abort)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "projet.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-billetmboa-change-me"
)
app.config["DATABASE"] = DATABASE


## Utilitaires base de données
def get_db():
    """Ouvre une connexion SQLite par requête."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        print("connexion a la bd reussi")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_required(f):
    """Décorateur : protège une route admin."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Veuillez vous connecter pour accéder à l'administration.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


## Partie publique
@app.route("/")
def index():
    db = get_db()
    ville = request.args.get("ville", "").strip()
    sql = """
        SELECT e.*, s.nom AS salle_nom, s.ville AS salle_ville,
               s.capacite AS salle_capacite
        FROM evenements e
        JOIN salles s ON s.id = e.salle_id
        WHERE e.publie = 1
          AND e.date_heure >= datetime('now', 'localtime')
    """
    params = []
    if ville:
        sql += " AND s.ville = ?"
        params.append(ville)
    sql += " ORDER BY e.date_heure ASC"
    evenements = db.execute(sql, params).fetchall()
    return render_template("index.html", evenements=evenements,
                           villes=["Douala", "Yaoundé"], ville=ville)


@app.route("/evenement/<int:event_id>")
def evenement(event_id):
    db = get_db()
    ev = db.execute(
        """SELECT e.*, s.nom AS salle_nom, s.ville AS salle_ville,
                  s.capacite AS salle_capacite
           FROM evenements e JOIN salles s ON s.id = e.salle_id
           WHERE e.id = ? AND e.publie = 1""",
        (event_id,),
    ).fetchone()
    if ev is None:
        abort(404)
    cats = db.execute(
        """SELECT c.*,
                  (SELECT COUNT(*) FROM billets b WHERE b.categorie_id = c.id) AS vendus
           FROM categories_billet c
           WHERE c.evenement_id = ?
           ORDER BY c.prix ASC""",
        (event_id,),
    ).fetchall()
    return render_template("evenement.html", ev=ev, cats=cats)


@app.route("/evenement/<int:event_id>/achat", methods=["GET", "POST"])
def achat(event_id):
    db = get_db()
    ev = db.execute(
        "SELECT * FROM evenements WHERE id = ? AND publie = 1", (event_id,)
    ).fetchone()
    if ev is None:
        abort(404)
    cats = db.execute(
        """SELECT c.*,
                  (SELECT COUNT(*) FROM billets b WHERE b.categorie_id = c.id) AS vendus
           FROM categories_billet c
           WHERE c.evenement_id = ?
           ORDER BY c.prix ASC""",
        (event_id,),
    ).fetchall()

    erreurs = []
    if request.method == "POST":
        categorie_id = request.form.get("categorie_id", type=int)
        nom = request.form.get("nom", "").strip()
        telephone = request.form.get("telephone", "").strip()
        quantite = request.form.get("quantite", type=int)

        # Validation serveur
        cat = None
        if categorie_id:
            cat = db.execute(
                "SELECT * FROM categories_billet WHERE id = ? AND evenement_id = ?",
                (categorie_id, event_id),
            ).fetchone()
        if cat is None:
            erreurs.append("Catégorie invalide.")
        if len(nom) < 2:
            erreurs.append("Le nom doit contenir au moins 2 caractères.")
        if len(telephone) < 8:
            erreurs.append("Le numéro de téléphone est invalide.")
        if quantite is None or not (1 <= quantite <= 5):
            erreurs.append("La quantité doit être entre 1 et 5.")

        if not erreurs and cat is not None:
            vendus = db.execute(
                "SELECT COUNT(*) FROM billets WHERE categorie_id = ?", (cat["id"],)
            ).fetchone()[0]
            restants = cat["quota"] - vendus
            if quantite > restants:
                erreurs.append(
                    f"Il ne reste que {restants} billet(s) dans cette catégorie."
                )

        if not erreurs:
            codes_gen = []
            for _ in range(quantite):
                code = secrets.token_hex(8).upper()  # 16 caractères imprévisibles
                db.execute(
                    """INSERT INTO billets
                       (categorie_id, nom_acheteur, telephone, code, date_achat, scanne)
                       VALUES (?, ?, ?, ?, ?, 0)""",
                    (cat["id"], nom, telephone, code,
                     datetime.now().isoformat(timespec="seconds")),
                )
                codes_gen.append(code)
            db.commit()
            flash(f"{quantite} billet(s) acheté(s) avec succès !", "success")
            return render_template("billets.html", ev=ev, cat=cat,
                                   codes=codes_gen, nom=nom)

    return render_template("achat.html", ev=ev, cats=cats, erreurs=erreurs)


## Authentification admin
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_val = request.form.get("login", "").strip()
        mdp = request.form.get("mot_de_passe", "")
        db = get_db()
        admin = db.execute(
            "SELECT * FROM administrateurs WHERE login = ?", (login_val,)
        ).fetchone()
        if admin and check_password_hash(admin["mot_de_passe_hash"], mdp):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_login"] = admin["login"]
            flash("Connexion réussie.", "success")
            # Redirection sûre (anti open-redirect)
            cible = request.args.get("next", "")
            if not cible.startswith("/") or cible.startswith("//"):
                cible = url_for("admin_dashboard")
            return redirect(cible)
        flash("Identifiants invalides.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("index"))


## Espace d'administration
@app.route("/admin")
@login_required
def admin_dashboard():
    db = get_db()
    nb_ev = db.execute("SELECT COUNT(*) FROM evenements").fetchone()[0]
    nb_billets = db.execute("SELECT COUNT(*) FROM billets").fetchone()[0]
    nb_scannes = db.execute(
        "SELECT COUNT(*) FROM billets WHERE scanne = 1"
    ).fetchone()[0]
    return render_template("admin/dashboard.html",
                           nb_ev=nb_ev, nb_billets=nb_billets,
                           nb_scannes=nb_scannes)


@app.route("/admin/evenements")
@login_required
def admin_evenements():
    db = get_db()
    evs = db.execute(
        """SELECT e.*, s.nom AS salle_nom, s.ville AS salle_ville
           FROM evenements e JOIN salles s ON s.id = e.salle_id
           ORDER BY e.date_heure DESC"""
    ).fetchall()
    return render_template("admin/evenements.html", evenements=evs)


@app.route("/admin/evenements/nouveau", methods=["GET", "POST"])
@login_required
def admin_evenement_nouveau():
    db = get_db()
    salles = db.execute("SELECT * FROM salles ORDER BY nom").fetchall()
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        artiste = request.form.get("artiste", "").strip()
        salle_id = request.form.get("salle_id", type=int)
        date = request.form.get("date", "").strip()
        heure = request.form.get("heure", "").strip()
        description = request.form.get("description", "").strip()
        publie = 1 if request.form.get("publie") else 0

        erreurs = []
        if len(titre) < 2:
            erreurs.append("Titre trop court.")
        if len(artiste) < 2:
            erreurs.append("Artiste trop court.")
        if not salle_id or not db.execute(
            "SELECT 1 FROM salles WHERE id = ?", (salle_id,)
        ).fetchone():
            erreurs.append("Salle invalide.")
        if not date or not heure:
            erreurs.append("Date et heure obligatoires.")

        for e in erreurs:
            flash(e, "danger")

        if not erreurs:
            db.execute(
                """INSERT INTO evenements
                   (titre, artiste, salle_id, date_heure, affiche, description, publie)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (titre, artiste, salle_id, f"{date} {heure}:00",
                 None, description, publie),
            )
            db.commit()
            flash("Événement créé.", "success")
            return redirect(url_for("admin_evenements"))
    return render_template("admin/evenement_form.html", salles=salles)


@app.route("/admin/evenement/<int:event_id>/publier", methods=["POST"])
@login_required
def admin_publier(event_id):
    db = get_db()
    ev = db.execute(
        "SELECT publie FROM evenements WHERE id = ?", (event_id,)
    ).fetchone()
    if ev is None:
        abort(404)
    nouveau = 0 if ev["publie"] else 1
    db.execute("UPDATE evenements SET publie = ? WHERE id = ?",
               (nouveau, event_id))
    db.commit()
    flash("Statut de publication modifié.", "success")
    return redirect(url_for("admin_evenements"))


@app.route("/admin/evenement/<int:event_id>/categories", methods=["GET", "POST"])
@login_required
def admin_categories(event_id):
    db = get_db()
    ev = db.execute(
        """SELECT e.*, s.capacite AS salle_capacite
           FROM evenements e JOIN salles s ON s.id = e.salle_id
           WHERE e.id = ?""",
        (event_id,),
    ).fetchone()
    if ev is None:
        abort(404)

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prix = request.form.get("prix", type=int)
        quota = request.form.get("quota", type=int)

        erreurs = []
        if nom not in ("Standard", "VIP"):
            erreurs.append("Nom de catégorie invalide.")
        if prix is None or prix < 0:
            erreurs.append("Prix invalide.")
        if quota is None or quota <= 0:
            erreurs.append("Quota invalide.")

        if not erreurs:
            deja = db.execute(
                "SELECT 1 FROM categories_billet WHERE evenement_id = ? AND nom = ?",
                (event_id, nom),
            ).fetchone()
            if deja:
                erreurs.append(f"La catégorie {nom} existe déjà.")
            total = db.execute(
                "SELECT COALESCE(SUM(quota), 0) FROM categories_billet WHERE evenement_id = ?",
                (event_id,),
            ).fetchone()[0]
            if total + quota > ev["salle_capacite"]:
                erreurs.append(
                    f"Quota total ({total + quota}) dépasse la capacité "
                    f"de la salle ({ev['salle_capacite']})."
                )

        if erreurs:
            for e in erreurs:
                flash(e, "danger")
        else:
            db.execute(
                "INSERT INTO categories_billet (evenement_id, nom, prix, quota) VALUES (?, ?, ?, ?)",
                (event_id, nom, prix, quota),
            )
            db.commit()
            flash("Catégorie ajoutée.", "success")
            return redirect(url_for("admin_categories", event_id=event_id))

    cats = db.execute(
        """SELECT c.*,
                  (SELECT COUNT(*) FROM billets b WHERE b.categorie_id = c.id) AS vendus
           FROM categories_billet c WHERE c.evenement_id = ?
           ORDER BY c.prix ASC""",
        (event_id,),
    ).fetchall()
    total_quotas = sum(c["quota"] for c in cats)
    return render_template("admin/categories.html", ev=ev, cats=cats,
                           total_quotas=total_quotas)


@app.route("/admin/controle", methods=["GET", "POST"])
@login_required
def admin_controle():
    """Contrôle d'entrée : version sans JavaScript (fallback)."""
    resultat = None
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        resultat = _verifier_code(code)
    return render_template("admin/controle.html", resultat=resultat)


def _verifier_code(code):
    """Fonction utilitaire commune aux routes HTML et JSON."""
    db = get_db()
    billet = db.execute(
        """SELECT b.*, c.nom AS categorie_nom, e.titre AS evenement_titre
           FROM billets b
           JOIN categories_billet c ON c.id = b.categorie_id
           JOIN evenements e ON e.id = c.evenement_id
           WHERE b.code = ?""",
        (code,),
    ).fetchone()
    if billet is None:
        return {"statut": "inconnu", "message": "Code inconnu."}
    if billet["scanne"]:
        return {"statut": "deja_utilise",
                "message": f"Billet déjà utilisé à {billet['heure_entree']}.",
                "billet": dict(billet)}
    maintenant = datetime.now().isoformat(timespec="seconds")
    db.execute(
        "UPDATE billets SET scanne = 1, heure_entree = ? WHERE id = ?",
        (maintenant, billet["id"]),
    )
    db.commit()
    return {"statut": "valide",
            "message": "Billet valide. Entrée autorisée.",
            "billet": dict(billet)}


@app.route("/admin/stats")
@login_required
def admin_stats():
    db = get_db()
    remplissage = db.execute(
        """SELECT e.id, e.titre, s.capacite,
                  (SELECT COALESCE(SUM(quota), 0) FROM categories_billet c
                   WHERE c.evenement_id = e.id) AS total_quota,
                  (SELECT COUNT(*) FROM billets b
                   JOIN categories_billet c ON c.id = b.categorie_id
                   WHERE c.evenement_id = e.id) AS vendus
           FROM evenements e JOIN salles s ON s.id = e.salle_id
           WHERE e.publie = 1
           ORDER BY e.date_heure DESC"""
    ).fetchall()

    recette = db.execute(
        """SELECT e.titre, c.nom AS categorie_nom, c.prix,
                  COUNT(b.id) AS vendus,
                  COUNT(b.id) * c.prix AS recette
           FROM evenements e
           JOIN categories_billet c ON c.evenement_id = e.id
           LEFT JOIN billets b ON b.categorie_id = c.id
           GROUP BY c.id
           ORDER BY e.titre, c.nom"""
    ).fetchall()

    total = db.execute("SELECT COUNT(*) FROM billets").fetchone()[0]
    scannes = db.execute(
        "SELECT COUNT(*) FROM billets WHERE scanne = 1"
    ).fetchone()[0]
    pct_scannes = round(scannes * 100 / total, 1) if total else 0

    arrivees = db.execute(
        """SELECT
              strftime('%H', heure_entree) || ':' ||
              CASE WHEN CAST(strftime('%M', heure_entree) AS INTEGER) < 30
                   THEN '00' ELSE '30' END AS tranche,
              COUNT(*) AS nb
           FROM billets
           WHERE scanne = 1 AND heure_entree IS NOT NULL
           GROUP BY tranche
           ORDER BY tranche"""
    ).fetchall()

    return render_template("admin/stats.html",
                           remplissage=remplissage, recette=recette,
                           pct_scannes=pct_scannes,
                           scannes=scannes, total=total, arrivees=arrivees)


## API JSON
@app.route("/api/evenements/<int:event_id>/places")
def api_places(event_id):
    """Renvoie les places restantes par catégorie (GET)."""
    db = get_db()
    if not db.execute(
        "SELECT 1 FROM evenements WHERE id = ? AND publie = 1", (event_id,)
    ).fetchone():
        return jsonify({"erreur": "Événement introuvable"}), 404
    cats = db.execute(
        """SELECT c.id, c.nom, c.prix, c.quota,
                  (SELECT COUNT(*) FROM billets b WHERE b.categorie_id = c.id) AS vendus,
                  (c.quota - (SELECT COUNT(*) FROM billets b
                              WHERE b.categorie_id = c.id)) AS restants
           FROM categories_billet c
           WHERE c.evenement_id = ?
           ORDER BY c.prix ASC""",
        (event_id,),
    ).fetchall()
    return jsonify({
        "evenement_id": event_id,
        "categories": [dict(c) for c in cats],
    })


@app.route("/api/controle", methods=["POST"])
@login_required
def api_controle():
    """Contrôle d'entrée via fetch (POST JSON)."""
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip().upper()
    if len(code) < 4:
        return jsonify({"statut": "erreur", "message": "Code invalide."}), 400
    return jsonify(_verifier_code(code))


## Erreur 404 personnalisée
@app.errorhandler(404)
def page_introuvable(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)