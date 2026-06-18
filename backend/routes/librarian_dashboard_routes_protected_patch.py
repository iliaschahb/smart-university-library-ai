# Patch à appliquer dans backend/routes/librarian_dashboard_routes.py
# Remplacer l'ancien fichier par cette version si besoin.

from datetime import date

from flask import Blueprint, jsonify
from sqlalchemy import func

from database import db
from models_kaggle_catalog import BooksCatalog, StudentLocal, LoanLocal, Inventory, BookAnalytics
from routes.auth_routes import librarian_required


librarian_dashboard_bp = Blueprint("librarian_dashboard_bp", __name__)


def safe_int(value):
    return int(value or 0)


def days_late(due_date):
    if not due_date:
        return 0
    return max((date.today() - due_date).days, 0)


@librarian_dashboard_bp.route("/librarian/dashboard", methods=["GET"])
@librarian_required
def librarian_dashboard():
    total_book_titles = safe_int(db.session.query(func.count(BooksCatalog.book_id)).scalar())
    total_students = safe_int(db.session.query(func.count(StudentLocal.student_id)).scalar())
    total_book_copies = safe_int(db.session.query(func.coalesce(func.sum(Inventory.quantity), 0)).scalar())
    available_books = safe_int(db.session.query(func.coalesce(func.sum(Inventory.available_quantity), 0)).scalar())
    borrowed_books = max(total_book_copies - available_books, 0)
    total_loans = safe_int(db.session.query(func.count(LoanLocal.loan_id)).scalar())
    active_loans = safe_int(db.session.query(func.count(LoanLocal.loan_id)).filter(LoanLocal.return_date.is_(None)).scalar())
    returned_loans = safe_int(db.session.query(func.count(LoanLocal.loan_id)).filter(LoanLocal.return_date.isnot(None)).scalar())

    late_loans_query = (
        LoanLocal.query
        .filter(LoanLocal.return_date.is_(None))
        .filter(LoanLocal.due_date < date.today())
        .all()
    )
    late_loans_count = len(late_loans_query)

    low_stock_books_query = (
        db.session.query(BooksCatalog, Inventory, BookAnalytics)
        .join(Inventory, Inventory.book_id == BooksCatalog.book_id)
        .outerjoin(BookAnalytics, BookAnalytics.book_id == BooksCatalog.book_id)
        .filter(Inventory.available_quantity <= 1)
        .order_by(Inventory.available_quantity.asc(), BooksCatalog.title.asc())
        .limit(10)
        .all()
    )

    out_of_stock_books = safe_int(db.session.query(func.count(Inventory.id)).filter(Inventory.available_quantity <= 0).scalar())
    low_stock_books = safe_int(db.session.query(func.count(Inventory.id)).filter(Inventory.available_quantity <= 1).scalar())

    loans_status_chart = [
        {"status": "BORROWED", "count": max(active_loans - late_loans_count, 0)},
        {"status": "LATE", "count": late_loans_count},
        {"status": "RETURNED", "count": returned_loans},
    ]

    top_borrowed_rows = (
        db.session.query(
            BooksCatalog.book_id,
            BooksCatalog.title,
            func.count(LoanLocal.loan_id).label("loan_count")
        )
        .join(LoanLocal, LoanLocal.book_id == BooksCatalog.book_id)
        .group_by(BooksCatalog.book_id, BooksCatalog.title)
        .order_by(func.count(LoanLocal.loan_id).desc(), BooksCatalog.title.asc())
        .limit(10)
        .all()
    )
    top_borrowed_books = [
        {"book_id": row.book_id, "title": row.title, "loan_count": safe_int(row.loan_count)}
        for row in top_borrowed_rows
    ]

    late_loans = []
    for loan in late_loans_query[:10]:
        late_loans.append({
            "loan_id": loan.loan_id,
            "student_id": loan.student_id,
            "student_name": loan.student.full_name if loan.student else "Étudiant inconnu",
            "book_id": loan.book_id,
            "book_title": loan.book.title if loan.book else "Livre inconnu",
            "borrow_date": loan.borrow_date.isoformat() if loan.borrow_date else None,
            "due_date": loan.due_date.isoformat() if loan.due_date else None,
            "days_late": days_late(loan.due_date),
        })

    stock_alerts = []
    for book, inventory, analytics in low_stock_books_query:
        stock_alerts.append({
            "book_id": book.book_id,
            "title": book.title,
            "quantity": safe_int(inventory.quantity),
            "available_quantity": safe_int(inventory.available_quantity),
            "global_popularity_level": analytics.global_popularity_level if analytics else "faible",
            "recommended_stock": analytics.recommended_stock if analytics else 0,
            "alert_level": "rupture" if safe_int(inventory.available_quantity) <= 0 else "faible",
        })

    return jsonify({
        "kpis": {
            "total_book_titles": total_book_titles,
            "total_book_copies": total_book_copies,
            "available_books": available_books,
            "borrowed_books": borrowed_books,
            "total_loans": total_loans,
            "active_loans": active_loans,
            "returned_loans": returned_loans,
            "late_loans": late_loans_count,
            "total_students": total_students,
            "low_stock_books": low_stock_books,
            "out_of_stock_books": out_of_stock_books,
        },
        "availability_chart": {"available": available_books, "borrowed": borrowed_books},
        "loans_status_chart": loans_status_chart,
        "books_by_category": [],
        "top_borrowed_books": top_borrowed_books,
        "late_loans": late_loans,
        "stock_alerts": stock_alerts,
        "auto_refresh_seconds": 30,
    }), 200
