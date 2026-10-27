# donnees_test.py
# creer la base a partir de schema.sql puis remplir avec les donnees de test realistes.

import os,random,sqlite3,secrets
from datetime import datetime,timedelta
from werkzeug.security import generate_password_hash

BASE_DIR =os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"projet.db")
SCHEMA_PATH = os.path.join(BASE_DIR,"schema.sql")

random.seed(42)

SALLES = [
    ("Palais des Sports", "Yaoundé", 8000),
    ("Salle des Fêtes de Douala", "Douala", 3500),
    ("Théâtre de Verdure", "Douala", 2000),
    ("Institut Français", "Yaoundé", 1200),
    ("Canal Olympia", "Douala", 5000),
    ("Centre Culturel", "Yaoundé", 1500),
]

TITRES = [
    "Nuit Afrobeat", "Comedy Club Live", "Jazz sous les étoiles",
    "Concert Gospel", "Rire à Douala", "Mbalax Night", "Slam & Poésie",
    "Electric Party", "Symphonie Urbaine", "Karaoké Géant", "Magie & Illusion",
    "Rock Camerounais", "Soirée Rumba", "Festival Hip-Hop", "Ciné-Concert",
]
ARTISTES = [
    "Les Merveilles", "K-Tino & Co", "Jazz Trio", "Chorale Espérance",
    "Boby & Fils", "Sahel Band", "Slam Azur", "DJ Nova", "Orchestre de Douala",
    "Les Voix d'Or", "Magic Show", "Rock Mboa", "Wenge Acoustic",
    "MC Yaoundé", "Ciné Confluence",
]
NOMS = ["Mbarga", "Ngo Bassa", "Fotso", "Atangana", "Njoya",
        "Ekane", "Tchoupo", "Bello", "Abena", "Manga"]
PRENOMS = ["Aline", "Paul", "Kevin", "Marie", "Ibrahim",
           "Sandra", "Rose", "Moussa", "Estelle", "Yannick"]


def creer_base():
    """Supprime l'ancienne base et applique schema.sql."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    return conn


def remplir(conn):
    cur = conn.cursor()

    # --- Salles ---
    for nom, ville, cap in SALLES:
        cur.execute(
            "INSERT INTO salles (nom, ville, capacite) VALUES (?, ?, ?)",
            (nom, ville, cap),
        )

    # --- Compte administrateur (mot de passe haché) ---
    cur.execute(
        "INSERT INTO administrateurs (login, mot_de_passe_hash) VALUES (?, ?)",
        ("admin", generate_password_hash("admin123")),
    )

    # --- Événements (5 passés, 10 futurs) ---
    base = datetime.now()
    for i, (titre, artiste) in enumerate(zip(TITRES, ARTISTES)):
        salle_id = (i % len(SALLES)) + 1
        if i < 5:
            dt = base - timedelta(days=random.randint(5, 30))
        else:
            dt = base + timedelta(days=random.randint(5, 60),
                                  hours=random.randint(18, 22))
        publie = 1 if i < 13 else 0
        cur.execute(
            """INSERT INTO evenements
               (titre, artiste, salle_id, date_heure, affiche, description, publie)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (titre, artiste, salle_id, dt.strftime("%Y-%m-%d %H:%M:00"),
             None, f"{titre} avec {artiste}.", publie),
        )

    # --- Catégories : Standard 70 %, VIP 20 % de la capacité ---
    for ev_id in range(1, 16):
        capacite = SALLES[(ev_id - 1) % len(SALLES)][2]
        cur.execute(
            "INSERT INTO categories_billet (evenement_id, nom, prix, quota) VALUES (?,?,?,?)",
            (ev_id, "Standard", 5000, int(capacite * 0.7)),
        )
        cur.execute(
            "INSERT INTO categories_billet (evenement_id, nom, prix, quota) VALUES (?,?,?,?)",
            (ev_id, "VIP", 15000, int(capacite * 0.2)),
        )

    # --- 800 billets ---
    categories = cur.execute(
        "SELECT id, quota FROM categories_billet"
    ).fetchall()
    codes = set()
    total = 0
    while total < 800:
        cat_id, quota = random.choice(categories)
        vendus = cur.execute(
            "SELECT COUNT(*) FROM billets WHERE categorie_id = ?", (cat_id,)
        ).fetchone()[0]
        if vendus >= quota:
            continue
        code = secrets.token_hex(8).upper()
        if code in codes:
            continue
        codes.add(code)
        nom = f"{random.choice(PRENOMS)} {random.choice(NOMS)}"
        tel = f"+2376{random.randint(10000000, 99999999)}"
        date_achat = (datetime.now() - timedelta(days=random.randint(0, 15))
                     ).isoformat(timespec="seconds")
        scanne = 1 if random.random() < 0.4 else 0
        heure_entree = None
        if scanne:
            heure_entree = (datetime.now() - timedelta(hours=random.randint(0, 5))
                           ).isoformat(timespec="seconds")
        cur.execute(
            """INSERT INTO billets
               (categorie_id, nom_acheteur, telephone, code, date_achat, scanne, heure_entree)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (cat_id, nom, tel, code, date_achat, scanne, heure_entree),
        )
        total += 1

    conn.commit()


def export_sql(conn):
    """Exporte toute la base dans export_projet.sql."""
    with open(os.path.join(BASE_DIR, "export_projet.sql"), "w", encoding="utf-8") as f:
        for ligne in conn.iterdump():
            f.write(ligne + "\n")


if __name__ == "__main__":
    conn = creer_base()
    remplir(conn)
    export_sql(conn)
    conn.close()
    print(f"Base créée : {DB_PATH}")
    print(f"Export SQL : {os.path.join(BASE_DIR, 'export_projet.sql')}")