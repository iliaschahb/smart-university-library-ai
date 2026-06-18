from pathlib import Path
import re

FRONTEND_DIR = Path("frontend")

PAGES = [
    ("index.html", "Accueil"),
    ("librarian_dashboard.html", "Bibliothécaire"),
    ("dashboard.html", "Dashboard"),
    ("books.html", "Livres"),
    ("students.html", "Étudiants"),
    ("loans.html", "Emprunts"),
    ("bigdata.html", "Big Data"),
    ("ml.html", "IA"),
    ("recommendations.html", "Recommandations"),
    ("visualizations.html", "Visualisations"),
]

CARD_PAGES = [
    ("dashboard.html", "Dashboard", "Consulter les statistiques globales."),
    ("books.html", "Livres", "Gérer le catalogue des livres."),
    ("students.html", "Étudiants", "Gérer les fiches étudiantes."),
    ("loans.html", "Emprunts", "Suivre les emprunts et retours."),
    ("librarian_dashboard.html", "Bibliothécaire", "Suivre la disponibilité, les retards et les alertes de stock."),
    ("bigdata.html", "Big Data", "Afficher les résultats PySpark et les indicateurs analytiques."),
    ("ml.html", "IA", "Prédire la popularité des livres avec le modèle entraîné."),
    ("recommendations.html", "Recommandations", "Afficher les recommandations intelligentes de livres."),
    ("visualizations.html", "Visualisations", "Consulter les graphiques métier et Data Science."),
]


def build_nav(active_file: str) -> str:
    links = []
    for file_name, label in PAGES:
        active = " active" if file_name == active_file else ""
        links.append(f'                <a class="nav-link{active}" href="{file_name}">{label}</a>')

    return """<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="index.html">Smart Library AI</a>
        <div class="navbar-nav ms-auto">
%s
        </div>
    </div>
</nav>""" % "\n".join(links)


def replace_navbar(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    new_nav = build_nav(file_path.name)

    pattern = re.compile(r'<nav class="navbar[\s\S]*?</nav>', re.MULTILINE)
    if pattern.search(content):
        content = pattern.sub(new_nav, content, count=1)
    else:
        content = content.replace("<body>", "<body>\n" + new_nav, 1)

    file_path.write_text(content, encoding="utf-8")


def build_index_cards() -> str:
    cards = []
    for href, title, text in CARD_PAGES:
        cards.append(f"""
            <div class="col-md-6 col-lg-4">
                <div class="card card-stat h-100">
                    <div class="card-body">
                        <h5>{title}</h5>
                        <p>{text}</p>
                        <a href="{href}" class="btn btn-primary">Ouvrir</a>
                    </div>
                </div>
            </div>""")
    return '<div class="row mt-4 g-4">' + "".join(cards) + "\n        </div>"


def update_index_cards():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    new_cards = build_index_cards()

    # Replace the first Bootstrap cards row after hero-box.
    pattern = re.compile(r'<div class="row mt-4 g-4">[\s\S]*?</div>\s*<div class="mt-4 small-muted">', re.MULTILINE)
    replacement = new_cards + "\n\n        <div class=\"mt-4 small-muted\">"

    if pattern.search(content):
        content = pattern.sub(replacement, content, count=1)
    else:
        # Fallback: insert before small-muted.
        content = content.replace('<div class="mt-4 small-muted">', new_cards + '\n\n        <div class="mt-4 small-muted">', 1)

    index_path.write_text(content, encoding="utf-8")


def main():
    if not FRONTEND_DIR.exists():
        raise SystemExit("Dossier frontend introuvable. Lance ce script depuis la racine du projet.")

    for file_name, _ in PAGES:
        file_path = FRONTEND_DIR / file_name
        if file_path.exists():
            replace_navbar(file_path)
            print(f"Navbar mise à jour : {file_path}")
        else:
            print(f"Page absente, ignorée : {file_path}")

    update_index_cards()
    print("Cartes de index.html mises à jour.")
    print("Terminé. Recharge le navigateur avec Ctrl+Shift+R.")


if __name__ == "__main__":
    main()
