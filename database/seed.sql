from datetime import date, timedelta

from database import db
from models import Category, Book, User, Student, Loan


def seed_database():
    # ------------------------------------------------------------------
    # 1. Categories
    # ------------------------------------------------------------------
    if Category.query.count() == 0:
        categories = [
            Category(name="Intelligence Artificielle", description="Livres sur l’IA et le machine learning"),
            Category(name="Big Data", description="Livres sur Hadoop, Spark et traitement massif"),
            Category(name="Base de données", description="Livres sur SQL, NoSQL et Datawarehouse"),
            Category(name="Développement Web", description="Livres sur Flask, Django, APIs et frontend"),
            Category(name="Cybersécurité", description="Livres sur la sécurité des données et la cryptographie"),
        ]
        db.session.add_all(categories)
        db.session.commit()

    # ------------------------------------------------------------------
    # 2. Books
    # ------------------------------------------------------------------
    if Book.query.count() == 0:
        books = [
            Book(
                title="Introduction à l'intelligence artificielle",
                author="Jean Dupont",
                isbn="978000000001",
                category_id=1,
                publication_year=2022,
                average_rating=4.5,
                ratings_count=120,
                quantity=5,
                available_quantity=4
            ),
            Book(
                title="Machine Learning avec Python",
                author="Marie Martin",
                isbn="978000000002",
                category_id=1,
                publication_year=2021,
                average_rating=4.7,
                ratings_count=210,
                quantity=4,
                available_quantity=3
            ),
            Book(
                title="Big Data avec Spark",
                author="Ahmed Benali",
                isbn="978000000003",
                category_id=2,
                publication_year=2023,
                average_rating=4.6,
                ratings_count=180,
                quantity=6,
                available_quantity=5
            ),
            Book(
                title="Hadoop et MapReduce",
                author="Nadia Karim",
                isbn="978000000004",
                category_id=2,
                publication_year=2020,
                average_rating=4.1,
                ratings_count=90,
                quantity=3,
                available_quantity=3
            ),
            Book(
                title="Bases de données avancées",
                author="Omar Tazi",
                isbn="978000000005",
                category_id=3,
                publication_year=2021,
                average_rating=4.3,
                ratings_count=130,
                quantity=4,
                available_quantity=2
            ),
            Book(
                title="MongoDB et NoSQL",
                author="Salma Idrissi",
                isbn="978000000006",
                category_id=3,
                publication_year=2022,
                average_rating=4.4,
                ratings_count=145,
                quantity=5,
                available_quantity=4
            ),
            Book(
                title="Développement Web avec Flask",
                author="Kamal Alaoui",
                isbn="978000000007",
                category_id=4,
                publication_year=2023,
                average_rating=4.8,
                ratings_count=170,
                quantity=5,
                available_quantity=5
            ),
            Book(
                title="APIs REST avec Python",
                author="Rachid Lahlou",
                isbn="978000000008",
                category_id=4,
                publication_year=2022,
                average_rating=4.5,
                ratings_count=110,
                quantity=4,
                available_quantity=4
            ),
            Book(
                title="Sécurité des données et cryptographie",
                author="Hicham B.",
                isbn="978000000009",
                category_id=5,
                publication_year=2021,
                average_rating=4.2,
                ratings_count=95,
                quantity=2,
                available_quantity=2
            ),
        ]
        db.session.add_all(books)
        db.session.commit()

    # ------------------------------------------------------------------
    # 3. Users + Students
    # ------------------------------------------------------------------
    if User.query.count() == 0 and Student.query.count() == 0:
        admin = User(
            name="Admin Principal",
            email="admin@library.ma",
            password_hash="hashed_admin_password",
            role="admin"
        )
        bibliothecaire = User(
            name="Bibliothecaire Central",
            email="biblio@library.ma",
            password_hash="hashed_biblio_password",
            role="bibliothecaire"
        )
        student_user_1 = User(
            name="Ilias Chahboun",
            email="ilias@student.ma",
            password_hash="hashed_student_password",
            role="etudiant"
        )
        student_user_2 = User(
            name="Sara El Fassi",
            email="sara@student.ma",
            password_hash="hashed_student_password",
            role="etudiant"
        )
        student_user_3 = User(
            name="Youssef Amrani",
            email="youssef@student.ma",
            password_hash="hashed_student_password",
            role="etudiant"
        )

        db.session.add_all([admin, bibliothecaire, student_user_1, student_user_2, student_user_3])
        db.session.commit()

        students = [
            Student(
                user_id=student_user_1.id,
                full_name="Ilias Chahboun",
                email="ilias@student.ma",
                department="Informatique",
                level="Licence 3"
            ),
            Student(
                user_id=student_user_2.id,
                full_name="Sara El Fassi",
                email="sara@student.ma",
                department="Data Science",
                level="Licence 3"
            ),
            Student(
                user_id=student_user_3.id,
                full_name="Youssef Amrani",
                email="youssef@student.ma",
                department="Mathématiques",
                level="Licence 3"
            ),
        ]

        db.session.add_all(students)
        db.session.commit()

    # ------------------------------------------------------------------
    # 4. Loans
    # ------------------------------------------------------------------
    if Loan.query.count() == 0 and Student.query.count() > 0 and Book.query.count() > 0:
        loans = [
            Loan(
                student_id=1,
                book_id=1,
                borrow_date=date.today() - timedelta(days=12),
                due_date=date.today() + timedelta(days=2),
                status="BORROWED"
            ),
            Loan(
                student_id=2,
                book_id=2,
                borrow_date=date.today() - timedelta(days=20),
                due_date=date.today() - timedelta(days=5),
                return_date=date.today() - timedelta(days=3),
                status="LATE"
            ),
            Loan(
                student_id=3,
                book_id=3,
                borrow_date=date.today() - timedelta(days=7),
                due_date=date.today() + timedelta(days=7),
                status="BORROWED"
            ),
        ]

        db.session.add_all(loans)
        db.session.commit()
