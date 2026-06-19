from database import db
from models_kaggle_catalog import BookAnalytics, BooksCatalog, LoanLocal, Inventory


def update_book_local_analytics(book_id: int):
    """
    Met à jour les statistiques locales d'un livre après une opération métier.
    Important :
    - ne réentraîne pas le modèle IA
    - met uniquement à jour les features locales utilisées par la prédiction
    """

    book = BooksCatalog.query.filter_by(book_id=book_id).first()
    if not book:
        raise ValueError(f"Livre introuvable : {book_id}")

    total_loans = LoanLocal.query.filter_by(book_id=book_id).count()

    active_loans = (
        LoanLocal.query
        .filter_by(book_id=book_id)
        .filter(LoanLocal.return_date.is_(None))
        .count()
    )

    late_loans = (
        LoanLocal.query
        .filter_by(book_id=book_id, status="LATE")
        .count()
    )

    analytics = BookAnalytics.query.filter_by(book_id=book_id).first()

    if not analytics:
        analytics = BookAnalytics(book_id=book_id)
        db.session.add(analytics)

    analytics.local_loan_count = total_loans
    analytics.local_active_loan_count = active_loans
    analytics.local_late_count = late_loans

    analytics.demand_score = (
        float(analytics.global_popularity_score or 0)
        + (total_loans * 120)
        - (late_loans * 30)
    )

    analytics.recommended_stock = max(
        2,
        min(12, int((total_loans / 3) + 2))
    )

    db.session.commit()

    return analytics


def update_inventory_availability(book_id: int):
    """
    Synchronise la disponibilité locale selon les emprunts actifs.
    Utile si des données ont été modifiées manuellement.
    """

    inventory = Inventory.query.filter_by(book_id=book_id).first()
    if not inventory:
        raise ValueError(f"Stock introuvable pour le livre : {book_id}")

    active_loans = (
        LoanLocal.query
        .filter_by(book_id=book_id)
        .filter(LoanLocal.return_date.is_(None))
        .count()
    )

    inventory.available_quantity = max(
        int(inventory.quantity or 0) - active_loans,
        0
    )

    db.session.commit()

    return inventory