"""
Génère des données OPÉRATIONNELLES synthétiques : étudiants, stock local, emprunts.
IMPORTANT : ces données sont artificielles et uniquement destinées à la démonstration.
Règle appliquée ici :
- le prénom peut se répéter
- le nom de famille ne doit pas se répéter
"""

import random
from datetime import date, timedelta

from app import app
from database import db
from models_kaggle_catalog import BooksCatalog, Inventory, StudentLocal, LoanLocal, BookAnalytics


FIRST_NAMES = [
    "Youssef", "Sara", "Aya", "Hamza", "Meryem", "Omar", "Salma", "Imane", "Rayan", "Lina",
    "Nour", "Kenza", "Amine", "Yassine", "Hiba", "Soukaina", "Anas", "Ilyas", "Ikram", "Nadia",
    "Zakaria", "Amina", "Bilal", "Marwa", "Samir", "Siham", "Reda", "Nisrine", "Adnane", "Chaimae",
    "Fatima", "Othmane", "Hajar", "Mehdi", "Khadija", "Mounir", "Asmae", "Taha", "Yasmine", "Abdelilah"
]

# On construit des noms de famille composés pour avoir un très grand nombre de noms uniques
LAST_NAME_PART1 = [
    "El", "Ben", "Ait", "Bou", "Bel", "Ould", "Alaoui", "Bennani", "Amrani", "Tazi",
    "Lahlou", "Fassi", "Kabbaj", "Rami", "Berrada", "Skalli", "Mernissi", "Kadiri", "Toumi", "Tahiri",
    "Lamrani", "Azzouzi", "Essaidi", "Filali", "Mokhtari", "Sabri", "Hariri", "Boukili", "El Idrissi", "El Mansouri"
]

LAST_NAME_PART2 = [
    "Idrissi", "Alaoui", "Bennani", "Amrani", "Tazi", "Chahboun", "Lahlou", "Fassi", "Kabbaj", "Rami",
    "Berrada", "Skalli", "Mernissi", "Boussaid", "Lahcen", "Kadiri", "Toumi", "Aouad", "Belkadi", "Mansouri",
    "Benjelloun", "Filali", "Zouhair", "Tahiri", "Lamrani", "Azzouzi", "Essaidi", "Mehdioui", "Rifai", "Rahmouni",
    "Chraibi", "Slaoui", "El Fassi", "El Ouazzani", "Bouzidi", "Mouline", "Rharbi", "Benkirane", "Nemli", "Bousselham"
]

DEPARTMENTS = [
    "Big Data",
    "Intelligence Artificielle",
    "Développement Web",
    "Base de données",
    "Cybersécurité"
]

LEVELS = ["L1", "L2", "L3", "Master 1", "Master 2"]


def generate_unique_last_name(used_last_names, index):
    """
    Génère un nom de famille unique.
    Le prénom pourra se répéter, mais pas le nom de famille.
    """
    max_attempts = 5000

    for _ in range(max_attempts):
        part1 = random.choice(LAST_NAME_PART1)
        part2 = random.choice(LAST_NAME_PART2)

        # éviter des répétitions triviales du style "Alaoui Alaoui"
        if part1.strip() == part2.strip():
            continue

        last_name = f"{part1} {part2}".strip()

        if last_name not in used_last_names:
            used_last_names.add(last_name)
            return last_name

    # fallback sécurité si toutes les combinaisons sont épuisées
    last_name = f"{random.choice(LAST_NAME_PART1)} {random.choice(LAST_NAME_PART2)}-{index}"
    used_last_names.add(last_name)
    return last_name


