import csv
import json
from functools import lru_cache
from pathlib import Path

from flask import Blueprint, jsonify


recommendation_bp = Blueprint("recommendation_bp", __name__)


def project_root():
    return Path(__file__).resolve().parents[2]


def analytics_dir():
    return project_root() / "data" / "analytics"


def raw_dir():
    return project_root() / "data" / "raw" / "goodbooks-10k"


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default


@lru_cache(maxsize=1)
def load_catalog():
    path = analytics_dir() / "recommendation_catalog.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Catalogue de recommandation introuvable : {path}. "
            "Exécute : python backend/bigdata/spark_export_recommendations.py"
        )
    with open(path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    clean_catalog = []
    skipped = 0
    for item in catalog:
        book_id = safe_int(item.get("book_id"), None)
        if book_id is None:
            skipped += 1
            continue

        item["book_id"] = book_id
        item["popularity_score"] = safe_float(item.get("popularity_score"))
        item["avg_user_rating"] = safe_float(item.get("avg_user_rating"))
        item["goodreads_average_rating"] = safe_float(item.get("goodreads_average_rating"))
        item["rating_count"] = safe_int(item.get("rating_count"))
        item["to_read_count"] = safe_int(item.get("to_read_count"))
        item["tag_count"] = safe_int(item.get("tag_count"))
        item["title"] = str(item.get("title") or "Sans titre")
        item["authors"] = str(item.get("authors") or "Inconnu")
        item["tag_names"] = [tag.get("tag_name") for tag in item.get("tags", []) if isinstance(tag, dict) and tag.get("tag_name")]
        clean_catalog.append(item)

    if skipped:
        print(f"Catalogue recommandations : {skipped} lignes ignorées.")

    return clean_catalog


@lru_cache(maxsize=1)
def catalog_by_id():
    return {item["book_id"]: item for item in load_catalog()}


@lru_cache(maxsize=1)
def max_popularity_score():
    catalog = load_catalog()
    return max([item.get("popularity_score", 0) for item in catalog] or [1]) or 1


def public_book(item, score=None, algorithm=None, reason=None):
    data = {
        "book_id": item.get("book_id"),
        "title": item.get("title"),
        "authors": item.get("authors"),
        "avg_user_rating": item.get("avg_user_rating"),
        "goodreads_average_rating": item.get("goodreads_average_rating"),
        "rating_count": item.get("rating_count"),
        "to_read_count": item.get("to_read_count"),
        "popularity_score": item.get("popularity_score"),
        "popularity_level": item.get("popularity_level"),
        "tags": item.get("tag_names", [])[:8],
    }
    if score is not None:
        data["recommendation_score"] = round(float(score), 4)
    if algorithm:
        data["algorithm"] = algorithm
    if reason:
        data["reason"] = reason
    return data


def get_user_ratings(user_id):
    path = raw_dir() / "ratings.csv"
    if not path.exists():
        raise FileNotFoundError(f"ratings.csv introuvable : {path}")

    rated = []
    liked = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if str(row.get("user_id")) == str(user_id):
                book_id = safe_int(row.get("book_id"), None)
                rating = safe_int(row.get("rating"), None)
                if book_id is None or rating is None:
                    continue
                rated.append(book_id)
                if rating >= 4:
                    liked.append(book_id)
    return rated, liked


def tag_overlap_score(candidate_tags, preferred_tags):
    if not preferred_tags:
        return 0.0
    candidate_set = set(candidate_tags)
    preferred_set = set(preferred_tags)
    if not candidate_set:
        return 0.0
    return len(candidate_set.intersection(preferred_set)) / max(len(preferred_set), 1)


def hybrid_score(item, preferred_tags=None):
    preferred_tags = preferred_tags or []
    popularity_norm = float(item.get("popularity_score") or 0) / max_popularity_score()
    rating_norm = float(item.get("avg_user_rating") or item.get("goodreads_average_rating") or 0) / 5
    tags_norm = tag_overlap_score(item.get("tag_names", []), preferred_tags)
    return (0.50 * tags_norm) + (0.35 * popularity_norm) + (0.15 * rating_norm)


@recommendation_bp.route("/recommendations/popular", methods=["GET"])
def popular_recommendations():
    catalog = load_catalog()
    books = sorted(catalog, key=lambda x: (x.get("popularity_score", 0), x.get("avg_user_rating", 0)), reverse=True)[:10]
    return jsonify({
        "algorithm": "popularity_based_bigdata",
        "recommendations": [public_book(book, score=hybrid_score(book), algorithm="popularity_based_bigdata", reason="Livre fortement populaire selon le score Big Data") for book in books]
    }), 200


@recommendation_bp.route("/recommendations/similar/<int:book_id>", methods=["GET"])
def similar_books(book_id):
    source = catalog_by_id().get(book_id)
    if not source:
        return jsonify({"error": f"Livre introuvable : {book_id}"}), 404

    source_tags = source.get("tag_names", [])
    candidates = []
    for item in load_catalog():
        if item["book_id"] == book_id:
            continue
        overlap = tag_overlap_score(item.get("tag_names", []), source_tags)
        if overlap > 0:
            candidates.append((hybrid_score(item, source_tags), overlap, item))

    candidates = sorted(candidates, key=lambda x: (x[0], x[1]), reverse=True)[:10]
    return jsonify({
        "source_book": public_book(source),
        "algorithm": "similarity_by_tags_and_popularity",
        "recommendations": [public_book(item, score=score, algorithm="similarity_by_tags_and_popularity", reason=f"Tags communs avec le livre source : {round(overlap * 100, 1)}%") for score, overlap, item in candidates]
    }), 200


@recommendation_bp.route("/recommendations/user/<int:user_id>", methods=["GET"])
def user_recommendations(user_id):
    rated_ids, liked_ids = get_user_ratings(user_id)
    catalog_map = catalog_by_id()

    preferred_tags = []
    for book_id in liked_ids:
        book = catalog_map.get(book_id)
        if book:
            preferred_tags.extend(book.get("tag_names", []))

    if not preferred_tags:
        popular = sorted(load_catalog(), key=lambda x: x.get("popularity_score", 0), reverse=True)[:10]
        return jsonify({
            "user_id": user_id,
            "algorithm": "cold_start_popularity",
            "rated_books_count": len(rated_ids),
            "liked_books_count": len(liked_ids),
            "recommendations": [public_book(book, score=hybrid_score(book), algorithm="cold_start_popularity", reason="Aucun historique suffisant, recommandation basée sur la popularité") for book in popular]
        }), 200

    rated_set = set(rated_ids)
    candidates = []
    for item in load_catalog():
        if item["book_id"] in rated_set:
            continue
        score = hybrid_score(item, preferred_tags)
        if score > 0:
            candidates.append((score, item))

    candidates = sorted(candidates, key=lambda x: x[0], reverse=True)[:10]
    return jsonify({
        "user_id": user_id,
        "algorithm": "hybrid_user_tags_popularity",
        "rated_books_count": len(rated_ids),
        "liked_books_count": len(liked_ids),
        "preferred_tags_sample": list(dict.fromkeys(preferred_tags))[:15],
        "recommendations": [public_book(item, score=score, algorithm="hybrid_user_tags_popularity", reason="Tags préférés utilisateur + score de popularité Big Data") for score, item in candidates]
    }), 200


@recommendation_bp.route("/recommendations/hybrid/<int:user_id>", methods=["GET"])
def hybrid_recommendations(user_id):
    return user_recommendations(user_id)


@recommendation_bp.route("/recommendations/health", methods=["GET"])
def recommendation_health():
    catalog_path = analytics_dir() / "recommendation_catalog.json"
    return jsonify({
        "catalog_exists": catalog_path.exists(),
        "catalog_path": str(catalog_path),
        "catalog_size": len(load_catalog()) if catalog_path.exists() else 0,
        "routes": [
            "/recommendations/popular",
            "/recommendations/similar/<book_id>",
            "/recommendations/user/<user_id>",
            "/recommendations/hybrid/<user_id>",
        ]
    }), 200


@recommendation_bp.route("/recommendations/cache/clear", methods=["POST"])
def clear_recommendation_cache():
    load_catalog.cache_clear()
    catalog_by_id.cache_clear()
    max_popularity_score.cache_clear()
    return jsonify({"message": "Cache recommandations vidé"}), 200
