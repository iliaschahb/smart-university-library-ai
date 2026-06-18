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
    ("ml_hybrid.html", "IA Hybride"),
    ("recommendations.html", "Recommandations"),
    ("visualizations.html", "Visualisations"),
    ("catalog_relational.html", "Catalogue Kaggle"),
]

INDEX_CARDS = [
    ("dashboard.html", "Dashboard", "Consulter la synthèse relationnelle de la plateforme."),
    ("books.html", "Livres", "Explorer le catalogue Kaggle relationnel et le stock local."),
    ("students.html", "Étudiants", "Afficher les étudiants relationnels locaux et leurs emprunts."),
    ("loans.html", "Emprunts", "Suivre les emprunts, les retours et les retards."),
    ("librarian_dashboard.html", "Bibliothécaire", "Surveiller les indicateurs métier et les alertes de stock."),
    ("bigdata.html", "Big Data", "Voir les résultats analytiques issus du pipeline PySpark."),
    ("ml_hybrid.html", "IA Hybride", "Prédire la demande locale d'un livre avec le modèle hybride."),
    ("recommendations.html", "Recommandations", "Afficher les recommandations intelligentes de livres."),
    ("visualizations.html", "Visualisations", "Consulter les graphiques métier et Data Science."),
    ("catalog_relational.html", "Catalogue Kaggle", "Consulter le catalogue relationnel basé sur Kaggle."),
]


def build_nav(active_file: str) -> str:
    links = []
    for file_name, label in PAGES:
        active = " active" if file_name == active_file else ""
        links.append(f'            <a class="nav-link{active}" href="{file_name}">{label}</a>')

    return (
        '<nav class="navbar navbar-expand-lg navbar-dark bg-primary">\n'
        '    <div class="container">\n'
        '        <a class="navbar-brand" href="index.html">Smart Library AI</a>\n'
        '        <div class="navbar-nav ms-auto">\n'
        + "\n".join(links) +
        '\n        </div>\n'
        '    </div>\n'
        '</nav>'
    )


def replace_navbar(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    new_nav = build_nav(file_path.name)
    pattern = re.compile(r'<nav class="navbar[\s\S]*?</nav>', re.MULTILINE)

    if pattern.search(content):
        content = pattern.sub(new_nav, content, count=1)
    else:
        content = content.replace("<body>", "<body>\n" + new_nav, 1)

    content = content.replace('href="ml.html"', 'href="ml_hybrid.html"')
    content = content.replace('>IA<', '>IA Hybride<')
    file_path.write_text(content, encoding="utf-8")


def build_index_cards() -> str:
    cards = []
    for href, title, text in INDEX_CARDS:
        cards.append(
            f"""
            <div class=\"col-md-6 col-lg-4\">
                <div class=\"card card-stat h-100\">
                    <div class=\"card-body\">
                        <h5>{title}</h5>
                        <p>{text}</p>
                        <a href=\"{href}\" class=\"btn btn-primary\">Ouvrir</a>
                    </div>
                </div>
            </div>"""
        )
    return '<div class="row mt-4 g-4">' + "".join(cards) + '\n        </div>'


def update_index_cards():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    new_cards = build_index_cards()
    pattern = re.compile(r'<div class="row mt-4 g-4">[\s\S]*?</div>\s*<div class="mt-4 small-muted">', re.MULTILINE)
    replacement = new_cards + '\n\n        <div class="mt-4 small-muted">'
    if pattern.search(content):
        content = pattern.sub(replacement, content, count=1)
    else:
        content = content.replace('<div class="mt-4 small-muted">', new_cards + '\n\n        <div class="mt-4 small-muted">', 1)
    index_path.write_text(content, encoding="utf-8")


def main():
    if not FRONTEND_DIR.exists():
        raise SystemExit("Dossier frontend introuvable. Lance ce script depuis la racine du projet.")

    for file_name, _ in PAGES:
        file_path = FRONTEND_DIR / file_name
        if file_path.exists():
            replace_navbar(file_path)
            print(f"Navbar uniformisée : {file_path}")
        else:
            print(f"Page absente, ignorée : {file_path}")

    update_index_cards()
    print("Cartes de index.html mises à jour vers IA Hybride.")
    print("Terminé. Recharge le navigateur avec Ctrl+Shift+R.")


if __name__ == "__main__":
    main()
