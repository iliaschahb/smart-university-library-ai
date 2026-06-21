from pathlib import Path

PAGES = [
    'frontend/index.html', 'frontend/books.html', 'frontend/students.html', 'frontend/loans.html',
    'frontend/dashboard.html', 'frontend/bigdata.html', 'frontend/ml_hybrid.html',
    'frontend/recommendations.html', 'frontend/librarian_dashboard.html',
    'frontend/admin_panel.html', 'frontend/visualizations.html', 'frontend/catalog_relational.html',
]


def ensure_link(content, href):
    tag = f'<link rel="stylesheet" href="{href}">'
    if tag in content:
        return content
    return content.replace('</head>', f'    {tag}\n</head>')


def ensure_script(content, src):
    tag = f'<script src="{src}"></script>'
    if tag in content:
        return content
    return content.replace('</body>', f'    {tag}\n</body>')


def normalize_text(content):
    replacements = {
        'BORROWED': 'En cours',
        'RETURNED': 'Retourné',
        'LATE': 'En retard',
        'Big Data': 'Analyses',
        'IA Hybride': 'Prévisions',
        'Visualisations': 'Graphiques',
        'Catalogue Kaggle': 'Catalogue avancé',
        'catalogue Kaggle relationnel': 'catalogue complet',
        'Dashboard bibliothécaire dynamique': 'Tableau de bord bibliothèque',
        'Visualisation métier mise à jour automatiquement depuis les données SQLite / Flask.': 'Suivi des indicateurs de la bibliothèque, mis à jour automatiquement.',
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content


for page in PAGES:
    p = Path(page)
    if not p.exists():
        print('Absent:', page)
        continue
    content = p.read_text(encoding='utf-8')
    content = ensure_link(content, 'css/ui_final.css')
    content = ensure_script(content, 'js/ui_helpers.js')
    content = normalize_text(content)
    p.write_text(content, encoding='utf-8')
    print('UI final appliquée:', page)
