# Smart University Library AI

## 1. Présentation

**Smart University Library AI** est une application web de gestion intelligente d’une bibliothèque universitaire. Le projet permet de gérer les livres, les étudiants, les emprunts, le stock, les utilisateurs et les prévisions de demande des livres.

L’objectif principal est de fournir une plateforme simple pour le bibliothécaire et un espace complet pour l’administrateur, tout en intégrant une partie Big Data avec Apache Spark et une partie Intelligence Artificielle pour la prévision de la demande.

---

## 2. Fonctionnalités principales

### Authentification

- Connexion pour l’administrateur et le bibliothécaire.
- Redirection selon le rôle connecté.
- Déconnexion depuis toutes les pages.
- Navigation dynamique selon le profil utilisateur.

### Gestion des utilisateurs

Disponible pour l’administrateur :

- créer un utilisateur ;
- choisir le rôle : administrateur ou bibliothécaire ;
- activer ou désactiver un utilisateur ;
- supprimer un utilisateur.

### Gestion des livres

- consulter le catalogue des livres ;
- rechercher par titre ou auteur ;
- afficher la note et la disponibilité ;
- mettre à jour le stock ;
- définir un emplacement ;
- calculer une prévision de demande pour un livre.

### Gestion des étudiants

- afficher les étudiants ;
- suivre les informations liées aux emprunts.

### Gestion des emprunts

- créer un nouvel emprunt ;
- vérifier automatiquement la disponibilité ;
- afficher la liste des emprunts ;
- retourner un livre ;
- mettre à jour automatiquement le statut et le stock.

### Tableau de bord bibliothèque

- afficher les indicateurs principaux ;
- suivre les emprunts actifs ;
- suivre les retards ;
- visualiser les alertes de stock ;
- afficher les livres les plus empruntés.

### Prévisions IA

- calculer un score de demande pour un livre ;
- utiliser les informations globales et locales ;
- aider à prendre des décisions de stock.

### Big Data avec Apache Spark

- lecture des fichiers Goodbooks-10k ;
- agrégation des ratings et des listes de lecture ;
- génération de features Spark ;
- export de fichiers analytiques dans `data/processed/`.

---

## 3. Rôles de l’application

### Administrateur

L’administrateur peut accéder à :

- Administration ;
- Bibliothèque ;
- Tableau de bord ;
- Livres ;
- Étudiants ;
- Emprunts ;
- Analyses ;
- Prévisions ;
- Suggestions ;
- Graphiques ;
- Catalogue avancé.

### Bibliothécaire

Le bibliothécaire peut accéder à :

- Bibliothèque ;
- Tableau de bord ;
- Livres ;
- Étudiants ;
- Emprunts ;
- Analyses ;
- Prévisions ;
- Suggestions.

Les pages d’administration, graphiques avancés et catalogue avancé sont réservées à l’administrateur.

---

## 4. Technologies utilisées

### Frontend

- HTML
- CSS
- JavaScript
- Bootstrap
- Bootstrap Icons
- Chart.js

### Backend

- Python
- Flask
- Flask-CORS
- SQLAlchemy
- SQLite

### Big Data et Intelligence Artificielle

- Apache Spark / PySpark
- Pandas
- NumPy
- scikit-learn
- Joblib

### DevOps et environnement

- Git
- GitHub
- GitHub Codespaces
- Docker, comme piste d’évolution pour un déploiement reproductible

---

## 5. Structure du projet

