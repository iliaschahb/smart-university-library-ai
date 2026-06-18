from pathlib import Path
import re

FRONTEND_DIR = Path('frontend')
PROTECTED_PAGES = [
    'admin_panel.html', 'librarian_dashboard.html', 'dashboard.html', 'books.html',
    'students.html', 'loans.html', 'bigdata.html', 'ml_hybrid.html',
    'recommendations.html', 'visualizations.html', 'catalog_relational.html'
]

NAV = """<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="index.html">Smart Library AI</a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link" href="index.html">Accueil</a>
            <a class="nav-link" href="admin_panel.html">Admin</a>
            <a class="nav-link" href="librarian_dashboard.html">Bibliothécaire</a>
            <a class="nav-link" href="dashboard.html">Dashboard</a>
            <a class="nav-link" href="books.html">Livres</a>
            <a class="nav-link" href="students.html">Étudiants</a>
            <a class="nav-link" href="loans.html">Emprunts</a>
            <a class="nav-link" href="bigdata.html">Big Data</a>
            <a class="nav-link" href="ml_hybrid.html">IA Hybride</a>
            <a class="nav-link" href="recommendations.html">Recommandations</a>
            <a class="nav-link" href="visualizations.html">Visualisations</a>
            <a class="nav-link" href="catalog_relational.html">Catalogue Kaggle</a>
            <button class="btn btn-sm btn-outline-light ms-2" onclick="logoutUser()">Déconnexion</button>
        </div>
    </div>
</nav>"""


def ensure_script(content, script):
    tag = f'<script src="{script}"></script>'
    if tag in content:
        return content
    return content.replace('</body>', f'    {tag}\n</body>')


def update_page(path: Path):
    content = path.read_text(encoding='utf-8')
    pattern = re.compile(r'<nav class="navbar[\s\S]*?</nav>', re.MULTILINE)
    if pattern.search(content):
        content = pattern.sub(NAV, content, count=1)
    else:
        content = content.replace('<body>', '<body>\n' + NAV, 1)
    content = content.replace('href="ml.html"', 'href="ml_hybrid.html"').replace('>IA<', '>IA Hybride<')
    content = ensure_script(content, 'js/api.js')
    content = ensure_script(content, 'js/auth.js')
    content = ensure_script(content, 'js/protect_admin.js')
    path.write_text(content, encoding='utf-8')
    print(f'Page protégée : {path}')


def main():
    for page in PROTECTED_PAGES:
        path = FRONTEND_DIR / page
        if path.exists():
            update_page(path)
        else:
            print(f'Page absente : {path}')

if __name__ == '__main__':
    main()
