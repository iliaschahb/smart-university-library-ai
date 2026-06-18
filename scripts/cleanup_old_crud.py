from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parents[1]
ARCHIVE_DIR = BASE_DIR / 'archive_old_crud'
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

FILES_TO_ARCHIVE = [
    'backend/routes/books_routes.py',
    'backend/routes/students_routes.py',
    'backend/routes/loans_routes.py',
    'backend/routes/categories_routes.py',
    'backend/models.py',
]

PAGES_TO_REVIEW = [
    'frontend/books.html',
    'frontend/students.html',
    'frontend/loans.html',
    'frontend/dashboard.html',
]


def move_file(rel_path: str):
    src = BASE_DIR / rel_path
    if not src.exists():
        print(f'Ignoré (absent) : {rel_path}')
        return

    dst = ARCHIVE_DIR / rel_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    print(f'Archivé : {rel_path} -> {dst}')


def main():
    print('=== Nettoyage sécurisé du projet ===')
    print('Les anciens fichiers CRUD sont déplacés vers archive_old_crud/ au lieu d’être supprimés.')
    print()

    for rel_path in FILES_TO_ARCHIVE:
        move_file(rel_path)

    print('Pages à conserver dans le projet actif ===')
    for page in PAGES_TO_REVIEW:
        print(f'- {page}')

    print('Terminé.')
    print('Vérifie ensuite backend/app.py pour t’assurer que seuls les blueprints ACTIFS restent importés.')


if __name__ == '__main__':
    main()
