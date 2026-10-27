# BilletMboa — Billetterie de concerts et d'événements

Projet Technologies Web — Flask + SQLite

## Installation

1. Copier le dossier `projet/`.
2. (Optionnel mais recommandé) créer un environnement virtuel :
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Linux / macOS
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Générer la base de test et l'export SQL :
   ```bash
   python donnees_test.py
   ```

## Lancement

```bash
python app.py
```

Ouvrir ensuite http://127.0.0.1:5000

## Comptes de test

| Rôle          | Identifiant | Mot de passe |
|---------------|-------------|--------------|
| Administrateur| `admin`     | `admin123`   |

## Fonctionnalités

### Partie publique
- Agenda des événements à venir, filtrable par ville
- Page d'un événement avec places restantes par catégorie
- Achat de 1 à 5 billets avec génération de codes uniques

### Espace d'administration (connexion)
- Création et publication d'événements
- Ajout de catégories (Standard / VIP) et de quotas
- Contrôle d'entrée : saisie d'un code → réponse valide / déjà utilisé / inconnu
- Statistiques : taux de remplissage, recette, % scannés, arrivées par tranche de 30 min

### API JSON
- `GET /api/evenements/<id>/places` → places restantes par catégorie
- `POST /api/controle` → vérification d'un code (JSON)

## Sécurité

- Mots de passe hachés avec `generate_password_hash`
- Requêtes SQL paramétrées (`?`)
- Validation serveur systématique (quotas, capacités, longueurs, codes)
- Suppressions / modifications uniquement en POST
- Génération des codes via `secrets` (imprévisibles)
- `debug=False` dans `app.run`

## Vérification W3C

Les pages principales (`index`, `evenement`, `achat`, `login`, `404`) sont validables sur
<https://validator.w3.org/>; sans erreur.