from flask import Blueprint, jsonify, request
from database import db
from models import Book, Category

books_bp = Blueprint("books_bp", __name__)


@books_bp.route("/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200


@books_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Livre introuvable"}), 404

    return jsonify(book.to_dict()), 200


@books_bp.route("/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON invalide ou manquant"}), 400

    title = data.get("title")
    author = data.get("author")
    isbn = data.get("isbn")
    category_id = data.get("category_id")
    publication_year = data.get("publication_year")
    quantity = data.get("quantity", 1)

    if not title:
        return jsonify({"error": "Le titre est obligatoire"}), 400

    # Vérification optionnelle de la catégorie
    if category_id is not None:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Catégorie introuvable"}), 400

    new_book = Book(
        title=title,
        author=author,
        isbn=isbn,
        category_id=category_id,
        publication_year=publication_year,
        quantity=quantity,
        available_quantity=quantity
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        "message": "Livre ajouté avec succès",
        "book": new_book.to_dict()
    }), 201


@books_bp.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Livre introuvable"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON invalide ou manquant"}), 400

    category_id = data.get("category_id", book.category_id)

    if category_id is not None:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Catégorie introuvable"}), 400

    old_quantity = book.quantity
    old_available_quantity = book.available_quantity

    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.isbn = data.get("isbn", book.isbn)
    book.category_id = category_id
    book.publication_year = data.get("publication_year", book.publication_year)
    book.quantity = data.get("quantity", book.quantity)

    # Ajustement simple de la disponibilité
    if "available_quantity" in data:
        book.available_quantity = data.get("available_quantity")
    elif "quantity" in data:
        difference = book.quantity - old_quantity
        book.available_quantity = max(0, old_available_quantity + difference)

    db.session.commit()

    return jsonify({
        "message": "Livre mis à jour avec succès",
        "book": book.to_dict()
    }), 200


@books_bp.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Livre introuvable"}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": "Livre supprimé avec succès"}), 200