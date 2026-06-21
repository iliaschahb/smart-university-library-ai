from pathlib import Path
path = Path('frontend/librarian_dashboard.html')
content = path.read_text(encoding='utf-8')
content = content.replace('<script src="js/protect_admin.js"></script>', '')
content = content.replace('js/protect_admin.js', '')
required = ['<script src="js/api.js"></script>', '<script src="js/auth.js"></script>', '<script src="js/librarian_auth_guard.js"></script>']
for tag in required:
    if tag not in content:
        content = content.replace('</body>', f'    {tag}\n</body>')
path.write_text(content, encoding='utf-8')
print('librarian_dashboard.html corrigé')
