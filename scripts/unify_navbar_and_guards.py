from pathlib import Path
import re

ADMIN_NAV = """<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="index.html">Smart Library AI</a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link" href="index.html">Accueil</a>
            <a class="nav-link" href="admin_panel.html">Administration</a>
            <a class="nav-link" href="librarian_dashboard.html">Bibliothèque</a>
            <a class="nav-link" href="books.html">Livres</a>
            <a class="nav-link" href="students.html">Étudiants</a>
            <a class="nav-link" href="loans.html">Emprunts</a>
            <a class="nav-link" href="dashboard.html">Tableau de bord</a>
            <a class="nav-link" href="bigdata.html">Analyses</a>
            <a class="nav-link" href="ml_hybrid.html">Prévisions</a>
            <a class="nav-link" href="recommendations.html">Suggestions</a>
            <a class="nav-link" href="visualizations.html">Graphiques</a>
            <a class="nav-link" href="catalog_relational.html">Catalogue avancé</a>
            <button class="btn btn-sm btn-outline-light ms-2" onclick="logoutUser()">Déconnexion</button>
        </div>
    </div>
</nav>"""

SHARED_NAV = """<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="index.html">Smart Library AI</a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link" href="index.html">Accueil</a>
            <a class="nav-link" href="librarian_dashboard.html">Bibliothèque</a>
            <a class="nav-link" href="dashboard.html">Tableau de bord</a>
            <a class="nav-link" href="books.html">Livres</a>
            <a class="nav-link" href="students.html">Étudiants</a>
            <a class="nav-link" href="loans.html">Emprunts</a>
            <a class="nav-link" href="bigdata.html">Analyses</a>
            <a class="nav-link" href="ml_hybrid.html">Prévisions</a>
            <a class="nav-link" href="recommendations.html">Suggestions</a>
            <button class="btn btn-sm btn-outline-light ms-2" onclick="logoutUser()">Déconnexion</button>
        </div>
    </div>
</nav>"""

