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


for page in PAGES:
    p = Path(page)
    if not p.exists():
        print('Absent:', page)
        continue

    content = p.read_text(encoding='utf-8')

    if '<div id="dynamicNavbarHost"></div>' not in content:
        content = content.replace('<body>', '<body>\n<div id="dynamicNavbarHost"></div>', 1)

    content = ensure_link(content, 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css')
    content = ensure_link(content, 'css/sidebar_dynamic.css')
    content = ensure_script(content, 'js/api.js')
    content = ensure_script(content, 'js/auth.js')
    content = ensure_script(content, 'js/nav_role.js')

    p.write_text(content, encoding='utf-8')
    print('Sidebar appliquée:', page)
