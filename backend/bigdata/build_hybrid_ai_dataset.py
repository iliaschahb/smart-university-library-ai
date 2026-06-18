import json
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = BASE_DIR / "backend"
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import app
from models_kaggle_catalog import BooksCatalog


def build_dataset():
    with app.app_context():
        rows = []

        books = BooksCatalog.query.order_by(BooksCatalog.book_id.asc()).all()

        for book in books:
            analytics = book.analytics
            inventory = book.inventory

            rows.append({
                "book_id": book.book_id,
                "title": book.title,
                "authors": book.authors,
                "publication_year": book.publication_year,
                "language_code": book.language_code,
                "average_rating": book.average_rating,
                "ratings_count": book.ratings_count,
                "work_ratings_count": book.work_ratings_count,

                # Variables globales issues de Kaggle / analytics
                "global_popularity_score": analytics.global_popularity_score if analytics else 0,
                "global_popularity_level": analytics.global_popularity_level if analytics else "faible",
                "to_read_count": analytics.to_read_count if analytics else 0,
                "tag_count": analytics.tag_count if analytics else 0,

                # Variables locales relationnelles
                "local_loan_count": analytics.local_loan_count if analytics else 0,
                "local_active_loan_count": analytics.local_active_loan_count if analytics else 0,
                "local_late_count": analytics.local_late_count if analytics else 0,

                # Variable cible / demande
                "demand_score": analytics.demand_score if analytics else 0,
                "recommended_stock": analytics.recommended_stock if analytics else 0,

                # Stock local
                "quantity": inventory.quantity if inventory else 0,
                "available_quantity": inventory.available_quantity if inventory else 0,

                # Tags
                "top_tags_json": analytics.top_tags_json if analytics else "[]",
            })

        df = pd.DataFrame(rows)

        csv_path = ANALYTICS_DIR / "hybrid_ai_dataset.csv"
        df.to_csv(csv_path, index=False)

        summary = {
            "rows": int(len(df)),
            "books_with_local_loans": int((df["local_loan_count"] > 0).sum()) if not df.empty else 0,
            "total_local_loans": int(df["local_loan_count"].sum()) if not df.empty else 0,
            "avg_global_popularity": float(df["global_popularity_score"].mean()) if not df.empty else 0,
            "avg_demand_score": float(df["demand_score"].mean()) if not df.empty else 0,
            "output_csv": str(csv_path),
        }

        summary_path = ANALYTICS_DIR / "hybrid_ai_dataset_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"Dataset IA hybride généré : {csv_path}")
        print(f"Résumé généré : {summary_path}")
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build_dataset()