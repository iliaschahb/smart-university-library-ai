from pathlib import Path
import re

SHARED_PAGES = [
    'frontend/index.html',
    'frontend/books.html',
    'frontend/students.html',
    'frontend/loans.html',
    'frontend/dashboard.html',
    'frontend/bigdata.html',
    'frontend/ml_hybrid.html',
    'frontend/recommendations.html',
    'frontend/librarian_dashboard.html',
]

ADMIN_ONLY_PAGES = [
    'frontend/admin_panel.html',
    'frontend/visualizations.html',
    'frontend/catalog_relational.html',
]

SHARED_NAV = """<nav class=\"navbar navbar-expand-lg navbar-dark bg-primary\">\n    <div class=\"container\">\n        <a class=\"navbar-brand\" href=\"index.html\">Smart Library AI</a>\n        <div class=\"navbar-nav ms-auto\">\n            <a class=\"nav-link\" href=\"index.html\">Accueil</a>\n            <a class=\"nav-link\" href=\"librarian_dashboard.html\">Bibliothèque</a>\n            <a class=\"nav-link\" href=\"dashboard.html\">Tableau de bord</a>\n            <a class=\"nav-link\" href=\"books.html\">Livres</a>\n            <a class=\"nav-link\" href=\"students.html\">Étudiants</a>\n            <a class=\"nav-link\" href=\"loans.html\">Emprunts</a>\n            <a class=\"nav-link\" href=\"bigdata.html\">Analyses</a>\n            <a class=\"nav-link\" href=\"ml_hybrid.html\">Prévisions</a>\n            <a class=\"nav-link\" href=\"recommendations.html\">Suggestions</a>\n            <button class=\"btn btn-sm btn-outline-light ms-2\" onclick=\"logoutUser()\">Déconnexion</button>\n        </div>\n    </div>\n</nav>"""

ADMIN_NAV = """<nav class=\"navbar navbar-expand-lg navbar-dark bg-primary\">\n    <div class=\"container\">\n        <a class=\"navbar-brand\" href=\"index.html\">Smart Library AI</a>\n        <div class=\"navbar-nav ms-auto\">\n            <a class=\"nav-link\" href=\"index.html\">Accueil</a>\n            <a class=\"nav-link\" href=\"admin_panel.html\">Administration</a>\n            <a class=\"nav-link\" href=\"librarian_dashboard.html\">Bibliothèque</a>\n            <a class=\"nav-link\" href=\"dashboard.html\">Tableau de bord</a>\n            <a class=\"nav-link\" href=\"books.html\">Livres</a>\n            <a class=\"nav-link\" href=\"students.html\">Étudiants</a>\n            <a class=\"nav-link\" href=\"loans.html\">Emprunts</a>\n            <a class=\"nav-link\" href=\"bigdata.html\">Analyses</a>\n            <a class=\"nav-link\" href=\"ml_hybrid.html\">Prévisions</a>\n            <a class=\"nav-link\" href=\"recommendations.html\">Suggestions</a>\n            <a class=\"nav-link\" href=\"visualizations.html\">Graphiques</a>\n            <a class=\"nav-link\" href=\"catalog_relational.html\">Catalogue avancé</a>\n            <button class=\"btn btn-sm btn-outline-light ms-2\" onclick=\"logoutUser()\">Déconnexion</button>\n        </div>\n    </div>\n</nav>"""


def replace_navbar(content: str, navbar: str) -> str:
    pattern = re.compile(r'<nav class="navbar[\s\S]*?</nav>', re.MULTILINE)
    if pattern.search(content):
        return pattern.sub(navbar, content, count=1)
    return content.replace('<body>', '<body>\n' + navbar, 1)


def ensure_style(content: str, href: str) -> str:
    tag = f'<link rel="stylesheet" href="{href}">'
    if tag in content:
        return content
    return content.replace('</head>', f'    {tag}\n</head>')


def ensure_script(content: str, src: str) -> str:
    tag = f'<script src="{src}"></script>'
    if tag in content:
        return content
    return content.replace('</body>', f'    {tag}\n</body>')


def remove_script(content: str, src: str) -> str:
    tag = f'<script src="{src}"></script>'
    return content.replace(tag, '')


def normalize_text(content: str) -> str:
    replacements = {
        'Catalogue Kaggle': 'Catalogue avancé',
        'catalogue Kaggle relationnel': 'catalogue complet',
        'Visualisations': 'Graphiques',
        'Visualisation métier mise à jour automatiquement depuis les données SQLite / Flask.': 'Suivi des indicateurs de la bibliothèque, mis à jour automatiquement.',
        'Dashboard bibliothécaire dynamique': 'Tableau de bord bibliothèque',
        'Big Data': 'Analyses',
        'IA Hybride': 'Prévisions',
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content


def process_shared_page(page_path: Path):
    content = page_path.read_text(encoding='utf-8')
    content = replace_navbar(content, SHARED_NAV)
    content = normalize_text(content)
    content = ensure_style(content, 'css/home_icons.css')
    # Remove admin guard from shared pages
    content = remove_script(content, 'js/protect_admin.js')
    content = remove_script(content, 'js/librarian_auth_guard.js' if page_path.name != 'librarian_dashboard.html' else 'js/protect_app_user.js')
    content = ensure_script(content, 'js/api.js')
    content = ensure_script(content, 'js/auth.js')
    if page_path.name == 'librarian_dashboard.html':
        content = ensure_script(content, 'js/librarian_auth_guard.js')
    else:
        content = ensure_script(content, 'js/protect_app_user.js')
    page_path.write_text(content, encoding='utf-8')
    print(f'Corrigé (partagée): {page_path}')


def process_admin_page(page_path: Path):
    content = page_path.read_text(encoding='utf-8')
    content = replace_navbar(content, ADMIN_NAV)
    content = normalize_text(content)
    content = ensure_style(content, 'css/home_icons.css')
    content = remove_script(content, 'js/protect_app_user.js')
    content = remove_script(content, 'js/librarian_auth_guard.js')
    content = ensure_script(content, 'js/api.js')
    content = ensure_script(content, 'js/auth.js')
    content = ensure_script(content, 'js/protect_admin.js')
    page_path.write_text(content, encoding='utf-8')
    print(f'Corrigé (admin): {page_path}')


def main():
    for page in SHARED_PAGES:
        p = Path(page)
        if p.exists():
            process_shared_page(p)
        else:
            print(f'Absent: {p}')

    for page in ADMIN_ONLY_PAGES:
        p = Path(page)
        if p.exists():
            process_admin_page(p)
        else:
            print(f'Absent: {p}')


if __name__ == '__main__':
    main()
