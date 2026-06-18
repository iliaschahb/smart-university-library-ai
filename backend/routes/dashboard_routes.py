from flask import Blueprint, jsonify
from sqlalchemy import func

from database import db
from models_kaggle_catalog import BooksCatalog, Inventory, StudentLocal, LoanLocal, BookAnalytics


dashboard_bp = Blueprint("dashboard_bp", __name__)


def safe_int(value):
    return int(value or 0)


@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def dashboard_summary():
    books_catalog = safe_int(db.session.query(func.count(BooksCatalog.book_id)).scalar())
    stocked_titles = safe_int(db.session.query(func.count(Inventory.id)).scalar())
    total_copies = safe_int(db.session.query(func.coalesce(func.sum(Inventory.quantity), 0)).scalar())
    available_copies = safe_int(db.session.query(func.coalesce(func.sum(Inventory.available_quantity), 0)).scalar())
    borrowed_copies = max(total_copies - available_copies, 0)
    students = safe_int(db.session.query(func.count(StudentLocal.student_id)).scalar())
    total_loans = safe_int(db.session.query(func.count(LoanLocal.loan_id)).scalar())
    active_loans = safe_int(db.session.query(func.count(LoanLocal.loan_id)).filter(LoanLocal.return_date.is_(None)).scalar())

    top_borrowed = (
        db.session.query(
            BooksCatalog.title,
            func.count(LoanLocal.loan_id).label("loan_count")
        )
        .join(LoanLocal, LoanLocal.book_id == BooksCatalog.book_id)
        .group_by(BooksCatalog.book_id, BooksCatalog.title)
        .order_by(func.count(LoanLocal.loan_id).desc(), BooksCatalog.title.asc())
        .limit(5)
        .all()
    )

    top_popular = (
        db.session.query(
            BooksCatalog.title,
            BookAnalytics.global_popularity_score,
            BookAnalytics.global_popularity_level,
        )
        .join(BookAnalytics, BookAnalytics.book_id == BooksCatalog.book_id)
        .order_by(BookAnalytics.global_popularity_score.desc(), BooksCatalog.title.asc())
        .limit(5)
        .all()
    )

    return jsonify({
        "catalog_books": books_catalog,
        "stocked_titles": stocked_titles,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "borrowed_copies": borrowed_copies,
        "students": students,
        "total_loans": total_loans,
        "active_loans": active_loans,
        "top_borrowed": [
            {"title": row.title, "loan_count": safe_int(row.loan_count)}
            for row in top_borrowed
        ],
        "top_popular": [
            {
                "title": row.title,
                "global_popularity_score": float(row.global_popularity_score or 0),
                "global_popularity_level": row.global_popularity_level,
            }
            for row in top_popular
        ]
    }), 200
