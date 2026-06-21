from pathlib import Path

path = Path('frontend/librarian_dashboard.html')
if not path.exists():
    raise SystemExit('frontend/librarian_dashboard.html introuvable')

content = path.read_text(encoding='utf-8')

# Important: librarian page must not use admin-only guard.
content = content.replace('<script src="js/protect_admin.js"></script>', '')
content = content.replace('js/protect_admin.js', '')

required = [
    '<script src="js/api.js"></script>',
    '<script src="js/auth.js"></script>',
    '<script src="js/librarian_auth_guard.js"></script>',
]

for tag in required:
    if tag not in content:
        content = content.replace('</body>', f'    {tag}\n</body>')

if 'logoutUser()' not in content:
    content = content.replace(
        '<div class="container py-4">',
        '<div class="container py-4">\n        <div class="d-flex justify-content-end mb-3"><button class="btn btn-outline-danger" onclick="logoutUser()">Déconnexion</button></div>',
        1
    )

path.write_text(content, encoding='utf-8')
print('librarian_dashboard.html corrigé : guard bibliothécaire + logout')
