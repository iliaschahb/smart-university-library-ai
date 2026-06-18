import json
from pathlib import Path

import numpy as np
import pandas as pd

from app import app
from database import db
from models_kaggle_catalog import BooksCatalog, BookAnalytics, Inventory


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw" / "goodbooks-10k"


REQUIRED = ["books.csv", "tags.csv", "book_tags.csv", "to_read.csv"]


def check_files():
    missing = [str(RAW_DIR / name) for name in REQUIRED if not (RAW_DIR / name).exists()]
    if missing:
        raise FileNotFoundError("Fichiers Kaggle manquants :\n" + "\n".join(missing))


def read_csv(file_name):
    return pd.read_csv(
        RAW_DIR / file_name,
        engine="python",
        quotechar='"',
        on_bad_lines="skip",
    )


def compute_catalog_dataframe():
    books = read_csv("books.csv")
    tags = read_csv("tags.csv")
    book_tags = read_csv("book_tags.csv")
    to_read = read_csv("to_read.csv")

    # Normalisation minimale
    books = books.rename(columns={"book_id": "goodreads_book_id_from_books"})
    books["book_id"] = books["id"].astype(int)
    books["goodreads_book_id"] = pd.to_numeric(books["goodreads_book_id_from_books"], errors="coerce")
    books["publication_year"] = pd.to_numeric(books["original_publication_year"], errors="coerce").fillna(0).astype(int)
    books["average_rating"] = pd.to_numeric(books["average_rating"], errors="coerce").fillna(0)
    books["ratings_count"] = pd.to_numeric(books["ratings_count"], errors="coerce").fillna(0).astype(int)
    books["work_ratings_count"] = pd.to_numeric(books["work_ratings_count"], errors="coerce").fillna(0).astype(int)
    books["work_text_reviews_count"] = pd.to_numeric(books["work_text_reviews_count"], errors="coerce").fillna(0).astype(int)

    to_read_count = to_read.groupby("book_id").size().reset_index(name="to_read_count")
    books = books.merge(to_read_count, on="book_id", how="left")
    books["to_read_count"] = books["to_read_count"].fillna(0).astype(int)

    # Tags principaux
    tags["tag_id"] = pd.to_numeric(tags["tag_id"], errors="coerce")
    book_tags["goodreads_book_id"] = pd.to_numeric(book_tags["goodreads_book_id"], errors="coerce")
    book_tags["tag_id"] = pd.to_numeric(book_tags["tag_id"], errors="coerce")
    book_tags["count"] = pd.to_numeric(book_tags["count"], errors="coerce").fillna(0)
    merged_tags = book_tags.merge(tags, on="tag_id", how="left")
    merged_tags = merged_tags.sort_values(["goodreads_book_id", "count"], ascending=[True, False])
    top_tags = (
        merged_tags.groupby("goodreads_book_id")
        .head(8)
        .groupby("goodreads_book_id")
        .apply(lambda df: [str(x) for x in df["tag_name"].dropna().tolist()])
        .to_dict()
    )
    tag_count = merged_tags.groupby("goodreads_book_id").size().to_dict()

    # Popularité globale depuis Kaggle
    books["global_popularity_score"] = (
        (books["average_rating"] * 100)
        + (np.log1p(books["ratings_count"]) * 1200)
        + (np.log1p(books["work_ratings_count"]) * 800)
        + (np.log1p(books["to_read_count"]) * 500)
    )

    q1 = books["global_popularity_score"].quantile(0.80)
    q2 = books["global_popularity_score"].quantile(0.97)

    def level(score):
        if score >= q2:
            return "élevée"
        if score >= q1:
            return "moyenne"
        return "faible"

    books["global_popularity_level"] = books["global_popularity_score"].apply(level)
    books["top_tags_json"] = books["goodreads_book_id"].apply(lambda x: json.dumps(top_tags.get(x, []), ensure_ascii=False))
    books["tag_count"] = books["goodreads_book_id"].apply(lambda x: int(tag_count.get(x, 0)))

    keep = [
        "book_id", "goodreads_book_id", "best_book_id", "work_id", "isbn", "isbn13",
        "title", "authors", "publication_year", "language_code", "average_rating",
        "ratings_count", "work_ratings_count", "work_text_reviews_count", "image_url",
        "small_image_url", "to_read_count", "global_popularity_score", "global_popularity_level",
        "top_tags_json", "tag_count",
    ]
    return books[keep].copy()


def sync_catalog():
    check_files()
    df = compute_catalog_dataframe()

    with app.app_context():
        db.create_all()

        synced = 0
        for row in df.to_dict(orient="records"):
            book = db.session.get(BooksCatalog, int(row["book_id"]))
            if not book:
                book = BooksCatalog(book_id=int(row["book_id"]))
                db.session.add(book)

            book.goodreads_book_id = None if pd.isna(row["goodreads_book_id"]) else int(row["goodreads_book_id"])
            book.best_book_id = None if pd.isna(row["best_book_id"]) else int(row["best_book_id"])
            book.work_id = None if pd.isna(row["work_id"]) else int(row["work_id"])
            book.isbn = None if pd.isna(row["isbn"]) else str(row["isbn"])
            book.isbn13 = None if pd.isna(row["isbn13"]) else str(row["isbn13"])
            book.title = str(row["title"] or "Sans titre")
            book.authors = str(row["authors"] or "Inconnu")
            book.publication_year = int(row["publication_year"] or 0)
            book.language_code = None if pd.isna(row["language_code"]) else str(row["language_code"])
            book.average_rating = float(row["average_rating"] or 0)
            book.ratings_count = int(row["ratings_count"] or 0)
            book.work_ratings_count = int(row["work_ratings_count"] or 0)
            book.work_text_reviews_count = int(row["work_text_reviews_count"] or 0)
            book.image_url = None if pd.isna(row["image_url"]) else str(row["image_url"])
            book.small_image_url = None if pd.isna(row["small_image_url"]) else str(row["small_image_url"])
            book.data_source = "kaggle_goodbooks"
            book.is_active = True

            analytics = book.analytics or BookAnalytics(book_id=book.book_id)
            analytics.top_tags_json = str(row["top_tags_json"] or "[]")
            analytics.global_popularity_score = float(row["global_popularity_score"] or 0)
            analytics.global_popularity_level = str(row["global_popularity_level"] or "faible")
            analytics.avg_user_rating = float(row["average_rating"] or 0)
            analytics.to_read_count = int(row["to_read_count"] or 0)
            analytics.tag_count = int(row["tag_count"] or 0)
            if not book.analytics:
                db.session.add(analytics)

            inventory = book.inventory or Inventory(book_id=book.book_id)
            if inventory.id is None:
                inventory.quantity = inventory.quantity or 0
                inventory.available_quantity = inventory.available_quantity or 0
                inventory.shelf_location = inventory.shelf_location or None
                db.session.add(inventory)

            synced += 1

        db.session.commit()
        print(f"Catalogue Kaggle synchronisé : {synced} livres")


if __name__ == "__main__":
    sync_catalog()
