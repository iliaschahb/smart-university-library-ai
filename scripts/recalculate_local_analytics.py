from app import app
from database import db
from models_kaggle_catalog import BooksCatalog, LoanLocal, BookAnalytics


def recalculate_local_analytics():
    with app.app_context():
        stats = {}

        for loan in LoanLocal.query.all():
            info = stats.setdefault(
                loan.book_id,
                {
                    "local_loan_count": 0,
                    "local_active_loan_count": 0,
                    "local_late_count": 0,
                }
            )

            info["local_loan_count"] += 1

            if loan.return_date is None:
                info["local_active_loan_count"] += 1

            if loan.status == "LATE":
                info["local_late_count"] += 1

        books = BooksCatalog.query.all()

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

        print("Statistiques locales recalculées avec succès.")
        print(f"Livres analysés : {len(books)}")
        print(f"Livres avec emprunts : {len(stats)}")


if __name__ == "__main__":
    recalculate_local_analytics()