```text
smart-university-library-ai/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── models_auth.py
│   ├── models_kaggle_catalog.py
│   ├── routes/
│   ├── services/
│   ├── ml/
│   ├── bigdata/
│   └── seed/
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── admin_panel.html
│   ├── librarian_dashboard.html
│   ├── books.html
│   ├── students.html
│   ├── loans.html
│   ├── dashboard.html
│   ├── bigdata.html
│   ├── ml_hybrid.html
│   ├── recommendations.html
│   ├── css/
│   └── js/
│
├── data/
├── scripts/
├── tests/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 6. Configuration locale

Pour des raisons de sécurité, les identifiants de démonstration et les clés secrètes ne sont pas publiés directement dans le README.

Créer un fichier `.env` à partir du modèle `.env.example` :

```bash
cp .env.example .env
```

Puis modifier les valeurs selon l’environnement local.

Exemple de variables attendues :

```env
SECRET_KEY=change-me
DATABASE_URL=sqlite:///library.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
LIBRARIAN_USERNAME=biblio
LIBRARIAN_PASSWORD=change-me
```

Le fichier `.env` ne doit jamais être poussé sur GitHub.

---

## 7. Base de données

Le projet utilise SQLite pour la démonstration académique. Ce choix facilite l’exécution dans GitHub Codespaces et évite la configuration d’un serveur de base de données externe.

Grâce à SQLAlchemy, une migration future vers PostgreSQL est possible en modifiant principalement la variable `DATABASE_URL`.

Exemple pour PostgreSQL :

```env
DATABASE_URL=postgresql://user:password@localhost:5432/library_ai
```

Pour utiliser PostgreSQL dans une version future, il faudra également installer un driver adapté, par exemple :

```bash
pip install psycopg2-binary
```

---

## 8. Lancement du projet dans Codespaces

### Backend

```bash
cd /workspaces/smart-university-library-ai
source .venv/bin/activate
cd backend
python app.py
```

Le backend doit tourner sur :

```text
http://localhost:5000
```

### Frontend

Dans un deuxième terminal :

```bash
cd /workspaces/smart-university-library-ai/frontend
python -m http.server 5500
```

Puis ouvrir le port 5500 dans le navigateur.

---

## 9. Comptes de démonstration

Les comptes de démonstration ne sont pas publiés directement dans le README pour des raisons de sécurité.

Pour une exécution locale, utiliser le fichier `.env` créé à partir de `.env.example` et définir les identifiants nécessaires.

---

## 10. Préparation des données

Si le catalogue ou la base est vide, lancer :

```bash
cd /workspaces/smart-university-library-ai
source .venv/bin/activate
PYTHONPATH=backend python backend/bigdata/sync_kaggle_catalog_to_db.py
PYTHONPATH=backend python backend/seed/seed_admin_user.py
PYTHONPATH=backend python backend/seed/seed_librarian_user.py
PYTHONPATH=backend python -c "from seed.seed_operational_data import seed; seed(seed_value=42, students_count=300, loans_count=2000, stocked_books=800)"
```

---

## 11. Traitement Big Data avec Apache Spark

Pour générer les features Spark à partir des fichiers Goodbooks-10k :

```bash
cd /workspaces/smart-university-library-ai
source .venv/bin/activate
PYTHONPATH=backend python backend/bigdata/spark_goodbooks_processing.py
```

Fichiers générés :

```text
data/processed/spark_books_features.csv
data/processed/spark_processing_summary.json
```

---

## 12. Préparation du modèle de prévision

Pour reconstruire le dataset analytique et entraîner le modèle :

```bash
cd /workspaces/smart-university-library-ai
source .venv/bin/activate
PYTHONPATH=backend python backend/bigdata/build_hybrid_ai_dataset.py
PYTHONPATH=backend python backend/ml/train_hybrid_demand_model.py
```

Le modèle généré est placé dans :

```text
backend/ml/models/
```

Fichiers principaux :

```text
backend/ml/models/hybrid_demand_model.joblib
backend/ml/models/hybrid_demand_metrics.json
```

---

## 13. Tests rapides

### Vérifier le backend

```bash
curl http://localhost:5000/health
```

### Vérifier le catalogue

```bash
curl http://localhost:5000/catalog/health
```

### Vérifier le modèle

```bash
curl http://localhost:5000/ml/hybrid/health
```

### Tester une prévision

```bash
curl http://localhost:5000/ml/hybrid/predict/2
```

---

## 14. Tests automatisés

Si `pytest` est installé, lancer :

```bash
pytest
```

Un workflow GitHub Actions peut être ajouté dans `.github/workflows/ci.yml` pour exécuter automatiquement les tests à chaque push.

---

## 15. Exécution avec Docker

Le projet peut être préparé pour une exécution avec Docker afin de faciliter le déploiement dans un environnement reproductible.

Exemple :

```bash
docker compose up --build
```

Cette approche permettrait de lancer l’application sans dépendre directement de la configuration de la machine locale.

---

## 16. Scénario de démonstration

- Se connecter avec le compte administrateur.
- Montrer la navigation complète.
- Créer un utilisateur bibliothécaire.
- Se connecter avec le compte bibliothécaire.
- Ouvrir la page Livres.
- Mettre à jour le stock d’un livre.
- Ouvrir la page Emprunts.
- Créer un emprunt.
- Retourner un livre.
- Ouvrir la page Prévisions et calculer un score.
- Montrer le tableau de bord bibliothèque.
- Montrer le traitement Spark et le résumé généré.

---

## 17. Points forts du projet

- Interface claire avec navigation dynamique selon le rôle.
- Séparation entre administrateur et bibliothécaire.
- Gestion complète des livres, étudiants, emprunts et stock.
- Mise à jour immédiate des données métier.
- Pipeline Big Data avec Apache Spark.
- Prévisions de demande avec un modèle IA.
- Projet adapté à une démonstration universitaire.
- Architecture évolutive grâce à SQLAlchemy.

---

## 18. Améliorations possibles

- Ajouter une recherche avancée par catégorie.
- Ajouter des notifications pour les retards.
- Ajouter un export PDF des rapports.
- Ajouter une page de statistiques mensuelles.
- Migrer vers PostgreSQL pour une version production.
- Ajouter davantage de tests automatisés.
- Déployer avec Docker ou sur une plateforme cloud.

---

## 19. Auteur

Projet réalisé par **ILIAS CHAHBOUN**.
