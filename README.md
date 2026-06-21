# Smart University Library AI

## 1. Présentation

**Smart University Library AI** est une application web de gestion intelligente d’une bibliothèque universitaire. Le projet permet de gérer les livres, les étudiants, les emprunts, le stock, les utilisateurs et les prévisions de demande des livres.

L’objectif principal est de fournir une plateforme simple pour le bibliothécaire et un espace complet pour l’administrateur.

---

## 2. Fonctionnalités principales

### Authentification

- Connexion sécurisée pour l’administrateur et le bibliothécaire.
- Redirection selon le rôle :
  - administrateur vers l’accueil complet ;
  - bibliothécaire vers le tableau de bord bibliothèque.
- Déconnexion depuis toutes les pages.

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

### Prévisions

- calculer un score de demande pour un livre ;
- utiliser les informations globales et locales ;
- aider à prendre des décisions de stock.

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

### Analyse et prévision

- Pandas
- NumPy
- scikit-learn
- Joblib

---

## 5. Structure du projet

```text
smart-university-library-ai/
├── backend/
│   ├── app.py
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
├── README.md
└── requirements.txt
```

---

## 6. Lancement du projet dans Codespaces

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

## 7. Comptes de test

### Administrateur

```text
Nom d'utilisateur : admin
Mot de passe      : Admin@123
```

### Bibliothécaire

```text
Nom d'utilisateur : biblio
Mot de passe      : Biblio@123
```

---

## 8. Préparation des données

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

## 9. Préparation du modèle de prévision

Pour reconstruire le dataset et entraîner le modèle :

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

Le fichier modèle ne doit pas être poussé sur GitHub s’il est volumineux.

---

## 10. Tests rapides

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

## 11. Scénario de démonstration

1. Se connecter avec le compte administrateur.
2. Montrer la navigation complète.
3. Créer un utilisateur bibliothécaire.
4. Se connecter avec le compte bibliothécaire.
5. Ouvrir la page Livres.
6. Mettre à jour le stock d’un livre.
7. Ouvrir la page Emprunts.
8. Créer un emprunt.
9. Retourner un livre.
10. Ouvrir la page Prévisions et calculer un score.
11. Montrer le tableau de bord bibliothèque.

---

## 12. Points forts du projet

- Interface claire avec navigation dynamique selon le rôle.
- Séparation entre administrateur et bibliothécaire.
- Gestion complète des livres, étudiants, emprunts et stock.
- Mise à jour immédiate des données métier.
- Prévisions de demande pour aider à gérer le stock.
- Projet adapté à une démonstration universitaire.

---

## 13. Améliorations possibles

- Ajouter une recherche avancée par catégorie.
- Ajouter des notifications pour les retards.
- Ajouter un export PDF des rapports.
- Ajouter une page de statistiques mensuelles.
- Ajouter un hébergement cloud complet.

---

## 14. Auteur

Projet réalisé par **ILIAS CHAHBOUN**.
