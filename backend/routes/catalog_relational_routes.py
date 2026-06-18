import json
from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from database import db
from models_kaggle_catalog import BooksCatalog, BookAnalytics, Inventory, StudentLocal, LoanLocal


catalog_relational_bp = Blueprint("catalog_relational_bp", __name__)


def parse_tags(tags_json):
    try:
        value = json.loads(tags_json or "[]")
        return value if isinstance(value, list) else []
    except Exception:
        return []


def book_public(book):
    analytics = book.analytics
    inventory = book.inventory
    return {
        "book_id": book.book_id,
        "title": book.title,
        "authors": book.authors,
        "publication_year": book.publication_year,
        "language_code": book.language_code,
        "average_rating": book.average_rating,
        "ratings_count": book.ratings_count,
        "global_popularity_score": analytics.global_popularity_score if analytics else 0,
        "global_popularity_level": analytics.global_popularity_level if analytics else "faible",
        "to_read_count": analytics.to_read_count if analytics else 0,
        "tag_count": analytics.tag_count if analytics else 0,
        "top_tags": parse_tags(analytics.top_tags_json if analytics else "[]"),
        "local_loan_count": analytics.local_loan_count if analytics else 0,
        "local_active_loan_count": analytics.local_active_loan_count if analytics else 0,
        "local_late_count": analytics.local_late_count if analytics else 0,
        "demand_score": analytics.demand_score if analytics else 0,
        "recommended_stock": analytics.recommended_stock if analytics else 0,
        "quantity": inventory.quantity if inventory else 0,
        "available_quantity": inventory.available_quantity if inventory else 0,
        "shelf_location": inventory.shelf_location if inventory else None,
    }


@catalog_relational_bp.route("/catalog/health", methods=["GET"])
def health():
    return jsonify({
        "books_catalog": BooksCatalog.query.count(),
        "inventory": Inventory.query.count(),
        "students_rel": StudentLocal.query.count(),
        "loans_rel": LoanLocal.query.count(),
        "today": date.today().isoformat(),
    }), 200


@catalog_relational_bp.route("/catalog/books", methods=["GET"])
def list_books():
    search = (request.args.get("search") or "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 20)), 1), 100)

    query = BooksCatalog.query
    if search:
        query = query.filter(
            or_(BooksCatalog.title.ilike(f"%{search}%"), BooksCatalog.authors.ilike(f"%{search}%"))
        )

    total = query.count()
    books = query.order_by(BooksCatalog.ratings_count.desc(), BooksCatalog.title.asc()) \
        .offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [book_public(book) for book in books],
    }), 200


@catalog_relational_bp.route("/catalog/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = db.session.get(BooksCatalog, book_id)
    if not book:
        return jsonify({"error": "Livre introuvable"}), 404
    return jsonify(book_public(book)), 200


def similarity_score(source, candidate):
    source_tags = set(book_public(source).get("top_tags", []))
    candidate_tags = set(book_public(candidate).get("top_tags", []))
    overlap = len(source_tags.intersection(candidate_tags))
    popularity = float(candidate.analytics.global_popularity_score if candidate.analytics else 0)
    return (overlap * 1000) + popularity


@catalog_relational_bp.route("/catalog/similar/<int:book_id>", methods=["GET"])
def similar(book_id):
    source = db.session.get(BooksCatalog, book_id)
    if not source:
        return jsonify({"error": "Livre introuvable"}), 404

    books = BooksCatalog.query.filter(BooksCatalog.book_id != book_id).all()
    scored = sorted(books, key=lambda b: similarity_score(source, b), reverse=True)[:10]
    return jsonify({
        "source": book_public(source),
        "items": [book_public(b) for b in scored],
    }), 200


@catalog_relational_bp.route("/catalog/stock-alerts", methods=["GET"])
def stock_alerts():
    books = BooksCatalog.query.join(Inventory).filter(Inventory.available_quantity <= 1).order_by(Inventory.available_quantity.asc()).all()
    return jsonify([book_public(book) for book in books]), 200


@catalog_relational_bp.route("/catalog/students", methods=["GET"])
def students():
    items = StudentLocal.query.order_by(StudentLocal.full_name.asc()).all()
    return jsonify([
        {
            "student_id": s.student_id,
            "full_name": s.full_name,
            "email": s.email,
            "department": s.department,
            "level": s.level,
            "loans_count": len(s.loans),
        }
        for s in items
    ]), 200


@catalog_relational_bp.route("/catalog/loans", methods=["GET"])
def loans():
    items = LoanLocal.query.order_by(LoanLocal.borrow_date.desc()).limit(100).all()
    return jsonify([
        {
            "loan_id": l.loan_id,
            "student_name": l.student.full_name if l.student else None,
            "book_title": l.book.title if l.book else None,
            "borrow_date": l.borrow_date.isoformat() if l.borrow_date else None,
            "due_date": l.due_date.isoformat() if l.due_date else None,
            "return_date": l.return_date.isoformat() if l.return_date else None,
            "status": l.status,
        }
        for l in items
    ]), 200