def seed(seed_value=42, students_count=20, loans_count=50, stocked_books=120):
    random.seed(seed_value)

    with app.app_context():
        db.create_all()

        books = BooksCatalog.query.order_by(BooksCatalog.ratings_count.desc()).limit(stocked_books).all()
        if not books:
            raise RuntimeError(
                "Le catalogue Kaggle est vide. Exécute d'abord sync_kaggle_catalog_to_db.py"
            )

        # ================================
        # Stock local synthétique
        # ================================
        for idx, book in enumerate(books, start=1):
            inventory = book.inventory or Inventory(book_id=book.book_id)
            inventory.quantity = random.randint(2, 8)
            inventory.available_quantity = inventory.quantity
            inventory.shelf_location = f"A-{(idx % 20) + 1}"

            if not book.inventory:
                db.session.add(inventory)

        # ================================
        # Étudiants synthétiques
        # Règle : NOMS DE FAMILLE UNIQUES
        # ================================
        existing_students = StudentLocal.query.count()

        # On récupère les noms de famille déjà utilisés pour éviter toute répétition
        used_last_names = set()
        for student in StudentLocal.query.all():
            parts = student.full_name.strip().split(" ", 1)
            if len(parts) == 2:
                used_last_names.add(parts[1].strip())

        for i in range(existing_students + 1, existing_students + students_count + 1):
            first_name = random.choice(FIRST_NAMES)
            last_name = generate_unique_last_name(used_last_names, i)
            full_name = f"{first_name} {last_name}"

            student = StudentLocal(
                full_name=full_name,
                email=f"student{i}@example.edu",
                department=random.choice(DEPARTMENTS),
                level=random.choice(LEVELS),
            )
            db.session.add(student)

        db.session.commit()

        students = StudentLocal.query.all()
        loans_created = 0

        # ================================
        # Emprunts synthétiques
        # ================================
        for _ in range(loans_count):
            student = random.choice(students)
            book = random.choice(books)
            inventory = book.inventory

            if not inventory or inventory.available_quantity <= 0:
                continue

            borrow_date = date.today() - timedelta(days=random.randint(1, 45))
            due_date = borrow_date + timedelta(days=14)
            returned = random.random() < 0.65

            loan = LoanLocal(
                student_id=student.student_id,
                book_id=book.book_id,
                borrow_date=borrow_date,
                due_date=due_date,
                return_date=(borrow_date + timedelta(days=random.randint(3, 20))) if returned else None,
            )

            if loan.return_date:
                loan.status = "RETURNED"
            elif due_date < date.today():
                loan.status = "LATE"
            else:
                loan.status = "BORROWED"

            db.session.add(loan)
            inventory.available_quantity = max(inventory.available_quantity - 1, 0)
            loans_created += 1

        db.session.commit()

        # ================================
        # Synchronisation analytique locale
        # ================================
        stats = {}

        for loan in LoanLocal.query.all():
            info = stats.setdefault(
                loan.book_id,
                {
                    "local_loan_count": 0,
                    "local_active_loan_count": 0,
                    "local_late_count": 0
                }
            )

            info["local_loan_count"] += 1

            if loan.return_date is None:
                info["local_active_loan_count"] += 1

            if loan.status == "LATE":
                info["local_late_count"] += 1

        for book in books:
            analytics = book.analytics or BookAnalytics(book_id=book.book_id)
            info = stats.get(book.book_id, {})

            analytics.local_loan_count = info.get("local_loan_count", 0)
            analytics.local_active_loan_count = info.get("local_active_loan_count", 0)
            analytics.local_late_count = info.get("local_late_count", 0)

            analytics.demand_score = (
                float(analytics.global_popularity_score or 0)
                + (analytics.local_loan_count * 120)
                - (analytics.local_late_count * 30)
            )

            analytics.recommended_stock = max(
                2,
                min(12, int((analytics.local_loan_count / 3) + 2))
            )

            if not book.analytics:
                db.session.add(analytics)

        db.session.commit()

        print(
            f"Données synthétiques générées : "
            f"{students_count} étudiants, {loans_created} emprunts, {len(books)} livres stockés."
        )


if __name__ == "__main__":
    seed()