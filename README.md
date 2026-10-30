BilletMboa — Plateforme de billetterie événementielle

BilletMboa est une application web de gestion et de réservation de billets pour des concerts et événements. Elle permet aux visiteurs de consulter les événements disponibles, de choisir une catégorie de billet et d'effectuer une réservation. Elle intègre également un espace d'administration destiné à la gestion des événements, des catégories, des ventes et du contrôle des entrées.

---

Présentation

La gestion des réservations et du contrôle d'accès aux événements nécessite un suivi fiable des billets, des capacités d'accueil et des ventes.

BilletMboa propose une solution centralisée permettant de gérer le cycle de vie des billets, depuis la publication d'un événement jusqu'à la validation du billet à l'entrée.

L'application repose sur une architecture web utilisant Flask côté serveur et SQLite pour la persistance des données.

Fonctionnalités

Espace public

- Consultation de l'agenda des événements publiés.
- Filtrage des événements par ville.
- Consultation des détails d'un événement : artiste, date, salle, ville et capacité.
- Affichage des places restantes par catégorie.
- Réservation de 1 à 5 billets par commande.
- Génération d'un code unique pour chaque billet acheté.

Espace d'administration

- Authentification de l'administrateur.
- Tableau de bord de gestion.
- Création et gestion des événements.
- Publication et dépublication des événements.
- Gestion des catégories de billets, des prix et des quotas.
- Contrôle et validation des billets à l'entrée.
- Consultation des statistiques d'exploitation.

Contrôle des billets

Chaque billet possède un code individuel permettant de vérifier sa validité.

Le système distingue notamment :

- Valide : le billet est reconnu et accepté lors du premier contrôle.
- Déjà utilisé : le billet a déjà été scanné.
- Inconnu : aucun billet ne correspond au code fourni.

Statistiques

L'espace d'administration permet de suivre plusieurs indicateurs :

- Taux de remplissage des événements.
- Recettes par événement et par catégorie.
- Pourcentage de billets contrôlés.
- Répartition des arrivées par tranches de 30 minutes.

---

Technologies utilisées

Domaine| Technologies
Backend| Python, Flask
Base de données| SQLite
Frontend| HTML5, CSS3
Interactivité| JavaScript
Communication asynchrone| Fetch API, JSON
Authentification| Sessions Flask
Sécurité des mots de passe| Werkzeug
Versionnement| Git, GitHub

---

Architecture fonctionnelle

L'application s'organise autour de trois espaces principaux :

Espace| Responsabilités
Public| Consultation des événements et réservation
Administration| Gestion des événements, catégories, ventes et statistiques
Contrôle d'accès| Vérification et validation des billets

Modèle de données

La base de données SQLite repose principalement sur les entités suivantes :

- salles : informations sur les lieux accueillant les événements.
- evenements : informations relatives aux concerts et événements.
- categories_billet : catégories, prix et quotas de billets.
- billets : informations sur les réservations, les codes et l'état de contrôle.

Les relations entre les tables et les contraintes d'intégrité sont définies dans "schema.sql".

---

API JSON

L'application expose notamment les routes suivantes :

Méthode| Endpoint| Description
GET| "/api/evenements/<id>/places"| Consultation des places restantes par catégorie
POST| "/api/controle"| Vérification d'un code de billet

Les échanges utilisent le format JSON. Le navigateur communique avec les routes concernées à l'aide de l'API Fetch.

---

Installation et exécution

Prérequis

Avant de commencer, assurez-vous de disposer des éléments suivants :

- Python 3.10 ou supérieur.
- pip.
- Git.
- Un navigateur web récent.

1. Cloner le dépôt

git clone https://github.com/Abelthomas12345/GLO-5-Groupe11.git

2. Accéder au projet

cd GLO-5-Groupe11

3. Créer un environnement virtuel

Windows :

python -m venv venv
venv\Scripts\activate

Linux / macOS :

python3 -m venv venv
source venv/bin/activate

4. Installer les dépendances

pip install -r requirements.txt

5. Initialiser la base de données

Le fichier "schema.sql" contient la structure de la base de données.

Le script "donnees_test.py" permet de préparer les données de démonstration prévues pour le projet.

python donnees_test.py

6. Lancer l'application

python app.py

Ouvrez ensuite votre navigateur à l'adresse :

http://127.0.0.1:5000/

«Note : la commande de lancement suppose que le point d'entrée Flask est "app.py". Si le fichier principal porte un autre nom dans le dépôt, adaptez cette commande.»

---

Sécurité et intégrité des données

Plusieurs mécanismes sont intégrés à l'application :

- Hachage des mots de passe avec Werkzeug.
- Requêtes SQL paramétrées.
- Validation des données côté serveur.
- Génération de codes de billets imprévisibles.
- Protection des routes d'administration par authentification.
- Contraintes d'intégrité dans la base de données.
- Vérification des quotas avant la création des billets.
- Contrôle de l'utilisation unique d'un billet.

Pour un déploiement en production, la clé secrète Flask doit être configurée à l'aide d'une variable d'environnement forte. Les protections CSRF, l'authentification des routes sensibles et la gestion des réservations concurrentes doivent également être vérifiées et renforcées.

---

Interface et compatibilité

BilletMboa dispose d'une interface adaptative conçue pour une utilisation sur ordinateur et téléphone.

Les principales interfaces comprennent :

- L'agenda des événements.
- La fiche détaillée d'un événement.
- Le formulaire de réservation.
- L'affichage des billets générés.
- Le tableau de bord administrateur.
- La gestion des événements et des catégories.
- Les statistiques et le contrôle d'accès.

---

Structure du dépôt

Projet
│
├── app.py
├── requirements.txt
├── schema.sql
├── donnees_test.py
├── README.md
│
├── templates/
│   ├── base.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── ...

---

Contexte du projet

Information| Détail
Projet| Projet 11 — Billetterie de concerts et d'événements
Application| BilletMboa
Filière| Génie Logiciel
Niveau| GLO-5
Module| Technologies Web
Année académique| 2026–2027
Type| Projet académique individuel

---

Évolutions envisageables

- Intégration d'une solution de paiement en ligne.
- Génération de billets au format PDF avec QR code.
- Envoi automatique des confirmations de réservation.
- Gestion avancée des comptes et des rôles.
- Tableau de bord analytique enrichi.
- Déploiement sur une infrastructure cloud.

---

Licence

Projet réalisé dans un cadre académique. Toute réutilisation, modification ou distribution doit respecter les conditions définies par les auteurs du projet.

---

BilletMboa — Simplifier la réservation, maîtriser les accès et valoriser les événements.