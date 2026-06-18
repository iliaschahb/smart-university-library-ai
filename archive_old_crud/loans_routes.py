from datetime import datetime, date, timedelta
from flask import Blueprint, jsonify, request

from database import db
from models import Loan, Student, Book

loans_bp = Blueprint("loans_bp", __name__)


def loan_to_dict(loan):
    return {
        "id": loan.id,
        "student_id": loan.student_id,
        "student_name": loan.student.full_name if loan.student else None,
        "book_id": loan.book_id,
        "book_title": loan.book.title if loan.book else None,
        "borrow_date": loan.borrow_date.isoformat() if loan.borrow_date else None,
        "due_date": loan.due_date.isoformat() if loan.due_date else None,
        "return_date": loan.return_date.isoformat() if loan.return_date else None,
        "status": loan.status,
        "created_at": loan.created_at.isoformat() if loan.created_at else None
    }


def parse_date(value, field_name):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Le champ {field_name} doit être au format YYYY-MM-DD")


@loans_bp.route("/loans", methods=["GET"])
def get_loans():
    loans = Loan.query.order_by(Loan.id.desc()).all()
    return jsonify([loan_to_dict(loan) for loan in loans]), 200


@loans_bp.route("/loans/<int:loan_id>", methods=["GET"])
def get_loan(loan_id):
    loan = db.session.get(Loan, loan_id)

    if not loan:
        return jsonify({"error": "Emprunt introuvable"}), 404

    return jsonify(loan_to_dict(loan)), 200


@loans_bp.route("/loans", methods=["POST"])
def create_loan():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON invalide ou manquant"}), 400

    student_id = data.get("student_id")
    book_id = data.get("book_id")
    borrow_date_str = data.get("borrow_date")
    due_date_str = data.get("due_date")

    if not student_id or not book_id:
        return jsonify({"error": "student_id et book_id sont obligatoires"}), 400

    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"error": "Étudiant introuvable"}), 404

    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Livre introuvable"}), 404

    if book.available_quantity <= 0:
        return jsonify({"error": "Aucun exemplaire disponible pour ce livre"}), 400

    try:
        if borrow_date_str:
            borrow_date = parse_date(borrow_date_str, "borrow_date")
        else:
            borrow_date = date.today()

        if due_date_str:
            due_date = parse_date(due_date_str, "due_date")
        else:
            due_date = borrow_date + timedelta(days=14)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    new_loan = Loan(
        student_id=student_id,
        book_id=book_id,
        borrow_date=borrow_date,
        due_date=due_date,
        status="BORROWED"
    )

    book.available_quantity -= 1

    db.session.add(new_loan)
    db.session.commit()

    return jsonify({
        "message": "Emprunt enregistré avec succès",
        "loan": loan_to_dict(new_loan)
    }), 201


@loans_bp.route("/loans/<int:loan_id>/return", methods=["PUT"])
def return_loan(loan_id):
    loan = db.session.get(Loan, loan_id)

    if not loan:
        return jsonify({"error": "Emprunt introuvable"}), 404

    if loan.return_date is not None:
        return jsonify({"error": "Ce livre a déjà été retourné"}), 400

    data = request.get_json(silent=True) or {}
    return_date_str = data.get("return_date")

    try:
        if return_date_str:
            return_date = parse_date(return_date_str, "return_date")
        else:
            return_date = date.today()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    loan.return_date = return_date

    if return_date > loan.due_date:
        loan.status = "LATE"
    else:
        loan.status = "RETURNED"

    if loan.book:
        loan.book.available_quantity += 1

    db.session.commit()

    return jsonify({
        "message": "Retour enregistré avec succès",
        "loan": loan_to_dict(loan)
    }), 200


@loans_bp.route("/loans/late", methods=["GET"])
def get_late_loans():
    today = date.today()

    loans = Loan.query.filter(
        Loan.return_date.is_(None),
        Loan.due_date < today
    ).all()

    # Mise à jour automatique du statut
    for loan in loans:
        if loan.status != "LATE":
            loan.status = "LATE"

    db.session.commit()

    return jsonify([loan_to_dict(loan) for loan in loans]), 200