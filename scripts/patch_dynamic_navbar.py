from pathlib import Path
import re

PAGES = [
    'frontend/index.html',
    'frontend/books.html',
    'frontend/students.html',
    'frontend/loans.html',
    'frontend/dashboard.html',
    'frontend/bigdata.html',
    'frontend/ml_hybrid.html',
    'frontend/recommendations.html',
    'frontend/librarian_dashboard.html',
    'frontend/admin_panel.html',
    'frontend/visualizations.html',
    'frontend/catalog_relational.html',
]

NAV_PLACEHOLDER = '<div id="dynamicNavbarHost"></div>'


def ensure_link(content: str, href: str) -> str:
    tag = f'<link rel="stylesheet" href="{href}">'
    if tag in content:
        return content
    if '</head>' in content:
        return content.replace('</head>', f'    {tag}\n</head>', 1)
    return content


def ensure_script(content: str, src: str) -> str:
    tag = f'<script src="{src}"></script>'
    if tag in content:
        return content
    if '</body>' in content:
        return content.replace('</body>', f'    {tag}\n</body>', 1)
    return content + f'\n{tag}\n'


def remove_script(content: str, src: str) -> str:
    tag = f'<script src="{src}"></script>'
    return content.replace(tag, '')


def normalize_labels(content: str) -> str:
    replacements = {
        'Catalogue Kaggle': 'Catalogue avancé',
        'catalogue Kaggle relationnel': 'catalogue complet',
        'Visualisations': 'Graphiques',
        'Big Data': 'Analyses',
        'IA Hybride': 'Prévisions',
        'Dashboard bibliothécaire dynamique': 'Tableau de bord bibliothèque',
        'Visualisation métier mise à jour automatiquement depuis les données SQLite / Flask.': 'Suivi des indicateurs de la bibliothèque, mis à jour automatiquement.',
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content


def patch_page(path: Path):
    content = path.read_text(encoding='utf-8')

    # Remplacer une navbar HTML normale par le conteneur dynamique.
    pattern = re.compile(r'<nav class="navbar[\s\S]*?</nav>', re.MULTILINE)
    if pattern.search(content):
        content = pattern.sub(NAV_PLACEHOLDER, content, count=1)
    elif NAV_PLACEHOLDER not in content:
        content = content.replace('<body>', '<body>\n' + NAV_PLACEHOLDER, 1)

    content = normalize_labels(content)

    # Nettoyer les anciennes inclusions éventuelles pour éviter les doublons.
    content = remove_script(content, 'js/nav_role.js')

    # Ajouter les fichiers nécessaires à la navbar dynamique.
    content = ensure_link(content, 'css/navbar_dynamic.css')
    content = ensure_script(content, 'js/api.js')
    content = ensure_script(content, 'js/auth.js')
    content = ensure_script(content, 'js/nav_role.js')

    path.write_text(content, encoding='utf-8')
    print(f'Patch navbar dynamique : {path}')


def main():
    for page in PAGES:
        p = Path(page)
        if p.exists():
            patch_page(p)
        else:
            print(f'Absent : {page}')


if __name__ == '__main__':
    main()
