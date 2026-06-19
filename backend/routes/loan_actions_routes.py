from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from database import db
from models_kaggle_catalog import BooksCatalog, Inventory, StudentLocal, LoanLocal
from routes.auth_routes import librarian_required
from services.analytics_service import update_book_local_analytics


loan_actions_bp = Blueprint("loan_actions_bp", __name__)


@loan_actions_bp.route("/loans/create", methods=["POST"])
@librarian_required
def create_loan():
    """
    Crée un nouvel emprunt sans réentraîner le modèle IA.
    Met à jour :
    - Inventory.available_quantity
    - BookAnalytics locales
    """

    data = request.get_json(silent=True) or {}

    student_id = data.get("student_id")
    book_id = data.get("book_id")
    days = int(data.get("days", 14))

    if not student_id or not book_id:
        return jsonify({
            "error": "student_id et book_id sont obligatoires."
        }), 400

    student = StudentLocal.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({
            "error": f"Étudiant introuvable : {student_id}"
        }), 404

    book = BooksCatalog.query.filter_by(book_id=book_id).first()
    if not book:
        return jsonify({
            "error": f"Livre introuvable : {book_id}"
        }), 404

    inventory = Inventory.query.filter_by(book_id=book_id).first()
    if not inventory:
        return jsonify({
            "error": f"Stock introuvable pour le livre : {book_id}"
        }), 404

    if int(inventory.available_quantity or 0) <= 0:
        return jsonify({
            "error": "Aucun exemplaire disponible pour ce livre."
        }), 400

    borrow_date = date.today()
    due_date = borrow_date + timedelta(days=days)

    loan = LoanLocal(
        student_id=student_id,
        book_id=book_id,
        borrow_date=borrow_date,
        due_date=due_date,
        return_date=None,
        status="BORROWED"
    )

    db.session.add(loan)
    inventory.available_quantity = max(
        int(inventory.available_quantity or 0) - 1,
        0
    )

    db.session.commit()

    analytics = update_book_local_analytics(book_id)

    return jsonify({
        "message": "Emprunt créé avec succès.",
        "loan": {
            "loan_id": loan.loan_id,
            "student_id": loan.student_id,
            "book_id": loan.book_id,
            "borrow_date": loan.borrow_date.isoformat(),
            "due_date": loan.due_date.isoformat(),
            "status": loan.status,
        },
        "inventory": {
            "quantity": inventory.quantity,
            "available_quantity": inventory.available_quantity,
        },
        "analytics": {
            "local_loan_count": analytics.local_loan_count,
            "local_active_loan_count": analytics.local_active_loan_count,
            "local_late_count": analytics.local_late_count,
            "demand_score": analytics.demand_score,
            "recommended_stock": analytics.recommended_stock,
        }
    }), 201


@loan_actions_bp.route("/loans/<int:loan_id>/return", methods=["POST"])
@librarian_required
def return_loan(loan_id):
    """
    Retourne un emprunt.
    Met à jour :
    - LoanLocal.return_date
    - LoanLocal.status
    - Inventory.available_quantity
    - BookAnalytics locales
    """

    loan = LoanLocal.query.filter_by(loan_id=loan_id).first()

    if not loan:
        return jsonify({
            "error": f"Emprunt introuvable : {loan_id}"
        }), 404

    if loan.return_date is not None:
        return jsonify({
            "error": "Cet emprunt est déjà retourné."
        }), 400

    inventory = Inventory.query.filter_by(book_id=loan.book_id).first()

    loan.return_date = date.today()
    loan.status = "RETURNED"

    if inventory:
        inventory.available_quantity = min(
            int(inventory.available_quantity or 0) + 1,
            int(inventory.quantity or 0)
        )

    db.session.commit()

    analytics = update_book_local_analytics(loan.book_id)

    return jsonify({
        "message": "Livre retourné avec succès.",
        "loan": {
            "loan_id": loan.loan_id,
            "student_id": loan.student_id,
            "book_id": loan.book_id,
            "borrow_date": loan.borrow_date.isoformat() if loan.borrow_date else None,
            "due_date": loan.due_date.isoformat() if loan.due_date else None,
            "return_date": loan.return_date.isoformat() if loan.return_date else None,
            "status": loan.status,
        },
        "inventory": {
            "quantity": inventory.quantity if inventory else None,
            "available_quantity": inventory.available_quantity if inventory else None,
        },
        "analytics": {
            "local_loan_count": analytics.local_loan_count,
            "local_active_loan_count": analytics.local_active_loan_count,
            "local_late_count": analytics.local_late_count,
            "demand_score": analytics.demand_score,
            "recommended_stock": analytics.recommended_stock,
        }
    }), 200


@loan_actions_bp.route("/inventory/<int:book_id>/update", methods=["POST"])
@librarian_required
def update_inventory(book_id):
    """
    Modifie le stock local d'un livre sans réentraîner le modèle.
    """

    data = request.get_json(silent=True) or {}

    quantity = data.get("quantity")
    shelf_location = data.get("shelf_location")

    book = BooksCatalog.query.filter_by(book_id=book_id).first()
    if not book:
        return jsonify({
            "error": f"Livre introuvable : {book_id}"
        }), 404

    inventory = Inventory.query.filter_by(book_id=book_id).first()

    if not inventory:
        inventory = Inventory(
            book_id=book_id,
            quantity=0,
            available_quantity=0
        )
        db.session.add(inventory)

    if quantity is not None:
        quantity = int(quantity)

        active_loans = (
            LoanLocal.query
            .filter_by(book_id=book_id)
            .filter(LoanLocal.return_date.is_(None))
            .count()
        )

        inventory.quantity = quantity
        inventory.available_quantity = max(quantity - active_loans, 0)

    if shelf_location is not None:
        inventory.shelf_location = str(shelf_location)

    db.session.commit()

    analytics = update_book_local_analytics(book_id)

    return jsonify({
        "message": "Stock mis à jour avec succès.",
        "book_id": book_id,
        "inventory": {
            "quantity": inventory.quantity,
            "available_quantity": inventory.available_quantity,
            "shelf_location": inventory.shelf_location,
        },
        "analytics": {
            "local_loan_count": analytics.local_loan_count,
            "local_active_loan_count": analytics.local_active_loan_count,
            "local_late_count": analytics.local_late_count,
            "demand_score": analytics.demand_score,
            "recommended_stock": analytics.recommended_stock,
        }
    }), 200