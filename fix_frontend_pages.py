from pathlib import Path

frontend = Path("frontend")

="index.html">Accueil</a>dashboard_html = """<!DOCTYPE html>
                <a class="nav-link active" href="dashboard.html">Dashboard</a>
                <a class="nav-link" href="books.html">Livres</a>
                <a class="nav-link" href="students.html">Etudiants</a>
                <a class="nav-link" href="loans.html">Emprunts</a>
                <a class="nav-link" href="bigdata.html">Big Data</a>
            </div>
        </div>
    </nav>

    <div class="container py-4">
        <div class="page-title">Tableau de bord</div>

        <div class="row g-4 mb-4">
            <div class="col-md-6 col-lg-3">
                <div class="card card-stat">
                    <div class="card-body">
                        <div class="text-muted">Total livres</div>
                        <div class="stat-value" id="totalBooks">0</div>
                    </div>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="card card-stat">
                    <div class="card-body">
                        <div class="text-muted">Total etudiants</div>
                        <div class="stat-value" id="totalStudents">0</div>
                    </div>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="card card-stat">
                    <div class="card-body">
                        <div class="text-muted">Total emprunts</div>
                        <div class="stat-value" id="totalLoans">0</div>
                    </div>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="card card-stat">
                    <div class="card-body">
                        <div class="text-muted">Livres disponibles</div>
                        <div class="stat-value" id="availableBooks">0</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row g-4">
            <div class="col-lg-6">
                <div class="table-container">
                    <h4>Top livres</h4>
                    <div id="topBooksContainer" class="loading-text">Chargement...</div>
                </div>
            </div>

            <div class="col-lg-6">
                <div class="table-container">
                    <h4>Top categories</h4>
                    <div id="topCategoriesContainer" class="loading-text">Chargement...</div>
                </div>
            </div>
        </div>

        <div class="row g-4 mt-1">
            <div class="col-lg-12">
                <div class="table-container">
                    <h4>Informations supplementaires</h4>
                    <p><strong>Retards :</strong> <span id="lateLoansCount">0</span></p>
                    <p class="footer-note">Source API : <code>/dashboard/summary</code></p>
                </div>
            </div>
        </div>
    </div>

    <script src="js/api.js"></script>
    <script src="js/dashboard.js"></script>
</body>
</html>
"""

books_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Livres - Smart Library AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="index.html">Smart Library AI</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="index.html">Accueil</a>
                <a class="nav-link" href="dashboard.html">Dashboard</a>
                <a class="nav-link active" href="books.html">Livres</a>
                <a class="nav-link" href="students.html">Etudiants</a>
                <a class="nav-link" href="loans.html">Emprunts</a>
                <a class="nav-link" href="bigdata.html">Big Data</a>
            </div>
        </div>
    </nav>

    <div class="container py-4">
        <div class="page-title">Gestion des livres</div>

        <div class="row g-4">
            <div class="col-lg-4">
                <div class="form-card">
                    <h4>Ajouter un livre</h4>

                    <form id="bookForm">
                        <div class="mb-3">
                            <label class="form-label">Titre</label>
                            <input type="text" class="form-control" id="title" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Auteur</label>
                            <input type="text" class="form-control" id="author">
                        </div>

                        <div class="mb-3">
                            <label class="form-label">ISBN</label>
                            <input type="text" class="form-control" id="isbn">
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Categorie</label>
                            <select class="form-select" id="category_id"></select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Annee de publication</label>
                            <input type="number" class="form-control" id="publication_year">
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Quantite</label>
                            <input type="number" class="form-control" id="quantity" value="1" min="1">
                        </div>

                        <button type="submit" class="btn btn-primary">Ajouter</button>
                    </form>
                </div>
            </div>

            <div class="col-lg-8">
                <div class="table-container">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4>Liste des livres</h4>
                        <button class="btn btn-outline-primary" onclick="loadBooks()">Actualiser</button>
                    </div>

                    <div id="booksTableContainer" class="loading-text">Chargement...</div>
                </div>
            </div>
        </div>
    </div>

    <script src="js/api.js"></script>
    <script src="js/books.js"></script>
</body>
</html>
"""

loans_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emprunts - Smart Library AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="index.html">Smart Library AI</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="index.html">Accueil</a>
                <a class="nav-link" href="dashboard.html">Dashboard</a>
                <a class="nav-link" href="books.html">Livres</a>
                <a class="nav-link" href="students.html">Etudiants</a>
                <a class="nav-link active" href="loans.html">Emprunts</a>
                <a class="nav-link" href="bigdata.html">Big Data</a>
            </div>
        </div>
    </nav>

    <div class="container py-4">
        <div class="page-title">Gestion des emprunts</div>

        <div class="row g-4">
            <div class="col-lg-4">
                <div class="form-card">
                    <h4>Nouvel emprunt</h4>

                    <form id="loanForm">
                        <div class="mb-3">
                            <label class="form-label">Etudiant</label>
                            <select class="form-select" id="student_id"></select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Livre</label>
                            <select class="form-select" id="book_id"></select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Date d'emprunt</label>
                            <input type="date" class="form-control" id="borrow_date">
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Date limite</label>
                            <input type="date" class="form-control" id="due_date">
                        </div>

                        <button type="submit" class="btn btn-primary">Enregistrer l'emprunt</button>
                    </form>
                </div>

                <div class="form-card mt-4">
                    <h4>Emprunts en retard</h4>
                    <button class="btn btn-outline-danger mb-3" onclick="loadLateLoans()">Afficher les retards</button>
                    <div id="lateLoansContainer"></div>
                </div>
            </div>

            <div class="col-lg-8">
                <div class="table-container">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4>Liste des emprunts</h4>
                        <button class="btn btn-outline-primary" onclick="loadLoans()">Actualiser</button>
                    </div>

                    <div id="loansTableContainer" class="loading-text">Chargement...</div>
                </div>
            </div>
        </div>
    </div>

    <script src="js/api.js"></script>
    <script src="js/loans.js"></script>
</body>
</html>
"""

(frontend / "dashboard.html").write_text(dashboard_html, encoding="utf-8")
(frontend / "books.html").write_text(books_html, encoding="utf-8")
(frontend / "loans.html").write_text(loans_html, encoding="utf-8")

print("Pages corrigees : dashboard.html, books.html, loans.html")
