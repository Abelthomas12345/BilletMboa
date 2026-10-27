--Schema de base  -Billeterie de concerts et d'évenements
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS billets;
DROP TABLE IF EXISTS categories_billet;
DROP TABLE IF EXISTS evenements;
DROP TABLE IF EXISTS salles;
DROP TABLE IF EXISTS administrateurs;

-- Salles
CREATE TABLE salles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    ville TEXT NOT NULL CHECK (ville IN ('Douala' ,'Yaoundé')),
    capacite INTEGER NOT NULL CHECK (capacite > 0)
);

-- Evénements
CREATE TABLE evenements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL ,
    artiste TEXT NOT NULL,
    salle_id INTEGER NOT NULL,
    date_heure TEXT  NOT NULL,
    affiche TEXT,
    description TEXT,
    publie INTEGER NOT NULL DEFAULT 0 CHECK (publie IN (0, 1)),
    FOREIGN KEY (salle_id) REFERENCES salles(id)
);

-- Categories de billets
CREATE TABLE categories_billet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evenement_id INTEGER NOT NULL ,
    nom TEXT NOT NULL CHECK (nom IN ('Standard','VIP')),
    prix INTEGER NOT NULL CHECK (prix >= 0),
    quota INTEGER  NOT NULL CHECK(quota > 0),
    UNIQUE (evenement_id,nom),
    FOREIGN KEY (evenement_id) REFERENCES evenements(id)
);

--Billets
CREATE TABLE billets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categorie_id INTEGER NOT NULL ,
    nom_acheteur TEXT NOT NULL,
    telephone TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    date_achat TEXT NOT NULL,
    scanne INTEGER NOT NULL DEFAULT 0 CHECK (scanne IN (0, 1)),
    heure_entree TEXT,
    FOREIGN KEY (categorie_id) REFERENCES categories_billet(id)
);

-- Administrateurs (connexion espace admin)
CREATE TABLE administrateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    mot_de_passe_hash  TEXT NOT NULL
);
CREATE INDEX idx_evenements_date ON evenements(date_heure);
CREATE INDEX idx_billets_categoriee ON billets(categorie_id);