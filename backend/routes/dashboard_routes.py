from flask import Blueprint, jsonify
from sqlalchemy import func

from database import db
from models import Book, Student, Loan, Category

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def dashboard_summary():
    total_books = db.session.query(func.count(Book.id)).scalar() or 0
    total_students = db.session.query(func.count(Student.id)).scalar() or 0
    total_loans = db.session.query(func.count(Loan.id)).scalar() or 0
    available_books = db.session.query(func.coalesce(func.sum(Book.available_quantity), 0)).scalar() or 0

    top_books_query = (
        db.session.query(
            Book.id,
            Book.title,
            func.count(Loan.id).label("loan_count")
        )
        .outerjoin(Loan, Loan.book_id == Book.id)
        .group_by(Book.id, Book.title)
        .order_by(func.count(Loan.id).desc())
        .limit(5)
        .all()
    )

    top_categories_query = (
        db.session.query(
            Category.id,
            Category.name,
            func.count(Loan.id).label("loan_count")
        )
        .outerjoin(Book, Book.category_id == Category.id)
        .outerjoin(Loan, Loan.book_id == Book.id)
        .group_by(Category.id, Category.name)
        .order_by(func.count(Loan.id).desc())
        .limit(5)
        .all()
    )

    late_loans_count = db.session.query(func.count(Loan.id)).filter(Loan.status == "LATE").scalar() or 0

    return jsonify({
        "total_books": total_books,
        "total_students": total_students,
        "total_loans": total_loans,
        "available_books": available_books,
        "late_loans_count": late_loans_count,
        "top_books": [
            {
                "id": row.id,
                "title": row.title,
                "loan_count": row.loan_count
            }
            for row in top_books_query
        ],
        "top_categories": [
            {
                "id": row.id,
                "name": row.name,
                "loan_count": row.loan_count
            }
            for row in top_categories_query
        ]
    }), 200